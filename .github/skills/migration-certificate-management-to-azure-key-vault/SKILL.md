---
name: migration-certificate-management-to-azure-key-vault
description: Migrates Java TLS/MTLS certificate management from local KeyStore storage to Azure Key Vault JCA (Java Cryptography Architecture). Replaces local certificate handling with Azure Key Vault for centralized certificate management. Use when migrating Java applications that use local KeyStore, SSLContext, or Certificate classes to Azure Key Vault for secure certificate storage.
---

name: 'Migrate TLS/MTLS certificate from local to Azure Key Vault'
description: "Migrate TLS/MTLS certificate management from local storage to Azure Key Vault"
codeLocation:
  type: textsearch
  filePattern: "**/*.java"
  codePattern: >-
    KeyStore|Certificate|SSLContext

steps:
  - description: "Migrate TLS/MTLS certificate management from local storage to Azure Key Vault"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from managing TLS/MTLS certificates locally (e.g., using KeyStore) to managing certificates in Azure Key Vault JCA while maintaining the same functionality. Below is a reference to the relevant Azure Key Vault APIs and migration examples for your convenience.
      Please notes:
      Replace `KeyStore` initialization with Azure Key Vault JCA equivalents.         
        - Example:
        ```java
        // Local KeyStore example
        KeyStore keyStore = KeyStore.getInstance("JKS");

        // Azure Key Vault JCA equivalent
        KeyVaultJcaProvider provider = new KeyVaultJcaProvider();
        Security.addProvider(provider);
        KeyStore keyStore = KeyVaultKeyStore.getKeyVaultKeyStoreBySystemProperty();
        ```
      Should not remove KeyManagerFactory, need it to initialize SSLContext.
      Make sure you add the following Descriptions as Comments if using KeyVaultKeyStore.getKeyVaultKeyStoreBySystemProperty()
        /**
         * Set the following configuration as system properties
         * - `azure.keyvault.uri`: The URI of your Azure Key Vault.
         * - `azure.keyvault.tenant-id`: The tenant ID of your Azure Active Directory.
         * - `azure.keyvault.client-id`: The client ID of your Azure Active Directory application.
         * - `azure.keyvault.client-secret`: The client secret of your Azure Active Directory application.
         */

      Ensure the resulting code is clean, efficient, and preserves the original functionality. Keep all irrelevant code/comments unchanged.

name: 'Add Azure Key Vault JCA dependency'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/{pom.xml,build.gradle,build.gradle.kts}'
  codePattern: ".*"

steps:
  - description: "Add Azure Key Vault JCA dependency"
    type: "instruction"
    content: |
      Your task is to add Azure Key Vault JCA dependency to a pom.xml, build.gradle, or build.gradle.kts file. Make sure you add the correct dependencies as below:

      Azure Key Vault JCA related dependencies:
      - groupId: com.azure
        artifactId: azure-security-keyvault-jca
        version: 2.10.0
      - groupId: com.azure
        artifactId: azure-identity
        version: 1.15.4

