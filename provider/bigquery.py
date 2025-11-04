import json
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


def get_config(credentials: dict[str, Any]) -> dict[str, Any]:
    """
    Parse and validate BigQuery credentials.

    Returns:
        dict containing service account info and project_id
    """
    # Get the service account JSON string
    service_account_json_str = credentials.get("service_account_json")
    if not service_account_json_str:
        raise ValueError("service_account_json is required")

    # Parse the JSON
    try:
        service_account_info = json.loads(service_account_json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in service_account_json: {str(e)}")

    # Validate required fields in the service account JSON
    required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
    missing_fields = [field for field in required_fields if field not in service_account_info]
    if missing_fields:
        raise ValueError(
            f"Missing required fields in service account JSON: {', '.join(missing_fields)}"
        )

    # Verify it's a service account
    if service_account_info.get("type") != "service_account":
        raise ValueError("The JSON must be a service_account type")

    # Get project_id (allow override from credentials)
    project_id = credentials.get("project_id") or service_account_info.get("project_id")
    if not project_id:
        raise ValueError("project_id is required either in credentials or service account JSON")

    bigquery_config = {
        "service_account_info": service_account_info,
        "project_id": project_id,
    }

    return bigquery_config


class BigqueryProvider(ToolProvider):

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate BigQuery credentials by parsing the service account JSON
        and attempting to create a BigQuery client.
        """
        try:
            from google.cloud import bigquery
            from google.oauth2 import service_account

            # Parse and validate credentials
            bigquery_config = get_config(credentials)

            # Create credentials object from service account info
            creds = service_account.Credentials.from_service_account_info(
                bigquery_config["service_account_info"]
            )

            # Create BigQuery client to test connection
            client = bigquery.Client(
                credentials=creds,
                project=bigquery_config["project_id"]
            )

            # Test the connection with a simple query
            query = "SELECT 1 as test"
            query_job = client.query(query)
            results = query_job.result()

            # If we get here, the credentials are valid

        except ImportError as e:
            raise ToolProviderCredentialValidationError(
                "google-cloud-bigquery library is not installed. "
                "Please install it with: pip install google-cloud-bigquery"
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
