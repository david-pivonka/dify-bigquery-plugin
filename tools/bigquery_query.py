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


class BigqueryQueryTool(Tool):

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
            raise ValueError("Parameters are not allowed in BigQuery Query tool")

        return typeOf(ast), ast.sql(dialect="bigquery")

    def _invoke(
        self, tool_parameters: Dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        query: str = tool_parameters.get("query")

        # Get max_fetched_rows from tool parameters (defaults to 100)
        max_fetched_rows = tool_parameters.get("max_fetched_rows", 100)
        if isinstance(max_fetched_rows, str):
            max_fetched_rows = int(max_fetched_rows) if max_fetched_rows.isdigit() else 100
        max_fetched_rows = int(max_fetched_rows)

        sql_type, sql_exp = self._check_query(query)

        # Only support SELECT operations
        if sql_type != SQLType.SELECT:
            raise ValueError("Only SELECT operations are allowed in BigQuery Query tool")

        client = None
        try:
            client = self._get_client()

            # Configure the query job to limit results
            job_config = bigquery.QueryJobConfig(
                maximum_bytes_billed=10**10  # 10GB limit to prevent runaway costs
            )

            # Execute the query
            query_job = client.query(sql_exp, job_config=job_config)

            # Fetch results with row limit from tool parameters
            results = query_job.result(max_results=max_fetched_rows)

            # Get column names from schema
            columns = [field.name for field in results.schema]

            # Convert rows to list of tuples
            rows = [tuple(row.values()) for row in results]

            logger.info(f"SQL-select exp={sql_exp}, count={len(rows)}, max_fetched_rows={max_fetched_rows}")

            # Yield the data and columns as variables
            yield self.create_variable_message("data", rows)
            yield self.create_variable_message("columns", columns)

            # Convert to list of dictionaries for JSON output
            data = [dict(zip(columns, row)) for row in rows]
            yield self.create_json_message({"data": data})

        except Exception as ex:
            logger.exception(f"SQL={sql_exp}, caused by={type(ex)}: {ex}")
            raise RuntimeError(f"{type(ex).__name__}: {ex}") from ex

        finally:
            if client:
                client.close()

