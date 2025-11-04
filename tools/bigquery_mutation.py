import logging
from typing import Any, Dict, Generator, Tuple

from dify_plugin import Tool
from dify_plugin.config.logger_format import plugin_logger_handler
from dify_plugin.entities.tool import ToolInvokeMessage
from google.cloud import bigquery
from google.oauth2 import service_account
from sqlglot import exp, parse_one

from provider import bigquery as bigquery_provider
from tools.api import SQLType, typeOf

logger = logging.getLogger(__name__)
logger.addHandler(plugin_logger_handler)


class BigqueryMutationTool(Tool):

    def __init__(self, runtime, session):
        super().__init__(runtime, session)
        try:
            credentials = self.runtime.credentials or runtime.credentials
            self.bigquery_config = bigquery_provider.get_config(credentials)
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery config: {str(e)}")

    def _get_client(self):
        """
        Create and return a BigQuery client.
        Plugin has short lifecycle, so we create a new client for each request.
        """
        creds = service_account.Credentials.from_service_account_info(
            self.bigquery_config["service_account_info"]
        )
        client = bigquery.Client(
            credentials=creds,
            project=self.bigquery_config["project_id"]
        )
        logger.info(f"Initialized BigQuery client for project: {self.bigquery_config['project_id']}")
        return client

    def _check_query(self, query: str) -> Tuple[SQLType, str]:
        """
        1. Perform SQL syntax analysis to find parameter variables
        2. Based on syntax analysis AST, determine the DML type of the SQL
        """
        if not query:
            raise ValueError("SQL query is required")

        try:
            ast = parse_one(query, dialect="bigquery")
        except BaseException as ex:
            raise ValueError(f"SQL syntax error, query={query}. caused by={ex}")

        # Check for placeholders and parameters
        for p in ast.find_all(exp.Placeholder):
            raise ValueError("Not allowed Placeholder -> `?`, Should use named parameters if needed")
        for p in ast.find_all(exp.Parameter):
            raise ValueError("Parameters are not allowed in BigQuery Mutation tool")

        return typeOf(ast), ast.sql(dialect="bigquery")

    def _invoke(
        self, tool_parameters: Dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        query: str = tool_parameters.get("query")

        sql_type, sql_exp = self._check_query(query)

        # Only allow INSERT, UPDATE, DELETE operations
        if sql_type not in [SQLType.INSERT, SQLType.UPDATE, SQLType.DELETE]:
            raise ValueError("Only INSERT, UPDATE, DELETE operations are allowed in BigQuery Mutation tool. Use BigQuery Query tool for SELECT operations.")

        client = None
        try:
            client = self._get_client()

            # Configure the query job
            job_config = bigquery.QueryJobConfig(
                maximum_bytes_billed=10**10  # 10GB limit to prevent runaway costs
            )

            # Execute the mutation query
            query_job = client.query(sql_exp, job_config=job_config)

            # Wait for the query to complete
            results = query_job.result()

            # Get the number of affected rows
            affected_rows = query_job.num_dml_affected_rows if query_job.num_dml_affected_rows is not None else 0

            logger.info(f"SQL-mutation type={sql_type.name}, exp={sql_exp}, affected_rows={affected_rows}")

            # Yield the affected rows count as a variable
            yield self.create_variable_message("affected_rows", affected_rows)

            # Yield JSON message with results
            yield self.create_json_message({
                "affected_rows": affected_rows,
                "success": True
            })

        except Exception as ex:
            logger.exception(f"SQL={sql_exp}, caused by={type(ex)}: {ex}")
            raise RuntimeError(f"{type(ex).__name__}: {ex}") from ex

        finally:
            if client:
                client.close()

