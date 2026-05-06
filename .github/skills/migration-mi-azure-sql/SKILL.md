---
name: migration-mi-azure-sql
description: Migrates Java Spring Boot projects from password-based authentication to Azure Managed Identity for connecting to Azure SQL Database. Updates Spring Cloud Azure dependencies and datasource configuration for passwordless authentication. Use when enabling managed identity for Azure SQL Database connections, removing hardcoded database passwords, or securing Java Spring Boot database authentication.
---

Your task is to migrate a Java project from password-based authentication to Azure Managed Identity for connecting to Azure SQL Database.

## For a Spring Boot project

### Update dependency

- Use spring-cloud-azure-dependencies (bom) to manage the Spring Cloud Azure dependency version. Choose a version of spring-cloud-azure-dependencies that is compatible with your Spring Boot version:
    - For projects using spring-boot:2.x, spring-cloud-azure-dependencies' version should >= `4.20.0` and < `5.0.0`.
    - For projects using spring-boot:3.x, spring-cloud-azure-dependencies' version should >= `5.22.0` and < `7.0.0`.
    - For projects using spring-boot:4.x, spring-cloud-azure-dependencies' version should >= `7.1.0`.
- Add dependency: com.azure.spring:spring-cloud-azure-starter

### Update properties

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

## For other Java projects

### Update Java code

- Remove username and password usage: Eliminate the hardcoded username and password in the connection string.
- Add a variable for the Azure client ID of managed identity.
- Append msiClientId to the connection string URL: ";msiClientId=" + ${AZURE_MANAGED_IDENTITY_CLIENT_ID}
- Append this exact string of authentication to the connection string URL: ";authentication=ActiveDirectoryMSI"
- Use the updated connection string URL for SQLServerDataSource when setting the URL.
- API reference — `com.microsoft.sqlserver.jdbc.SQLServerDataSource`:
    - `setUrl(String url)`: Sets the connection URL.
    - `getURL()`: Returns the connection URL.
    - `getConnection()`: Establishes a connection to the data source.

### Update properties

- Add the configuration for the Azure client ID for managed identity. Common naming conventions include AZURE_CLIENT_ID, azure.client.id, azure.identity.client-id. Apply a naming convention consistent with the style of the context.
- Remove the configuration for username and password of the **SQL** database:
    - Remove username and password segments from JDBC connection strings (typically after the ; symbol).
    - Remove username and password properties from the configuration file.
    - Note: Do not remove username and password properties if they are used for other purposes.
