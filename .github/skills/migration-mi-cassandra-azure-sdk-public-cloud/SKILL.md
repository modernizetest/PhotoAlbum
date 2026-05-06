---
name: migration-mi-cassandra-azure-sdk-public-cloud
description: Migrates Java applications to connect to Azure Cosmos DB for Apache Cassandra using managed identity via Service Connector in Azure public cloud. Updates CqlSession configuration and Spring Data Cassandra properties. Use when migrating Java or Spring Boot applications to Azure Cosmos DB Cassandra API, enabling managed identity for Cassandra connections, or replacing Cassandra password authentication.
---

name: "Update Java code to connect to Azure Cosmos DB for Cassandra via Service Connector in Azure public cloud"
description: "Update Java code to make Java applications or Spring Boot applications connect to Azure Cosmos DB for Cassandra via Service Connector in Azure public cloud"
codeLocation:
  type: "textsearch"
  codePattern: "CqlSession"
  filePattern: "**/*.java"
steps:
  - description: "Update Java code to connect to Azure Cosmos DB for Cassandra"
    type: "instruction"
    content: |
      Your task is to update Java code to connect to Azure Cosmos DB for Cassandra via Service Connector in Azure public cloud.

      1. For applications that have the dependency "spring-boot-starter-data-cassandra" and do not create their own CqlSession:
        Do nothing, because properties with prefix "spring.data.cassandra" will be injected as environment variables.

      2. For other Java applications that create their own CqlSession, create a CqlSession with a password retrieved by an Azure AD token.
        2.1. Only update files that create CqlSession, not files that just use it as a parameter.
        2.2. Merge the following template code fragment into existing code:
          ```java
          import java.net.InetSocketAddress;
          import java.net.URI;
          import java.net.http.HttpClient;
          import java.net.http.HttpRequest;
          import java.net.http.HttpResponse;
          import javax.net.ssl.SSLContext;
          import com.azure.core.credential.AccessToken;
          import com.azure.core.credential.TokenRequestContext;
          import com.azure.identity.DefaultAzureCredential;
          import com.azure.identity.DefaultAzureCredentialBuilder;
          import com.datastax.oss.driver.api.core.CqlSession;
          import org.json.simple.JSONObject;
          import org.json.simple.parser.JSONParser;

              try {
                  int cassandraPort = Integer.parseInt(System.getenv("AZURE_COSMOS_PORT"));
                  String cassandraUsername = System.getenv("AZURE_COSMOS_USERNAME");
                  String cassandraHost = System.getenv("AZURE_COSMOS_CONTACTPOINT");
                  String cassandraKeyspace = System.getenv("AZURE_COSMOS_KEYSPACE");
                  String listKeyUrl = System.getenv("AZURE_COSMOS_LISTKEYURL");
                  String scope = System.getenv("AZURE_COSMOS_SCOPE");

                  // If possible, inject DefaultAzureCredential as a bean instead of creating it directly here
                  DefaultAzureCredential defaultCredential = new DefaultAzureCredentialBuilder().build();

                  // Get the access token.
                  AccessToken accessToken = defaultCredential.getToken(new TokenRequestContext().addScopes(new String[]{ scope })).block();
                  String token = accessToken.getToken();

                  // Get the password.
                  HttpClient client = HttpClient.newBuilder()
                      .version(HttpClient.Version.HTTP_1_1) // Without this line, will cause a runtime error such as HTTP Error 411. The request must be chunked or have a content length
                      .build();
                  HttpRequest request = HttpRequest.newBuilder()
                      .uri(new URI(listKeyUrl))
                      .header("Authorization", "Bearer " + token)
                      .POST(HttpRequest.BodyPublishers.noBody())
                      .build();
                  HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
                  JSONParser parser = new JSONParser();
                  JSONObject responseBody = (JSONObject) parser.parse(response.body());
                  String cassandraPassword = (String) responseBody.get("primaryMasterKey");

                  // Connect to Azure Cosmos DB for Cassandra with proper SSL configuration
                  final SSLContext sc = SSLContext.getInstance("TLS");
                  sc.init(null, null, null); // Without this line, it will cause this runtime error: IllegalStateException: SSLContext is not initialized
                  return CqlSession.builder()
                          .withSslContext(sc)
                          .addContactPoint(new InetSocketAddress(cassandraHost, cassandraPort))
                          .withLocalDatacenter("West US 2") // 1. Without this line, it will cause a runtime error. 2. Make sure it's the same as your Azure Cosmos DB account's location before deploying to Azure.
                          .withKeyspace(cassandraKeyspace) // Without this line, it will cause this runtime error: NoNodeAvailableException: No node was available to execute the query
                          .withAuthCredentials(cassandraUsername, cassandraPassword)
                          .build();
              } catch (Exception e) {
                  throw new RuntimeException("Failed to create Cassandra session", e);
              }
            ```
        2.3. Remove all comments from the template code.
        2.4. When both the environment variable name from new added code and original code can be used, use the new added one.
        2.5. Keep other CqlSession configuration related code in existing code:
          ```java
          DriverConfigLoader loader = DriverConfigLoader.programmaticBuilder()
            .withDuration(DefaultDriverOption.REQUEST_TIMEOUT, Duration.ofSeconds(5))
            .withDuration(DefaultDriverOption.CONNECTION_INIT_QUERY_TIMEOUT, Duration.ofSeconds(5))
            .withDuration(DefaultDriverOption.CONTROL_CONNECTION_TIMEOUT, Duration.ofSeconds(5))
            .build();

          var builder = CqlSession.builder()
            .addContactPoint(new InetSocketAddress(contactPoints, port))
            .withLocalDatacenter(localDatacenter)
            .withConfigLoader(loader);
          ```
        2.6. For Spring beans, don't create DefaultAzureCredential as a local variable, inject it as a bean instead.
          2.6.1. Prefer this way in Spring bean definition methods: Define DefaultAzureCredential as a bean, and inject DefaultAzureCredential as a bean
            ```java
            import com.azure.core.credential.TokenCredential;
            import com.azure.identity.DefaultAzureCredential;
            import com.azure.identity.DefaultAzureCredentialBuilder;
            import com.datastax.oss.driver.api.core.CqlSession;
            import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
            import org.springframework.context.annotation.Bean;

            // Important: Add bean definition in case it's not defined in other places.
            @Bean
            @ConditionalOnMissingBean // Add this in case it's defined in other places.
            public TokenCredential credential() { // Caution: the return type is TokenCredential
              return new DefaultAzureCredentialBuilder().build();
            }
            // Inject TokenCredential as bean
            @Bean
            public CqlSession cqlSession(TokenCredential credential) {
              // Use credential here.
              return CqlSession.builder()...
            }
            ```
          2.6.2. Avoid this way in Spring bean definition methods: Create DefaultAzureCredential as a local variable
            ```java
            import com.azure.identity.DefaultAzureCredential;
            import com.azure.identity.DefaultAzureCredentialBuilder;
            import com.datastax.oss.driver.api.core.CqlSession;
            import org.springframework.context.annotation.Bean;

            @Bean
            public CqlSession cqlSession() {
              // Create DefaultAzureCredential as local variable
              DefaultAzureCredential defaultCredential = new DefaultAzureCredentialBuilder().build(); // Import DefaultAzureCredentialBuilder and use its simple name rather than using fully qualified name.
              // Use credential here.
              return CqlSession.builder()...
            }
            ```
        2.7. For environment variables and properties, only use the names that exist in existing code or provided by Service Connector (listed below).
            - AZURE_COSMOS_LISTKEYURL
            - AZURE_COSMOS_SCOPE
            - AZURE_COSMOS_RESOURCEENDPOINT
            - AZURE_COSMOS_CONTACTPOINT
            - AZURE_COSMOS_PORT
            - AZURE_COSMOS_KEYSPACE
            - AZURE_COSMOS_USERNAME
            - AZURE_COSMOS_CLIENTID
        2.8. If it is supported to use "@Value" in current file, then use it to replace "System.getenv()". And use property instead of environment variable in "@Value".
          2.8.1. Example:
            ```java
            @Value("${azure.cosmos.listkeyurl}")
            private String listKeyUrl;
            ```
          2.8.2. Use property (azure.cosmos.listkeyurl) instead of environment variable (AZURE_COSMOS_LISTKEYURL).
          2.8.3. Use lowercase for all characters in property name.
          2.8.4. When both the property name from new added code (example: "azure.cosmos.listkeyurl") and original code (example: "app.cosmos.listkeyurl") can be used, use the new added one.
        2.9. Remove unused code and comments. For example: If some private field and private method will never be used after your modification, then delete them all.
        2.10. Organize imports:
            - Prefer importing classes and using their simple names rather than using fully qualified names.
            - Remove unused imports.
            - Add missing imports.
            - Keep existing import order.

