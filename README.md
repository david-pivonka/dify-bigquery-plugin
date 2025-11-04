# BigQuery Plugin for Dify

**Author:** david-pivonka
**Version:** 0.0.1
**Type:** Tool Plugin

## Description

The BigQuery plugin enables Dify applications to query and modify data in Google BigQuery directly. It provides secure, authenticated connections to BigQuery using Google Cloud service account credentials with separate tools for read and write operations.

## Features

- ✅ **Secure Authentication**: Uses Google Cloud service account JSON for authentication
- ✅ **Dual Tools**: Separate tools for queries (SELECT) and mutations (INSERT/UPDATE/DELETE)
- ✅ **Per-Query Row Limits**: Control result size with configurable row limits at the query level
- ✅ **SQL Validation**: Automatic validation of SQL syntax before execution
- ✅ **Cost Protection**: Built-in query cost limits to prevent runaway billing
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Standardized Output**: Returns data in a consistent format

## Installation

### Prerequisites

- A Google Cloud Platform account with BigQuery enabled
- A service account with appropriate BigQuery permissions
- Dify platform access

### Required Permissions

Your Google Cloud service account must have at least these IAM roles:

- `roles/bigquery.user` - To run queries
- `roles/bigquery.dataViewer` - To read table data

Or specific dataset/table level permissions as needed.

### Installing the Plugin

1. Download the `dify-bigquery-plugin.difypkg` file
2. In Dify, navigate to Plugins → Install Plugin
3. Upload the `.difypkg` file
4. Configure the plugin credentials (see Configuration section)

The plugin provides two tools:
- **BigQuery Query**: For SELECT operations (read-only)
- **BigQuery Mutation**: For INSERT, UPDATE, DELETE operations (write operations)

## Configuration

The plugin requires the following credentials:

### service_account_json (Required)

The complete JSON content of your Google Cloud service account key file. This includes:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "...",
  "universe_domain": "googleapis.com"
}
```

**How to obtain:**
1. Go to Google Cloud Console
2. Navigate to IAM & Admin → Service Accounts
3. Create or select a service account
4. Create a new key → JSON format
5. Copy the entire JSON content

### project_id (Optional)

Override the project ID from the service account JSON if you want to query a different project.

## Usage

The plugin provides two separate tools that can be used in Dify workflows:

### Tool 1: BigQuery Query (Read Operations)

Use this tool to execute SELECT queries and retrieve data from BigQuery.

**In Dify Workflows:**
1. Add the "BigQuery Query" tool to your workflow
2. Configure the query parameter with your SELECT statement
3. Optionally set max_fetched_rows to limit result size
4. Connect the output to subsequent nodes

**Parameters:**
- **query** (string, required): The SELECT query to execute
- **max_fetched_rows** (number, optional): Maximum rows to return (default: 100)

**Important:** Only SELECT queries are allowed in this tool. Use the Mutation tool for data modifications.

**Output:**
- `data`: Array of row data
- `columns`: Array of column names
- JSON message with formatted results

### Tool 2: BigQuery Mutation (Write Operations)

Use this tool to execute INSERT, UPDATE, or DELETE queries to modify data in BigQuery.

**In Dify Workflows:**
1. Add the "BigQuery Mutation" tool to your workflow
2. Configure the query parameter with your INSERT/UPDATE/DELETE statement
3. Connect the output to subsequent nodes

**Parameters:**
- **query** (string, required): The INSERT, UPDATE, or DELETE query to execute

**Important:** Only INSERT, UPDATE, DELETE queries are allowed in this tool. Use the Query tool for SELECT operations.

**Output:**
- `affected_rows`: Number of rows modified
- `success`: Boolean indicating successful execution
- JSON message with mutation results

### Example Queries

#### Query Tool Examples (SELECT)

**Simple SELECT:**
```sql
SELECT 1 as test_value, 'Hello BigQuery' as message
```

**Query a Table:**
```sql
SELECT
  customer_id,
  order_date,
  total_amount
FROM `project.dataset.orders`
WHERE order_date >= '2024-01-01'
LIMIT 100
```
*Note: Use max_fetched_rows parameter to limit results returned to Dify*

**Aggregation Query:**
```sql
SELECT
  product_category,
  COUNT(*) as order_count,
  SUM(total_amount) as total_revenue
