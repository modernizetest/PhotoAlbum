---
name: migration-oracle-to-postgresql
description: Migrates Java application database layer from Oracle Database to PostgreSQL, including JDBC driver changes, SQL syntax conversion, and Oracle-specific feature replacement. Uses project-specific coding_notes.md guidance when available. Use when migrating Java applications from Oracle to PostgreSQL, converting Oracle SQL to PostgreSQL syntax, or replacing Oracle JDBC drivers.
---

# Migrate from Oracle to PostgreSQL

Your task is to migrate a project from using Oracle to using PostgreSQL.

## Migration steps

1. Locate the `coding_notes.md` file:
    - If `coding_notes.md` is already provided in the prompt or context, use it and skip to step 2.
    - Otherwise, search for `coding_notes.md` in the migration project workspace using the pattern `.github/postgres-migrations/*/results/application_guidance/coding_notes.md`.
    - If multiple files are found, compare their modification timestamps and use the most recently modified file.
    - If no `coding_notes.md` file is found, proceed to step 3 and follow only the requirements below.
2. If `coding_notes.md` is found, read its entire content before listing files that need to be migrated.
    - The file contains project-specific migration guidance and rules that must be read before listing files that need to be migrated.
    - The file may exceed 1,000 lines; ensure you read it completely from start to end.
3. Review the requirements below. **Priority rule**: If any requirement conflicts with guidance in `coding_notes.md`, follow the `coding_notes.md` instructions instead.
4. Apply the requirements to the project.

## Requirements

