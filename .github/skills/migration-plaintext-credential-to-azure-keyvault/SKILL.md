---
name: migration-plaintext-credential-to-azure-keyvault
description: Migrates hardcoded plaintext credentials (passwords, secrets, API keys, connection strings, tokens) in Java source code to Azure Key Vault for secure storage and retrieval. Use when securing Java applications by removing hardcoded credentials, migrating plaintext secrets to Azure Key Vault, or implementing centralized secret management.
---

name: 'Migrate plaintext credentials in Java to use Azure Key Vault'
description: "Migrate plaintext credentials in Java files to Azure Key Vault for secure storage and retrieval."
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    (password|secret|key|connectionString|credential|token|apiKey)[\s]*=[\s]*[\"\'"][^\"\';]*[\"\']|(private|public|protected|static|final)*[\s]+(String|char\[\])[\s]+(password|secret|key|connectionString|credential|token|apiKey)[\s]*=[\s]*[\"\'"][^\"\';]*[\"\']|[\.]put[\s]*\([\s]*[\"\'](password|secret|key|connectionString|credential|token|apiKey)[\"\']([\s]*,[^;\)]*)*[\s]*[\"\'"][^\"\';]*[\"\']

steps:
  - description: "Migrate plaintext credentials in Java to use Azure Key Vault"
    type: "instruction"
    content: |
      Applicable condition: Don't take the test file into consideration.
      Your task is to migrate any java file from using the plaintext credential to leverage Azure Key Vault to managed the credentials.
      Here are the steps:
        1. You have to make sure this is really a plaintext sensitive credential in java file before editing it. It must be in a string formula with password you can directly read.
          Ignore all other cases like a pass-in parameter, a variable read from environment variable or other config service.
          - ONLY modify sensitive credentials that are hardcoded directly in the source code
            * Example of sensitive credentials to modify: passwords, API keys, tokens, encryption keys, connection strings containing passwords
            * For example: `private final String dbPassword = "password123";` should be modified
          - DO NOT modify the following cases and leave them unchanged:
            * Regular configuration that isn't sensitive (URLs, hostnames, port numbers, usernames, database names)
              For example: `private final String dbUrl = "jdbc:mysql://localhost:3306/mydb";` should NOT be modified
            * Test cases and test files should be excluded from editing.
            * Code that calls a bean/service/method to retrieve a secret, including getter & setter functions
            * Code that reads credentials from environment variables, property files, or configuration systems
            * Code that directly or indirectly retrieves credentials from method parameters or dynamic context
              - For example:
                ```
                public boolean login(String email, String password) {
                    PreparedStatement st = conn.prepareStatement("SELECT * FROM user WHERE email = ? AND password = ?");
                    st.setString(1, email);
                    st.setString(2, password); // This should NOT be replaced with Azure Key Vault logic
                }
                ```
                ```
                String password = request.getParameter("password").trim();
                ```
                This should NOT be replaced with Azure Key Vault logic.
            * Any code that already uses a credential management system
          - We only want to modify the actual implementation where plaintext sensitive credentials are directly defined
        2. Base on the following API provided, leverage Azure Key Vault to manage the credential.

      Here are the APIs for your reference:

      If you want to read a secret from the Azure Key Vault, keep in mind always use `new DefaultAzureCredentialBuilder().build()` as your best choice. Here is a sample code:
      Don't forget to import the package for the `SecretClient` & `SecretClientBuilder` & `KeyVaultSecret`
      ```
      // Please replace with your own Key Vault URI and <secret-name>
      SecretClient secretClient = new SecretClientBuilder()
        .vaultUrl("<your-key-vault-url>")
        .credential(new DefaultAzureCredentialBuilder().build())
        .buildClient();

      KeyVaultSecret secret = secretClient.getSecret("<secret-name>");
      ```

name: 'Migrate plaintext credentials configuration to Azure Key Vault'
description: "Migrate plaintext credential configurations to Azure Key Vault for secure management."
codeLocation:
  type: textsearch
  filePattern: '**/{application,application-*,bootstrap,bootstrap-*,config}.{properties,yaml,yml}'
  codePattern: >-
    (?i)(^|\s|\.|\.\.)(password|secret|key|token|apiKey|accessKey|connectionString|credential)([._-]?\w*)[=:\s]+["']?[^"'\$\{\}\[\]<>][^"'\$\{\}\[\]<>]+["']?($|\s)

steps:
  - description: "Migrate plaintext credentials configuration to Azure Key Vault"
    type: "instruction"
    content: |
      Your task is to migrate an *.properties/yaml file from using the plaintext credentials configuration to leverage Azure Key Vault to manage the credentials.
      Here are the steps:
        1. You have to make sure this is really plaintext credentials in the config file before editing it. For other normal configurations like username, url, etc. Please keep them unchanged.
        2. For credential configurations:
           - Comment out the plaintext credential key-value pairs (do not delete them), replace the value with REDACTED
           - Add the following comment and configuration line (only once per file):
             ```
             # Replace <your-vault-name> with your actual Azure Key Vault name
             azure.keyvault.uri=https://<your-vault-name>.vault.azure.net
             ```
           - Ensure this configuration is only added once per file to avoid duplication
        3. If the file is a docker-compose file, do not modify.

name: 'Add Azure Key Vault dependency'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/{pom.xml,build.gradle,build.gradle.kts}'
  codePattern: ".*"

steps:
  - description: "Add Azure Key Vault dependency"
    type: "instruction"
    content: |
      Your task is to add Azure Key Vault dependency in the project build file.

      Azure Key Vault related dependencies:
        - groupId: com.azure
          artifactId: azure-security-keyvault-secrets
          version: 4.9.3
        - groupId: com.azure
          artifactId: azure-identity
          version: 1.15.4