name: "Update dependencies to connect to Azure Cosmos DB for Cassandra via Service Connector in Azure public cloud"
description: "Update dependencies to make Java applications or Spring Boot applications connect to Azure Cosmos DB for Cassandra via Service Connector in Azure public cloud"
codeLocation:
  type: "textsearch"
  codePattern: "cassandra|datastax|java-driver"
  filePattern: "**/{pom.xml,build.gradle,build.gradle.kts}"
steps:
  - description: "Update dependencies to connect to Azure Cosmos DB for Cassandra"
    type: "instruction"
    content: |
      Please add the following dependencies to your project build file. These are required to use managed identity with Azure Cosmos DB for Cassandra via Service Connector:

      1. For applications that have the dependency "spring-boot-starter-data-cassandra" and do not create their own CqlSession: do nothing.

      2. For other Java applications that create their own CqlSession, add these dependencies:
        - groupId: com.datastax.oss
          artifactId: java-driver-core
          version: 4.5.1
        - groupId: com.datastax.oss
          artifactId: java-driver-query-builder
          version: 4.5.1
        - groupId: com.datastax.cassandra
          artifactId: cassandra-driver-extras
          version: 3.1.4
        - groupId: com.azure
          artifactId: azure-identity
          version: 1.14.2
        - groupId: com.googlecode.json-simple
          artifactId: json-simple
          version: 1.1.1

      Note:
        1. Please check the latest version of newly added dependencies, and upgrade to the latest version if possible.
        2. If the version is covered by bom (like spring-boot-dependencies / spring-cloud-azure-dependencies / azure-sdk-bom), then don't specify the version directly.

