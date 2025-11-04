## Privacy Policy

### 1. Information Collection Statement

**This plugin does NOT collect or require any of the following:**
- Personal user information (including but not limited to names, emails, device identifiers)
- User behavior data (including but not limited to search history, click tracking, geolocation)
- Device information (including but not limited to IP addresses, OS versions)

**Data Interaction Disclosure:**
- Connects to Google BigQuery using user-provided service account credentials to execute SQL queries
- Processes query results and mutation confirmations as requested by the user
- No user-identifiable information is collected or transmitted beyond what is necessary for BigQuery API communication
- All authentication is handled through Google Cloud service account credentials provided by the user

---

### 2. Scope of Data Processing

**Core Functionality:**
- **Query Tool**: Executes SELECT queries against Google BigQuery and returns result data
- **Mutation Tool**: Executes INSERT, UPDATE, and DELETE operations against Google BigQuery and returns affected row counts
- Validates SQL syntax before execution
- Enforces query type restrictions (Query tool: SELECT only; Mutation tool: INSERT/UPDATE/DELETE only)
- Applies configurable row limits for SELECT queries to prevent excessive data retrieval

**Transparency Commitments:**
- Does not store, cache, or log query results locally or remotely
- Does not store, cache, or log SQL queries or user credentials
- Does not modify user data beyond explicitly requested SQL operations (Mutation tool)
- Does not transmit data to any third party other than Google Cloud BigQuery API
- Service account credentials remain encrypted in Dify's credential store

---

### 3. Data Credentials and Authentication

**User-Provided Credentials:**
- Requires Google Cloud service account JSON key file content
- Credentials are stored securely in Dify's encrypted credential storage
- Credentials are used exclusively to authenticate with Google BigQuery API
- Project ID can be optionally overridden by the user

**Credential Security:**
- Service account credentials are transmitted only to Google Cloud Platform
- No credentials are logged, stored locally, or transmitted to third parties
- Users maintain full control over service account permissions in Google Cloud Console

---

### 4. Third-Party Dependency Notice

**Google Cloud BigQuery:**
- This plugin relies on the Google Cloud BigQuery API (https://cloud.google.com/bigquery)
- Complies with Google Cloud Platform's terms of service and API usage policies
- Users are advised to review Google Cloud's privacy policy: https://cloud.google.com/terms/cloud-privacy-notice

**Data Attribution:**
- All data accessed through this plugin belongs to the user's Google Cloud project
- This plugin serves as a technical interface to BigQuery with no control over data content or accuracy
- Users are responsible for ensuring compliance with data protection regulations (GDPR, CCPA, etc.) for data stored in BigQuery

**Required Permissions:**
- Minimum required: `roles/bigquery.user` (to run queries)
- For read access: `roles/bigquery.dataViewer` (to read table data)
- Users should follow the principle of least privilege when configuring service account permissions

---

### 5. Data Security Measures

**Encrypted Transmission:**
- All communications with Google BigQuery API use HTTPS/TLS encryption
- Service account credentials are encrypted at rest in Dify's credential store
- No credentials or query data are transmitted over unencrypted channels

**Zero-Persistence Mechanism:**
- Query results are processed in-memory and returned immediately to Dify workflows
- No local caching, database storage, or logging of query results or BigQuery data
- Temporary data is automatically purged from memory after processing
- Plugin operates with short lifecycle - no long-running processes or persistent connections

**Query Cost Protection:**
- Maximum query billing limit set to 10GB per query to prevent runaway costs
- Configurable row limits (default: 100) for SELECT queries
- Users maintain control over query costs through Google Cloud billing controls

---

### 6. Data Processing Transparency

**What We Process:**
- SQL queries provided by users in Dify workflows
- Service account credentials for BigQuery authentication
- Query results from BigQuery (SELECT operations)
- Mutation confirmations from BigQuery (INSERT/UPDATE/DELETE operations)

**What We Do NOT Process:**
- User personal information beyond BigQuery service account credentials
- Data from sources other than Google BigQuery
- Query history or analytics
- User behavior tracking

**Data Flow:**
1. User configures plugin with Google Cloud service account credentials in Dify
2. User creates workflow with BigQuery Query or Mutation tool nodes
3. Workflow executes and sends SQL query to plugin
4. Plugin validates query and connects to BigQuery using provided credentials
5. Plugin executes query on BigQuery and receives results
6. Plugin returns results to Dify workflow and purges data from memory
7. No data is retained by the plugin after workflow completion

---

### 7. User Rights and Control

**Users Have Full Control Over:**
- Google Cloud service account credentials and permissions
- SQL queries executed against their BigQuery datasets
- Data access permissions in Google Cloud Console
- Query result limits and cost controls
- Choice to use Query tool (read-only) or Mutation tool (write operations)

**Users Can:**
- Revoke service account credentials at any time in Google Cloud Console
- Monitor all BigQuery query activity in Google Cloud Console
- Remove plugin from Dify instance at any time
- Modify service account permissions to restrict plugin access

---

### 8. Compliance and Best Practices

**Security Recommendations:**
- Use service accounts with minimum required permissions
- Regularly rotate service account keys
- Monitor BigQuery audit logs for unexpected activity
- Review and limit dataset/table access for service accounts
- Enable Google Cloud security features (VPC Service Controls, etc.)

**Data Protection:**
- This plugin does not implement data retention policies (zero retention)
- Users are responsible for their own data protection compliance
- Plugin supports secure enterprise deployments through Dify's security features

---

### 9. Contact and Updates

For questions or concerns about this privacy policy:
- GitHub Repository: https://github.com/david-pivonka/dify-bigquery-plugin
- Report security issues through GitHub Issues

**Policy Updates:**
- This privacy policy may be updated to reflect changes in plugin functionality
- Material changes will be documented in plugin release notes
- Users are encouraged to review this policy periodically

---

**Last Updated:** November 4, 2025
**Plugin Version:** 0.0.1
