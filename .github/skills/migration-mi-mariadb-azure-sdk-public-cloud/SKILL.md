---
name: migration-mi-mariadb-azure-sdk-public-cloud
description: Migrates Java applications from password-based MariaDB authentication to Azure Managed Identity for Azure Database for MariaDB in public cloud using AzureMysqlAuthenticationPlugin. Updates JDBC connection and authentication configuration. Use when enabling managed identity for Azure Database for MariaDB, removing MariaDB passwords, or implementing credential-free MariaDB authentication in Azure.
---

name: "Update code to use Managed Identity in Azure Database for MariaDB (Public Cloud)"
description: "Update the database authentication mechanism to Azure Database for MariaDB managed identity authentication using AzureMysqlAuthenticationPlugin."
codeLocation:
  type: "textsearch"
  codePattern: "DriverManager"
  filePattern: "**/*.java"
steps:
  - description: "Migrate to Managed Identity authentication"
    type: "instruction"
    content: |
      Your task is to migrate a java file from using a connection string to using passwordless managed identity for authentication in Azure Database for MariaDB (Public Cloud).
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Please ensure to follow the guidance below to complete this task:
      1. Remove password Usage: Eliminate the hardcoded password in the connection string.
      2. Replace the value of user name with managed identity for the database connection: Please use the name of managed identity to replace the value of the user name for MariaDB database connection.
      3. Add Authentication Plugin Config: Please add a new string variable for authenticationPluginClassNameConfig. The value should be exactly this string "&authenticationPlugins=com.azure.identity.extensions.jdbc.mysql.AzureMysqlAuthenticationPlugin"
      4. Append the mentioned authenticationPluginClassNameConfig to the connection string url.
      5. Use the updated connection string url to get Connection.

      Below are the APIs provided for your reference:

      Class: DriverManager
        Description: The basic service for managing a set of JDBC drivers.
        Package: java.sql
        Methods:
          getConnection(String url): Attempts to establish a connection to the given database URL.
          getConnection(String url, Properties info): Attempts to establish a connection to the given database URL.

name: "Add dependency for Managed Identity in Azure Database for MariaDB (Public Cloud)"
description: "Add the azure-identity-extensions library as a dependency to enable managed identity support."
codeLocation:
  type: "textsearch"
  codePattern: "mariadb"
  filePattern: "**/{pom.xml,build.gradle}"
steps:
  - description: "Add azure-identity-extensions dependency"
    type: "instruction"
    content: |
      Please add the azure-identity-extensions dependency:
      groupId: com.azure
      artifactId: azure-identity-extensions
      version: 1.1.14

      Note:
      1. Please check the latest version of newly added dependencies, and upgrade the version if possible.
      2. If the version is covered by bom (like spring-boot-dependencies / spring-cloud-azure-dependencies / azure-sdk-bom), then don't specify version directly.

name: "Update properties for Managed Identity in Azure Database for MariaDB (Public Cloud)"
description: "Update application configuration properties with managed identity authentication related settings, and remove original password or connection string settings."
codeLocation:
  type: "textsearch"
  codePattern: ".*"
  filePattern: "**/application{,-*}.{yml,yaml,properties}"
steps:
  - description: "Add properties for Managed Identity authentication"
    type: "instruction"
    content: |
      Your task is to migrate a configuration file to use managed identity for authentication in Azure Database for MariaDB instead of a password.
      If the configuration file is yaml, please ensure the indentation and format is correct and consistent with the rest of the file.

      1. Add the configuration for Azure managed identity name.

      2. Remove the configuration for the password of the **MariaDB** database:
        - Removing password segments from JDBC connection strings (typically after the & symbol)
        - Removing the password property from the configuration file
      Note: please do not remove the password property if it is used for other purposes.
