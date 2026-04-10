---
name: migration-mi-azuresql-azure-sdk-21v-china
description: Migrate from SQL Database to Azure SQL Database with Azure SDK and managed identity in Mooncake for secure, credential-free authentication.
---

# mi-azuresql-azure-sdk-21v-china

## Overview

Your job is to migrate from SQL Database to Azure SQL Database with Azure SDK and managed identity in Mooncake for secure, credential-free authentication.
Below are the specific instructions for different migration tasks, please follow the instructions to complete the migration.

## Knowledge Base Content

* KB ID: 
* Title: Upgrade code to use Managed Identity in Azure SQL (China Cloud)
* Description: Migrate SQL Server authentication to use Azure Managed Identity with ActiveDirectoryMSI in China Cloud.
* Content: 

## Upgrade code to use Managed Identity in Azure SQL (China Cloud)

Migrate SQL Server authentication to use Azure Managed Identity with ActiveDirectoryMSI in China Cloud.

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `SQLServerDataSource`

### Instruction

Your task is to migrate a java file from using a connection string to using passwordless managed identity for authentication in Azure SQL (China Cloud).
Ensure the resulting code is clean, efficient, and preserves the original functionality.
Please ensure to follow the guidance below to complete this task:
1. Remove user and password usage: Eliminate the hardcoded user and password in the connection string.
2. Please add a variable for the Azure client ID of Azure managed identity.
3. Please append msiClientId to the connection string url: ";msiClientId=" + <azure managed identity client id>
4. Please append this exact string of authentication to the connection string url: ";authentication=ActiveDirectoryMSI"
5. Use the updated connection string url for SQLServerDataSource when set url.

Below are the APIs provided for your reference:

Class: SQLServerDataSource
  Description: Represents a list of properties specific to connecting to a SQL Server database by using a SQLServerConnection object.
  Package: com.microsoft.sqlserver.jdbc
  Implements: ISQLServerDataSource, DataSource, java.io.Serializable, javax.naming.Referenceable
  Contructor:
    SQLServerDataSource(): Initializes a new instance of the SQLServerDataSource class.
  Methods:
    setUrl(String url): Sets the URL that is used to connect to the data source.
    getURL(): Returns the URL used to connect to the data source.
    getConnection(): 	Tries to establish a connection with the data source that this SQLServerDataSource object represents.



## Add properties for Managed Identity in Azure SQL (China Cloud)

Add the Azure Managed Identity client ID properties for Azure SQL in China Cloud.

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/application{,-*}.{yml,yaml,properties}`
- Regex pattern to find code lines: `.*`

### Instruction

Your task is to migrate a configuration file to use managed identity for authentication in Azure SQL instead of a password.
If the configuration file is yaml, please ensure the indentation and format is correct and consistent with the rest of the file.
Please ensure the formats of keys and values remain consistent with the naming convention of the original ones.

1. Please add the configuration for the Azure client ID for managed identity.
  Common naming conventions include AZURE_CLIENT_ID, azure.client.id, azure.identity.client-id.
  Please apply a naming convention consistent with the style of the context.

2. Remove the configuration for the password of the **SQL** database:
  - Removing password segments from JDBC connection strings (typically after the ; symbol)
  - Removing the password property from the configuration file
Note: please do not remove the password property if it is used for other purposes.