- Don't modify any content that is not related to Oracle to PostgreSQL migration.
- Enable passwordless connection. Use managed identity by default. Add comments to show how to authenticate by service principal.
    - For a Spring Boot project
        - Update dependencies
            1. Use spring-cloud-azure-dependencies (bom) to manage the Spring Cloud Azure dependency version. Choose a version of spring-cloud-azure-dependencies that is compatible with your Spring Boot version:
                - For projects using spring-boot:2.x, spring-cloud-azure-dependencies' version should >=`4.20.0` and < `5.0.0`.
                - For projects using spring-boot:3.x, spring-cloud-azure-dependencies' version should >= `5.22.0` and < `7.0.0`.
                - For projects using spring-boot:4.x, spring-cloud-azure-dependencies' version should >=`7.1.0`.
            2. Add a new dependency: com.azure.spring:spring-cloud-azure-starter-jdbc-postgresql.
        - Update properties
            1. Remove any password/secret configuration for the Azure Database for PostgreSQL datasource (for example, `spring.datasource.password` or passwords embedded in the JDBC URL), but keep or configure the required username (typically the managed identity or Azure AD principal name). In applications with multiple datasources, update only the PostgreSQL datasource credentials.
            2. Add Azure Database for PostgreSQL passwordless-related properties.
            3. Add comments about Azure sovereign cloud deployment.
            4. Add comments about authentication by a service principal.
            5. Example modification.
                ```diff
                - spring.datasource.url=jdbc:postgresql://localhost:5432/testdb
                - spring.datasource.username=testuser
                - spring.datasource.password=testpass
                + # 1. Do not set spring.datasource.password, access token will be retrieved automatically and used as password.
                + # 2. For system-assigned managed identity only, "spring.cloud.azure.credential.client-id" can be omitted.
                + # 3. For service principal auth, remove "spring.cloud.azure.credential.managed-identity-enabled" property and add these properties:
                + #   spring.cloud.azure.profile.tenant-id=<your-service-principal-tenant-id>
                + #   spring.cloud.azure.credential.client-id=<your-service-principal-client-id>
                + #   spring.cloud.azure.credential.client-secret=<your-service-principal-client-secret>
                + # 4. For Azure sovereign clouds, set the following two properties (the "azure" cloud type is the default and can be omitted):
                + #   spring.cloud.azure.profile.cloud-type=azure_china / azure_germany / azure_us_government / azure
                + #   spring.datasource.azure.scopes=<scope-for-your-cloud>
                + #     azure_china: https://ossrdbms-aad.database.chinacloudapi.cn/.default
                + #     azure_germany: https://ossrdbms-aad.database.cloudapi.de/.default
                + #     azure_us_government: https://ossrdbms-aad.database.usgovcloudapi.net/.default
                + #     azure: https://ossrdbms-aad.database.windows.net/.default
                + # 5. Remember to set the values for the environment variables in the URL below
                + spring.datasource.url=jdbc:postgresql://${POSTGRESQL_SERVER}.postgres.database.azure.com:${POSTGRESQL_PORT}/${POSTGRESQL_DATABASE}?sslmode=require
                + spring.datasource.username=${MANAGED_IDENTITY_NAME}
                + spring.datasource.azure.passwordless-enabled=true
                + spring.cloud.azure.credential.client-id=<your_managed_identity_client_id>
                + spring.cloud.azure.credential.managed-identity-enabled=true
                ```
    - For other Java projects
        1. Add a new dependency: com.azure:azure-identity-extensions:1.2.2. Check the latest compatible version of the dependency, and upgrade the version if possible.
        2. In the properties file, update the PostgreSQL JDBC URL to support authentication with managed identity.
            * Delete all "username" and "password" related content that ONLY corresponds to the PostgreSQL JDBC URL.
            * Add these parameters to the PostgreSQL JDBC URL:
                - user=${MANAGED_IDENTITY_NAME}
                - sslmode=require (IMPORTANT: Use "require" instead of other values like "verify-full")
                - authenticationPluginClassName=com.azure.identity.extensions.jdbc.postgresql.AzurePostgresqlAuthenticationPlugin
                - azure.managedIdentityEnabled=true
                - azure.clientId=${MANAGED_IDENTITY_CLIENT_ID}
            * Use environment variables for database host/port/database name if the original value does not point to Azure Database for PostgreSQL.
            * Add an example PostgreSQL JDBC URL to show how to authenticate with a service principal. These parameters are required:
                - user=${SERVICE_PRINCIPAL_NAME}
                - sslmode=require (IMPORTANT: Use "require" instead of other values like "verify-full")
                - authenticationPluginClassName=com.azure.identity.extensions.jdbc.postgresql.AzurePostgresqlAuthenticationPlugin
                - azure.clientId=${SERVICE_PRINCIPAL_CLIENT_ID}
                - azure.clientSecret=${SERVICE_PRINCIPAL_CLIENT_SECRET}
                - azure.tenantId=${SERVICE_PRINCIPAL_TENANT_ID}
            * Do not add default values for environment variables.
            * Example modification.
                ```diff
                - url=jdbc:postgresql://localhost:5432/testdb
                - username=testuser
                - password=testpass
                + # 1. Do not set password, access token will be retrieved automatically and used as password.
                + # 2. For system-assigned managed identity only, "azure.clientId" can be omitted in the jdbc url parameters.
                + # 3. For service principal auth, delete "azure.managedIdentityEnabled=true" in the jdbc url parameters, and add these jdbc url parameters:
                + #    azure.tenantId
                + #    azure.clientId
                + #    azure.clientSecret
                + # 4. Remember to set the values for the environment variables in the URL below
                + url=jdbc:postgresql://${POSTGRESQL_SERVER}.postgres.database.azure.com:${POSTGRESQL_PORT}/${POSTGRESQL_DATABASE}?user=${MANAGED_IDENTITY_NAME}&sslmode=require&authenticationPluginClassName=com.azure.identity.extensions.jdbc.postgresql.AzurePostgresqlAuthenticationPlugin&azure.managedIdentityEnabled=true&azure.clientId=${MANAGED_IDENTITY_CLIENT_ID}
                ```
        3. In the Java code, comment out all "username" and "password" related content that ONLY corresponds to the PostgreSQL JDBC URL.
            * Example modification 1.
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
            * Example modification 2.
                ```diff
                - hikariDataSource.setUsername(dataSource1Config.getUsername());
                - hikariDataSource.setPassword(dataSource1Config.getPassword());
                + // Comment out all content about "username" and "password" because now PostgreSQL will authenticate using managed identity.
                + // hikariDataSource.setUsername(dataSource1Config.getUsername());
                + // hikariDataSource.setPassword(dataSource1Config.getPassword());
                ```
        4. Enable Azure sovereign cloud by adding the azure.authorityHost property in JDBC URL, either in Java code or in property file.
            * For Azure China Cloud.
                Example in Java code:
                ```diff
                + properties.put("azure.authorityHost",AzureAuthorityHosts.AZURE_CHINA);
                ```
                Example in property file:
                ```diff
                + url={JDBC_URL}&azure.authorityHost=https://login.chinacloudapi.cn
                ```
            * For Azure Germany Cloud.
                Example in Java code:
                ```diff
                + properties.put("azure.authorityHost",AzureAuthorityHosts.AZURE_GERMANY);
                ```
                Example in property file:
                ```diff
                + url={JDBC_URL}&azure.authorityHost=https://login.microsoftonline.de
                ```
            * For Azure Government Cloud.
                Example in Java code:
                ```diff
                + properties.put("azure.authorityHost",AzureAuthorityHosts.AZURE_GOVERNMENT);
                ```
                Example in property file:
                ```diff
                + url={JDBC_URL}&azure.authorityHost=https://login.microsoftonline.us
                ```
            * For Unknown Cloud, add comments.
                Example in Java code:
                ```diff
                + // you need to manually configure the 'azure.authorityHost' for the following clouds:
                + //   - Azure Germany:          properties.put("azure.authorityHost",AzureAuthorityHosts.AZURE_GERMANY);
                + //   - Azure China (21Vianet): properties.put("azure.authorityHost",AzureAuthorityHosts.AZURE_CHINA);
                + //   - Azure US Government:    properties.put("azure.authorityHost",AzureAuthorityHosts.AZURE_GOVERNMENT);
                ```
                Example in property file:
                ```diff
                + # you need to manually configure the 'azure.authorityHost' for the following clouds:
                + #    azure.authorityHost = (one-of-the-following-values)
                + #      - azure_china: https://login.chinacloudapi.cn
                + #      - azure_germany: https://login.microsoftonline.de
                + #      - azure_us_government: https://login.microsoftonline.us
                ```
            * For Azure Public Cloud, do not add anything.
- Use lowercase for identifiers (like table and column names) and data types (like varchar). Use uppercase for SQL keywords (like `SELECT`, `FROM`, `WHERE`). This includes SQL statements and JPA annotations like `@Table`, `@Column`, `@NamedNativeQuery`, and `@Query`.
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
- Migrate all other Oracle-specific content to PostgreSQL. Verify each change is functionally equivalent and compatible.
