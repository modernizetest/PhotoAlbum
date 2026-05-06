---
name: migration-ibm-db2-to-azure-postgresql
description: Migrate IBM Db2 to Azure Database for PostgreSQL
---

# Migrate from IBM Db2 to Azure Database for PostgreSQL

Your task is to migrate a project from using IBM Db2 to using Azure Database for PostgreSQL.

## Requirements

- Don't modify any content that is not related to IBM Db2 to Azure Database for PostgreSQL migration.
- Enable passwordless connection. Use managed identity by default. Add comments to show how to authenticate by service principal.
    - **IMPORTANT - JDBC only**: The following steps only work for JDBC connections. If the project uses R2DBC (check for `r2dbc:` URLs or `r2dbc-postgresql` dependencies), ignore this entire requirement.
    - In Java code, comment out all "username" and "password" related content that ONLY corresponds to the PostgreSQL JDBC URL.
        ```diff
        - @Value("${spring.shardingsphere.dataSource1.username}")
        - private String username;
        - @Value("${spring.shardingsphere.dataSource1.password}")
        - private String password;
        + // Comment out all content about "username" and "password" because now PostgreSQL will authenticate using managed identity.
        + // @Value("${spring.shardingsphere.dataSource1.username}")
        + // private String username;
        + // @Value("${spring.shardingsphere.dataSource1.password}")
        + // private String password;
        ```
        ```diff
        - hikariDataSource.setUsername(dataSource1Config.getUsername());
        - hikariDataSource.setPassword(dataSource1Config.getPassword());
        + // Comment out all content about "username" and "password" because now PostgreSQL will authenticate using managed identity.
        + // hikariDataSource.setUsername(dataSource1Config.getUsername());
        + // hikariDataSource.setPassword(dataSource1Config.getPassword());
        ```
    - In build config file (like pom.xml), add this dependency:
        ```diff
        + <dependency>
        +     <groupId>com.azure</groupId>
        +     <artifactId>azure-identity-extensions</artifactId>
        +     <version>1.2.2</version>
        + </dependency>
        ```
    - In the property file, update the PostgreSQL JDBC URL to support authentication by managed identity. Follow these steps:
        - Add these parameters to the PostgreSQL JDBC URL:
            - user=${MANAGED_IDENTITY_NAME}
            - sslmode=require (IMPORTANT: Use "require" instead of other values like "verify-full")
            - authenticationPluginClassName=com.azure.identity.extensions.jdbc.postgresql.AzurePostgresqlAuthenticationPlugin
            - azure.managedIdentityEnabled=true
            - azure.clientId=${MANAGED_IDENTITY_CLIENT_ID}
        - Use environment variable for database host/port/database name if the original value is not Azure PostgreSQL.
        - Add comments about environment variables in the PostgreSQL JDBC URL.
        - Comment out all "username" and "password" related content that ONLY corresponds to the PostgreSQL JDBC URL.
        - Do not add default values for environment variables.
        - Example:
            ```diff
            - url:  jdbc:postgresql://localhost:5432/testdb
            - username: testuser
            - password: testpass
            + # Remember to set the value for the environment variables in the url value below
            + # For Azure sovereign cloud, add these parameters in the url:
            + #  azure.scopes
            + #     - azure_china: https://ossrdbms-aad.database.chinacloudapi.cn/.default
            + #     - azure_germany: https://ossrdbms-aad.database.cloudapi.de/.default
            + #     - azure_us_government: https://ossrdbms-aad.database.usgovcloudapi.net/.default
            + #     - azure: https://ossrdbms-aad.database.windows.net/.default
            + #  azure.authorityHost
            + #     - azure_china: https://login.partner.microsoftonline.cn
            + #     - azure_germany: https://login.microsoftonline.de
            + #     - azure_us_government: https://login.microsoftonline.us
            + #     - azure: https://login.microsoftonline.com
            + url: jdbc:postgresql://${PGHOST}:${PGPORT}/${PGDATABASE}?user=${MANAGED_IDENTITY_NAME}&sslmode=require&authenticationPluginClassName=com.azure.identity.extensions.jdbc.postgresql.AzurePostgresqlAuthenticationPlugin&azure.managedIdentityEnabled=true&azure.clientId=${MANAGED_IDENTITY_CLIENT_ID}
            + # Comment out all content about "username" and "password" because now PostgreSQL will authenticate using managed identity.
            + # username: testuser
            + # password: testpass
            ```
    - In the property file, add an example PostgreSQL JDBC URL to show how to authenticate by service principal.
        - These parameters are required:
            - user=${SERVICE_PRINCIPAL_NAME}
            - sslmode=require (IMPORTANT: Use "require" instead of other values like "verify-full")
            - authenticationPluginClassName=com.azure.identity.extensions.jdbc.postgresql.AzurePostgresqlAuthenticationPlugin
            - azure.clientId=${SERVICE_PRINCIPAL_CLIENT_ID}
            - azure.clientSecret=${SERVICE_PRINCIPAL_CLIENT_SECRET}
            - azure.tenantId=${SERVICE_PRINCIPAL_TENANT_ID}
        - Do not add default values for environment variables.
        - Example:
            ```diff
            + # Example URL for authentication by Service Principal instead of Managed Identity
            + # url: jdbc:postgresql://${PGHOST}:${PGPORT}/${PGDATABASE}?user=${SERVICE_PRINCIPAL_NAME}&sslmode=require&authenticationPluginClassName=com.azure.identity.extensions.jdbc.postgresql.AzurePostgresqlAuthenticationPlugin&azure.clientId=${SERVICE_PRINCIPAL_CLIENT_ID}&azure.clientSecret=${SERVICE_PRINCIPAL_CLIENT_SECRET}&azure.tenantId=${SERVICE_PRINCIPAL_TENANT_ID}
            ```
- Use lowercase for identifiers (like table and column names) and data types (like varchar). Use uppercase for SQL keywords (like `SELECT`, `FROM`, `WHERE`). This includes SQL statements and JPA annotations like `@Table`, `@Column`, `@NamedNativeQuery`, and `@Query`.
    - Example:
        ```diff
        - String sql = """
        -         INSERT INTO EMPLOYEES (
        -             EMPLOYEE_ID, FIRST_NAME, LAST_NAME, EMAIL,
        -             PHONE_NUMBER, HIRE_DATE, JOB_ID, SALARY,
        -             COMMISSION_PCT, MANAGER_ID, DEPARTMENT_ID
        -         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        -     """;
        + String sql = """
        +         INSERT INTO employees (
        +             employee_id, first_name, last_name, email,
        +             phone_number, hire_date, job_id, salary,
        +             commission_pct, manager_id, department_id
        +         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        +     """;
        ```
        ```diff
        - @Entity
        - @Table(name = "ITEMS")
        - public class Item {
        -     @Id
        -     @Column(name = "ITEM_ID")
        -     private Long id;
        - }
        + @Entity
        + @Table(name = "items")
        + public class Item {
        +     @Id
        +     @Column(name = "item_id")
        +     private Long id;
        + }
        ```
- Migrate all other IBM Db2-specific content to Azure Database for PostgreSQL. Verify each change is functionally equivalent and compatible.