FROM `project.dataset.orders`
GROUP BY product_category
ORDER BY total_revenue DESC
```

#### Mutation Tool Examples (INSERT/UPDATE/DELETE)

**INSERT Data:**
```sql
INSERT INTO `project.dataset.customers` (customer_id, name, email, created_at)
VALUES (12345, 'John Doe', 'john@example.com', CURRENT_TIMESTAMP())
```

**UPDATE Data:**
```sql
UPDATE `project.dataset.orders`
SET status = 'shipped', shipped_at = CURRENT_TIMESTAMP()
WHERE order_id = 98765 AND status = 'pending'
```

**DELETE Data:**
```sql
DELETE FROM `project.dataset.temp_data`
WHERE created_at < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
```

### Output Formats

**Query Tool Output:**

1. **Variables**:
   - `data`: Array of row tuples
   - `columns`: Array of column names

2. **JSON Message**:
```json
{
  "data": [
    {
      "column1": "value1",
      "column2": "value2"
    },
    {
      "column1": "value3",
      "column2": "value4"
    }
  ]
}
```

**Mutation Tool Output:**

1. **Variables**:
   - `affected_rows`: Number of rows modified (integer)

2. **JSON Message**:
```json
{
  "affected_rows": 5,
  "success": true
}
```

## Security Features

### Tool Separation

- **Query Tool**: Restricted to SELECT operations only - rejects all modification queries
- **Mutation Tool**: Restricted to INSERT/UPDATE/DELETE operations only - rejects SELECT queries
- This separation ensures intentional data modifications and prevents accidental writes

### Query Restrictions

- **No Parameters**: Query parameters are not allowed to prevent injection attacks
- **SQL Validation**: All queries are parsed and validated before execution
- **Type Checking**: SQL AST analysis ensures query types match tool capabilities

### Cost Protection

- **Query Cost Limit**: Maximum 10GB of data scanned per query
- **Per-Query Row Limits**: Control result size for each individual query (Query tool only)
- **Timeout Protection**: Queries have timeout limits to prevent long-running operations

## Development

### Building from Source

```bash
# Clone the repository
git clone https://github.com/david-pivonka/dify-bigquery-plugin.git
cd dify-bigquery-plugin

# Install dependencies
pip install -r requirements.txt

# Package the plugin
dify plugin package .
```

### Testing

See [TESTING.md](TESTING.md) for detailed testing instructions.

```bash
# Run the plugin for testing
dify plugin run ./dify-bigquery-plugin.difypkg --enable-logs
```

## Troubleshooting

### Common Issues

**Error: "Invalid JSON in service_account_json"**
- Ensure you're pasting the complete, valid JSON from your service account key file
- Check for any truncated or modified content

**Error: "Missing required fields in service account JSON"**
- Verify your service account JSON contains all required fields: type, project_id, private_key_id, private_key, client_email

**Error: "Only SELECT operations are allowed" (from Query tool)**
- You're using the Query tool with a mutation query
- Use the BigQuery Mutation tool for INSERT, UPDATE, DELETE operations

**Error: "Only INSERT, UPDATE, DELETE operations are allowed" (from Mutation tool)**
- You're using the Mutation tool with a SELECT query
- Use the BigQuery Query tool for SELECT operations

**Query timeout or exceeded quota**
- Reduce query complexity
- Ensure your GCP project has sufficient BigQuery quota
- Check service account permissions

## Architecture

The plugin is structured following Dify's plugin architecture:

```
dify-bigquery-plugin/
├── manifest.yaml               # Plugin metadata
├── main.py                     # Plugin entry point
├── provider/
│   ├── bigquery.yaml           # Provider configuration
│   └── bigquery.py             # Credential validation
├── tools/
│   ├── bigquery_query.yaml     # Query tool definition
│   ├── bigquery_query.py       # Query tool implementation
│   ├── bigquery_mutation.yaml  # Mutation tool definition
│   ├── bigquery_mutation.py    # Mutation tool implementation
│   └── api.py                  # SQL type checking utilities
└── requirements.txt            # Python dependencies
```

### Key Components

- **Provider**: Handles credential validation and configuration for both tools
- **Query Tool**: Implements SELECT query execution with row limiting
- **Mutation Tool**: Implements INSERT/UPDATE/DELETE operations with affected row tracking
- **SQL Validation**: Uses sqlglot for SQL parsing and type checking (shared by both tools)

## Dependencies

- `dify_plugin>=0.4.0,<0.7.0` - Dify plugin SDK
- `google-cloud-bigquery>=3.0.0` - Google BigQuery client
- `sqlglot>=26.11.1` - SQL parser and transpiler
- `sqlglotrs>=0.4.0` - Fast SQL parser

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please visit:
- GitHub: https://github.com/david-pivonka/dify-bigquery-plugin

## Privacy

See [PRIVACY.md](PRIVACY.md) for information about data handling and privacy practices.