name: "Update properties to connect to Azure Cosmos DB for Cassandra via Service Connector in Azure public cloud"
description: "Update properties to make Java applications or Spring Boot applications connect to Azure Cosmos DB for Cassandra via Service Connector in Azure public cloud"
codeLocation:
  type: "textsearch"
  codePattern: ".*"
  filePattern: "**/application{,-*}.{yml,yaml,properties}"
steps:
  - description: "Update properties to connect to Azure Cosmos DB for Cassandra"
    type: "instruction"
    content: |
      To migrate to managed identity authentication in Azure Cosmos DB for Cassandra API, follow these steps:

      1. For applications that have the dependency "spring-boot-starter-data-cassandra" and do not create their own CqlSession:
        When deployed to Azure, the Service Connector will provide these properties:
          ```properties
          spring.data.cassandra.contact-points=xxx
          spring.data.cassandra.port=
          spring.data.cassandra.keyspace-name=
          spring.data.cassandra.local-datacenter=
          spring.data.cassandra.ssl=
          spring.data.cassandra.username=
          spring.data.cassandra.password=
          ```
        However, properties that start with "spring.data" only work for Spring Boot version 2.x, not for Spring Boot 3.x. In Spring Boot 3.x, the correct properties should start with "spring.cassandra".
        1.1. If the application depends on Spring Boot 2.x, then do nothing.
        1.2. If the application depends on Spring Boot 3.x, add the following properties to make Service Connector-provided properties take effect:
          ```properties
          spring.cassandra.contact-points=${spring.data.cassandra.contact-points}
          spring.cassandra.port=${spring.data.cassandra.port}
          spring.cassandra.keyspace-name=${spring.data.cassandra.keyspace-name}
          spring.cassandra.local-datacenter=${spring.data.cassandra.local-datacenter}
          spring.cassandra.ssl.enabled=${spring.data.cassandra.ssl}
          spring.cassandra.username=${spring.data.cassandra.username}
          spring.cassandra.password=${spring.data.cassandra.password}
          ```
        If the property file already contains related properties, delete the original properties before adding the above properties.

      2. For other Java applications that create their own CqlSession, update properties.
        2.1. All Service Connector-provided environment variable names:
          - AZURE_COSMOS_LISTKEYURL
          - AZURE_COSMOS_SCOPE
          - AZURE_COSMOS_RESOURCEENDPOINT
          - AZURE_COSMOS_CONTACTPOINT
          - AZURE_COSMOS_PORT
          - AZURE_COSMOS_KEYSPACE
          - AZURE_COSMOS_USERNAME
          - AZURE_COSMOS_CLIENTID
        2.2. Use Service Connector environment variables when available:
          2.2.1. Example:
            ```properties
            # Before migration
            cassandra.keyspace=test_keyspace
            # After migration
            # The variables that start with "AZURE_COSMOS_" are compatible with the ones provided by Azure Service Connector.
            # Refs: https://learn.microsoft.com/azure/service-connector/how-to-integrate-cosmos-cassandra?tabs=java
            cassandra.keyspace=${AZURE_COSMOS_KEYSPACE:""}
            ```
          2.2.2. Keep the reference link in the property file.
          2.2.3. Use only the correct environment variable names listed above.
          2.2.4. Add a default value in case some environment variable does not exist (depends on service connector type).
          2.2.5. Make sure the property key and value correspond correctly. For example: AZURE_COSMOS_LISTKEYURL is used to get the key, it cannot be used as property value for these property keys: "app.cosmos.connection-string" or "cassandra.password".
        2.3. Add properties for all Service Connector-provided environment variables.
          2.3.1. For example, for the environment variable "AZURE_COSMOS_LISTKEYURL", add this property:
            ```properties
            azure.cosmos.listkeyurl=${AZURE_COSMOS_LISTKEYURL:""} # Note: Use lowercase for all characters in property name.
            ```
          2.3.2. All the 8 environment variables listed above should be added.
          2.3.3. Delete duplicate properties only when they have the same key. Don't delete them if they have the same value. For example:
            ```properties
            # Keep them all because they have different property keys.
            azure.cosmos.listkeyurl=${AZURE_COSMOS_LISTKEYURL:""}
            azure.listkeyurl=${AZURE_COSMOS_LISTKEYURL:""}
            app.cosmos.listkeyurl=${AZURE_COSMOS_LISTKEYURL:""}
            ```
        2.4. For Cassandra connection related properties without Service Connector equivalents, set default values with comments:
          ```properties
          # Before migration
          cassandra.localDatacenter=datacenter1
          # After migration
          cassandra.localDatacenter="West US 2" # Caution: Make sure this value is correct.
          ```

