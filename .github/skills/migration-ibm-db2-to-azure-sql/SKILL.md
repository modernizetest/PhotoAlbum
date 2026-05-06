---
name: migration-ibm-db2-to-azure-sql
description: Migrate IBM Db2 to Azure SQL Database
---

# Migrate from IBM Db2 to Azure SQL Database

Your task is to migrate a project from using IBM Db2 to using Azure SQL Database.

## Requirements

- Don't modify any content that is not related to IBM Db2 to Azure SQL Database migration.
- Enable passwordless connection. Use managed identity by default.
    - **For a Spring Boot project:**
        - Update dependency:
            - Use spring-cloud-azure-dependencies (bom) to manage the Spring Cloud Azure dependency version. Choose a version of spring-cloud-azure-dependencies that is compatible with your Spring Boot version:
                - For projects using spring-boot:2.x, spring-cloud-azure-dependencies' version should >= `4.20.0` and < `5.0.0`.
                - For projects using spring-boot:3.x, spring-cloud-azure-dependencies' version should >= `5.22.0` and < `7.0.0`.
                - For projects using spring-boot:4.x, spring-cloud-azure-dependencies' version should >= `7.1.0`.
            - Add dependency: com.azure.spring:spring-cloud-azure-starter
        - Update properties:
            - Add the configuration for Azure managed identity:
                ```properties
                spring.cloud.azure.credential.managed-identity-enabled=true
                spring.cloud.azure.credential.client-id=${AZURE_MANAGED_IDENTITY_CLIENT_ID}
                ```
            - Update the spring.datasource.url property for Azure Active Directory Managed Identity authentication:
                - If the spring.datasource.url property is missing, add it using the JDBC URL format shown in the example below.
                - If the spring.datasource.url value does not already contain "authentication=ActiveDirectoryMSI", append ";authentication=ActiveDirectoryMSI" to the end of it.
                - Example:
                    ```properties
                    spring.datasource.url=jdbc:sqlserver://${DATABASE_SERVER_HOST_NAME}:1433;database=${DATABASE_NAME};encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net;loginTimeout=30;authentication=ActiveDirectoryMSI
                    ```
            - Remove the configuration for username and password of the **SQL** database:
                - Remove username and password segments from JDBC connection strings (typically after the ; symbol).
                - Remove username and password properties from the configuration file, e.g., spring.datasource.username, spring.datasource.password.
                - Note: Do not remove username and password properties if they are used for other purposes.
    - **For other Java projects:**
        - Update Java code:
            - Remove username and password usage: Eliminate the hardcoded username and password in the connection string.
            - Add a variable for the Azure client ID of managed identity.
            - Append msiClientId to the connection string URL: ";msiClientId=" + ${AZURE_MANAGED_IDENTITY_CLIENT_ID}
            - Append this exact string of authentication to the connection string URL: ";authentication=ActiveDirectoryMSI"
            - Use the updated connection string URL for SQLServerDataSource when setting the URL.
            - API reference — `com.microsoft.sqlserver.jdbc.SQLServerDataSource`:
                - `setUrl(String url)`: Sets the connection URL.
                - `getURL()`: Returns the connection URL.
                - `getConnection()`: Establishes a connection to the data source.
        - Update properties:
            - Add the configuration for the Azure client ID for managed identity. Common naming conventions include AZURE_CLIENT_ID, azure.client.id, azure.identity.client-id. Apply a naming convention consistent with the style of the context.
            - Remove the configuration for username and password of the **SQL** database:
                - Remove username and password segments from JDBC connection strings (typically after the ; symbol).
                - Remove username and password properties from the configuration file.
                - Note: Do not remove username and password properties if they are used for other purposes.
- Migrate all Db2-related content to Azure SQL Database equivalents.
    - Check all files that may require updates, for example Java files, XML files, SQL files, configuration files, and project build files (such as `pom.xml` and `build.gradle`).
    - Error-prone items:
        - Review SQL in annotations and code (for example `@NamedQuery`, `@NamedNativeQuery`, `@Query`, and SQL strings); migrate Db2-specific syntax/semantics.
        - Migrate Db2-only patterns (`QUARTER(`, `DATE(`, `||`, `FETCH FIRST`, `BEGIN ATOMIC ... END`) to Azure SQL equivalents (for example T-SQL `BEGIN ... END`).
        - `PERCENTILE_CONT`: rewrite to `PERCENTILE_CONT(p) WITHIN GROUP (ORDER BY x) OVER (...)`.
            - Use `OVER ()` for global percentile and `OVER (PARTITION BY <group_key>)` for per-group percentile.
            - Preserve original output grain and row cardinality (for example, if Db2 `GROUP BY` returns one row per group, Azure SQL must also return one row per group).
            - Use a subquery/CTE to compute and deduplicate before joining back only when needed to preserve original grain/cardinality; avoid mechanical inline replacement.
    - Verify each change is functionally equivalent and compatible with Azure SQL Database.
