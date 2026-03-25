# Azure Service Bus Emulator TestContainers Coding Reference

## Contents
- 1. MANDATORY - Choose Approach based on Spring/non-Spring, Spring Boot version, TestContainers version
- 2. MANDATORY - Scan all queues/topics/subscriptions before writing code
- 3. MANDATORY - Spring Context Isolation — for ALL Spring approaches
  + Always add `@ActiveProfiles("test")`
- 4. Wire ALL beans from the real emulator — do NOT mock
- 5. Example of Service Bus Emulator config.json
- 6. Emulator with ServiceBusEmulatorContainer (testcontainers >= 1.20.5)
  + Setting up a network
  + Starting a SQL Server container as dependency
  + Starting a Service Bus Emulator container
  + Using Azure Service Bus clients
  + Emulator with GenericContainer (testcontainers < 1.20.5)
- 7. Using Spring Cloud Azure with @ServiceConnection (Spring Boot >= 3.1)
  + Maven dependencies
  + Container setup with @ServiceConnection
  + Spring messaging pattern (ServiceBusTemplate / ServiceBusSenderClient)
- 8. Spring Boot 2.x Pattern
- 9. Handle ServiceBusAdministrationClient
- 10. Handle Object/Bean creation with Azure Token Credential/TokenCredential/DefaultAzureCredential
- 11. Emulator Readiness and Retry
- 12. Emulator fails to start
- 13. Common Gotchas

## MANDATORY - Choose Approach based on Spring/non-Spring, Spring Boot version, TestContainers version

**You MUST check the project's testcontainers and Spring Boot versions BEFORE writing any Service Bus test code.** Using the wrong approach wastes significant time on compilation and runtime failures that are impossible to fix.

- If project contains usage of `ServiceBusAdministrationClient`, use Service Bus emulator
- If Spring Boot **>= 3.1**, use `@ServiceConnection` for auto-wiring: [Using Spring Cloud Azure with @ServiceConnection](#using-spring-cloud-azure-with-serviceconnection-spring-boot--31)
- If Spring Boot **2.x**, use `@DynamicPropertySource` — `@ServiceConnection` is NOT available: [Spring Boot 2.x pattern](#spring-boot-2x-pattern)
- If testcontainers **>= 1.20.5**, use `ServiceBusEmulatorContainer` from `org.testcontainers:azure`: [Emulator with ServiceBusEmulatorContainer](#emulator-with-servicebusemulatorcontainer-testcontainers--1205)
- If testcontainers **< 1.20.5**, use `GenericContainer` with the emulator Docker image: [Emulator with GenericContainer](#emulator-with-genericcontainer-testcontainers--1205)


**CRITICAL: `ServiceBusEmulatorContainer` does NOT exist in testcontainers before 1.20.5.** If you see `ClassNotFoundException` or `cannot find symbol: class ServiceBusEmulatorContainer`, the project's testcontainers version is too old. Switch to the GenericContainer approach or upgrade testcontainers. The Maven artifact is `org.testcontainers:azure` (NOT `testcontainers-azure`).

## MANDATORY - Scan all queues/topics/subscriptions before writing code
The Service Bus emulator cannot create Service Bus queues/topics/subscriptions on the fly, so every resource need to be declared in the config.json. So scan the project to see what queues/topics/subscriptions need to be declared. And then define them in config.json.

## MANDATORY - Spring Context Isolation — for ALL Spring approaches

**This section applies to EVERY Service Bus test, regardless of whether you use `ServiceBusEmulatorContainer` or `GenericContainer`.** Skipping this is the #1 cause of `UnsatisfiedDependencyException` and context startup failures.

### Always add `@ActiveProfiles("test")`

```java
@SpringBootTest
@ActiveProfiles("test")  // MANDATORY — without this, application-test.properties/yml is NOT loaded
@Testcontainers
@Tag("Layer1")
class MyServiceBusL1Test { ... }
```

Without `@ActiveProfiles("test")`, the main `application.properties`/`application.yml` is used, which typically contains:
- Real Azure connection strings or `${AZURE_...}` placeholders that fail to resolve
- `spring.cloud.azure.credential.managed-identity-enabled=true` which tries real Azure auth
- Service Bus namespace URLs that attempt real AMQP connections

## Wire ALL beans from the real emulator — do NOT mock

**NEVER `@MockBean` the `ServiceBusSenderClient`, `ServiceBusTemplate`, `ServiceBusReceiverClient`, `ServiceBusProcessorClient`, `TokenCredential`, `ServiceBusAdministrationClient`, or ANY bean related to the migrated service.** All beans must be wired from the real emulator via object creation, `@DynamicPropertySource` or `@ServiceConnection`.

```java
@SpringBootTest
@ActiveProfiles("test")
@Testcontainers
@Tag("Layer1")
class MessageServiceL1Test {

    // Container setup (GenericContainer or ServiceBusEmulatorContainer)

    @DynamicPropertySource
    static void serviceBusProperties(DynamicPropertyRegistry registry) {
        String connectionString = String.format(
            "Endpoint=sb://%s:%d;SharedAccessKeyName=RootManageSharedAccessKey;"
            + "SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;",
            SERVICE_BUS.getHost(), SERVICE_BUS.getMappedPort(5672));
        registry.add("spring.cloud.azure.servicebus.connection-string", () -> connectionString);
        registry.add("spring.cloud.azure.servicebus.namespace", () -> "sbemulatorns");
        // Disable managed identity — the emulator uses SharedAccessKey from the connection string
        registry.add("spring.cloud.azure.credential.managed-identity-enabled", () -> "false");
    }

    // NO @MockBean at all — all beans wired from the real emulator
    @Autowired
    private MessageService messageService;  // The app's own service class under test

    // ... tests that exercise messageService methods ...
}
```

**If the `@Configuration` class uses `DefaultAzureCredentialBuilder`:** Set `spring.cloud.azure.credential.managed-identity-enabled=false` in `@DynamicPropertySource` and ensure the connection string includes `SharedAccessKeyName` + `SharedAccessKey`. The Spring Cloud Azure auto-configuration will use the connection string credential instead of `DefaultAzureCredential`.

**If the `@Configuration` class reads from `System.getenv()`:** Add test properties via `@DynamicPropertySource` or `@TestPropertySource` that satisfy those lookups, or add a test-friendly constructor/factory method to the config class (minimal safe source change).

**Self-check before running any test:** Does the application have ANY `@Configuration` class that creates `TokenCredential`, `ServiceBusAdministrationClient`, `ServiceBusTemplate`, `AzureServiceBusProperties`, `ServiceBusSenderClient`, or `SimpleMessageListenerContainer` beans? If yes, you MUST provide correct emulator connection properties via `@DynamicPropertySource` so these beans connect to the real emulator. Do NOT mock them.

## Example of Service Bus Emulator config.json

Place this file at `src/test/resources/config.json` (or `service-bus-config.json`):

### 

```json
{
  "UserConfig": {
    "Namespaces": [
      {
        "Name": "sbemulatorns",
        "Queues": [
          {
            "Name": "queue.1",
            "Properties": {
              "DeadLetteringOnMessageExpiration": false,
              "DefaultMessageTimeToLive": "PT1H",
              "DuplicateDetectionHistoryTimeWindow": "PT20S",
              "ForwardDeadLetteredMessagesTo": "",
              "ForwardTo": "",
              "LockDuration": "PT1M",
              "MaxDeliveryCount": 3,
              "RequiresDuplicateDetection": false,
              "RequiresSession": false
            }
          }
        ],

        "Topics": [
          {
            "Name": "topic.1",
            "Properties": {
              "DefaultMessageTimeToLive": "PT1H",
              "DuplicateDetectionHistoryTimeWindow": "PT20S",
              "RequiresDuplicateDetection": false
            },
            "Subscriptions": [
              {
                "Name": "subscription.1",
                "Properties": {
                  "DeadLetteringOnMessageExpiration": false,
                  "DefaultMessageTimeToLive": "PT1H",
                  "LockDuration": "PT1M",
                  "MaxDeliveryCount": 3,
                  "ForwardDeadLetteredMessagesTo": "",
                  "ForwardTo": "",
                  "RequiresSession": false
                },
                "Rules": [
                  {
                    "Name": "app-prop-filter-1",
                    "Properties": {
                      "FilterType": "Correlation",
                      "CorrelationFilter": {
                     "ContentType": "application/text",
                     "CorrelationId": "id1",
                     "Label": "subject1",
                     "MessageId": "msgid1",
                     "ReplyTo": "someQueue",
                     "ReplyToSessionId": "sessionId",
                     "SessionId": "session1",
                     "To": "xyz"
                   }
                    }
                  }
                ]
              },
              {
                "Name": "subscription.2",
                "Properties": {
                  "DeadLetteringOnMessageExpiration": false,
                  "DefaultMessageTimeToLive": "PT1H",
                  "LockDuration": "PT1M",
                  "MaxDeliveryCount": 3,
                  "ForwardDeadLetteredMessagesTo": "",
                  "ForwardTo": "",
                  "RequiresSession": false
                },
                "Rules": [
                  {
                    "Name": "user-prop-filter-1",
                    "Properties": {
                      "FilterType": "Correlation",
                      "CorrelationFilter": {
                        "Properties": {
                          "prop1": "value1"
                        }
                      }
                    }
                  }
                ]
              },
              {
                "Name": "subscription.3",
                "Properties": {
                  "DeadLetteringOnMessageExpiration": false,
                  "DefaultMessageTimeToLive": "PT1H",
                  "LockDuration": "PT1M",
                  "MaxDeliveryCount": 3,
                  "ForwardDeadLetteredMessagesTo": "",
                  "ForwardTo": "",
                  "RequiresSession": false
                }
              },
              {
                "Name": "subscription.4",
                "Properties": {
                  "DeadLetteringOnMessageExpiration": false,
                  "DefaultMessageTimeToLive": "PT1H",
                  "LockDuration": "PT1M",
                  "MaxDeliveryCount": 3,
                  "ForwardDeadLetteredMessagesTo": "",
                  "ForwardTo": "",
                  "RequiresSession": false
                },
                "Rules": [
                  {
                    "Name": "sql-filter-1",
                    "Properties": {
                      "FilterType": "Sql",
                      "SqlFilter": {
                        "SqlExpression": "sys.MessageId = '123456' AND userProp1 = 'value1'"
                      },
                      "Action" : {
                        "SqlExpression": "SET sys.To = 'Entity'"
                      }
                    }
                  }
                ]
              }
            ]
          }
        ]
      }
    ],
    "Logging": {
      "Type": "File"
    }
  }
}
```

## Emulator with ServiceBusEmulatorContainer (testcontainers >= 1.20.5)

**Requires: `org.testcontainers:azure` version >= 1.20.5**

```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>azure</artifactId>
    <version>1.20.5</version><!-- or newer; class does NOT exist before 1.20.5 -->
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>mssqlserver</artifactId>
    <scope>test</scope>
</dependency>
```

### Setting up a network

```java
Network network = Network.newNetwork();
```

### Starting a SQL Server container as dependency

```java
MSSQLServerContainer<?> mssqlServerContainer = new MSSQLServerContainer<>(
    "mcr.microsoft.com/mssql/server:2022-CU14-ubuntu-22.04"
)
    .acceptLicense()
    .withPassword("yourStrong(!)Password")
    .withCreateContainerCmdModifier(cmd -> {
        cmd.getHostConfig().withCapAdd(Capability.SYS_PTRACE);
    })
    .withNetwork(network);
```

### Starting a Service Bus Emulator container

```java
ServiceBusEmulatorContainer emulator = new ServiceBusEmulatorContainer(
    "mcr.microsoft.com/azure-messaging/servicebus-emulator:1.1.2"
)
    .acceptLicense()
    .withConfig(MountableFile.forClasspathResource("/service-bus-config.json"))
    .withNetwork(network)
    .withMsSqlServerContainer(mssqlServerContainer);
```

### Using Azure Service Bus clients

```java
ServiceBusSenderClient senderClient = new ServiceBusClientBuilder()
    .connectionString(emulator.getConnectionString())
    .sender()
    .queueName("queue.1")
    .buildClient();

ServiceBusProcessorClient processorClient = new ServiceBusClientBuilder()
    .connectionString(emulator.getConnectionString())
    .processor()
    .queueName("queue.1")
    .processMessage(messageConsumer)
    .processError(errorConsumer)
    .buildProcessorClient();
```

### Emulator with GenericContainer (testcontainers < 1.20.5)

**Use this when the project's testcontainers version does not include `ServiceBusEmulatorContainer`.** This approach uses `GenericContainer` directly with the same emulator Docker image.

```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>mssqlserver</artifactId>
    <scope>test</scope>
</dependency>
```

```java
@Testcontainers
@Tag("Layer1")
class ServiceBusEmulatorL1Test {

    static final Network NETWORK = Network.newNetwork();

    @Container
    static final MSSQLServerContainer<?> SQL_SERVER = new MSSQLServerContainer<>(
            "mcr.microsoft.com/mssql/server:2022-CU14-ubuntu-22.04")
            .acceptLicense()
            .withPassword("yourStrong(!)Password")
            .withNetwork(NETWORK)
            .withNetworkAliases("mssql");

    @Container
    static final GenericContainer<?> SERVICE_BUS = new GenericContainer<>(
            "mcr.microsoft.com/azure-messaging/servicebus-emulator:1.1.2")
            .withExposedPorts(5672)
            .withNetwork(NETWORK)
            .withEnv("ACCEPT_EULA", "Y")
            .withEnv("MSSQL_SA_PASSWORD", "yourStrong(!)Password")
            .withEnv("SQL_SERVER", "mssql")  // network alias of the SQL Server container
            .withCopyFileToContainer(
                    MountableFile.forClasspathResource("config.json"),
                    "/ServiceBus_Emulator/ConfigFiles/config.json")
            .dependsOn(SQL_SERVER)
            .waitingFor(Wait.forLogMessage(".*Emulator Service is Successfully Up!.*", 1)
                    .withStartupTimeout(Duration.ofMinutes(3)));

    static String getConnectionString() {
        return String.format(
            "Endpoint=sb://%s:%d;SharedAccessKeyName=RootManageSharedAccessKey;"
            + "SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;",
            SERVICE_BUS.getHost(), SERVICE_BUS.getMappedPort(5672));
    }

    private ServiceBusSenderClient senderClient;
    private ServiceBusReceiverClient receiverClient;

    @BeforeAll
    static void waitForEmulator() {
        // Emulator needs extra time after port is ready for entities to initialize
        // Use Awaitility — NEVER Thread.sleep()
        Awaitility.await()
            .atMost(Duration.ofSeconds(120))
            .pollInterval(Duration.ofSeconds(2))
            .until(() -> {
                try {
                    ServiceBusSenderClient probe = new ServiceBusClientBuilder()
                        .connectionString(getConnectionString())
                        .sender().queueName("queue.1").buildClient();
                    probe.sendMessage(new ServiceBusMessage("probe"));
                    probe.close();
                    return true;
                } catch (Exception e) {
                    return false;
                }
            });
    }

    @BeforeEach
    void setupClients() {
        senderClient = new ServiceBusClientBuilder()
            .connectionString(getConnectionString())
            .sender().queueName("queue.1").buildClient();
        receiverClient = new ServiceBusClientBuilder()
            .connectionString(getConnectionString())
            .receiver().queueName("queue.1").buildClient();
    }

    @AfterEach
    void closeClients() {
        if (senderClient != null) senderClient.close();
        if (receiverClient != null) receiverClient.close();
    }
}
```

## Using Spring Cloud Azure with @ServiceConnection (Spring Boot >= 3.1)

**Requires:** Spring Boot >= 3.1, `spring-cloud-azure-testcontainers`, testcontainers >= 1.20.5.

`@ServiceConnection` is a Spring Boot 3.1+ feature. **Do NOT use this with Spring Boot 2.x — it will not compile.** For Spring Boot 2.x, see the [Spring Boot 2.x pattern](#spring-boot-2x-pattern) section.

### Maven dependencies

Pick the Spring Cloud Azure version compatible with the project's Spring Boot version. See [aka.ms/spring/versions](https://aka.ms/spring/versions) for the compatibility matrix.

| Spring Boot | Spring Cloud Azure | Notes |
|---|---|---|
| 2.x | 4.x | No `@ServiceConnection`, no `spring-cloud-azure-testcontainers`. Use `@DynamicPropertySource`. |
| 3.1.x - 3.5.x | 5.x | `@ServiceConnection` available |
| 4.0.x | 7.x | `@ServiceConnection` available |

```xml
<properties>
  <!-- Match this to your Spring Boot version per the table above -->
  <version.spring.cloud.azure>5.25.0</version.spring.cloud.azure>
</properties>

<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.azure.spring</groupId>
      <artifactId>spring-cloud-azure-dependencies</artifactId>
      <version>${version.spring.cloud.azure}</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>

<dependencies>
  <!-- Use spring-messaging-azure-servicebus for ServiceBusTemplate/ServiceBusSenderClient -->
  <dependency>
    <groupId>com.azure.spring</groupId>
    <artifactId>spring-messaging-azure-servicebus</artifactId>
  </dependency>
  <!-- OR use spring-cloud-azure-stream-binder-servicebus for Spring Cloud Stream Supplier/Consumer -->
  <!--
  <dependency>
    <groupId>com.azure.spring</groupId>
    <artifactId>spring-cloud-azure-stream-binder-servicebus</artifactId>
  </dependency>
  -->
  <dependency>
    <groupId>com.azure.spring</groupId>
    <artifactId>spring-cloud-azure-starter</artifactId>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>com.azure.spring</groupId>
    <artifactId>spring-cloud-azure-testcontainers</artifactId>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>com.microsoft.sqlserver</groupId>
    <artifactId>mssql-jdbc</artifactId>
    <scope>test</scope>
  </dependency>
</dependencies>
```

### Container setup with @ServiceConnection

`@ServiceConnection` tells Spring Boot to auto-configure `AzureServiceBusConnectionDetails` from the running container — no manual connection string wiring needed. The `MSSQLServerContainer` is NOT annotated with `@Container` because `ServiceBusEmulatorContainer.withMsSqlServerContainer()` manages its lifecycle.

```java
private static final Network NETWORK = Network.newNetwork();

private static final MSSQLServerContainer<?> SQLSERVER = new MSSQLServerContainer<>(
        "mcr.microsoft.com/mssql/server:2022-CU14-ubuntu-22.04")
        .acceptLicense()
        .withNetwork(NETWORK)
        .withNetworkAliases("sqlserver");

@Container
@ServiceConnection
private static final ServiceBusEmulatorContainer SERVICE_BUS = new ServiceBusEmulatorContainer(
        "mcr.microsoft.com/azure-messaging/servicebus-emulator:latest")
        .acceptLicense()
        .withCopyFileToContainer(MountableFile.forClasspathResource("Config.json"),
                "/ServiceBus_Emulator/ConfigFiles/Config.json")
        .withNetwork(NETWORK)
        .withMsSqlServerContainer(SQLSERVER);
```

### Spring messaging pattern (ServiceBusTemplate / ServiceBusSenderClient)

Use when the application uses `ServiceBusSenderClient` or `ServiceBusTemplate` for sending, and `ServiceBusRecordMessageListener` for processing.

```java
@SpringJUnitConfig
@TestPropertySource(properties = {
    "spring.cloud.azure.servicebus.entity-name=queue.1",
    "spring.cloud.azure.servicebus.entity-type=queue"
})
@Testcontainers
@Tag("Layer1")
class ServiceBusMessagingL1Test {

    // ... container setup as above ...

    @Autowired
    private ServiceBusSenderClient senderClient;

    @Autowired
    private ServiceBusTemplate serviceBusTemplate;

    @Test
    void senderClientCanSendAndReceiveMessage() {
        // The emulator depends on SQL Server and needs time to initialize messaging entities
        waitAtMost(Duration.ofSeconds(120)).pollInterval(Duration.ofSeconds(2)).untilAsserted(() -> {
            senderClient.sendMessage(new ServiceBusMessage("Hello World!"));
        });

        waitAtMost(Duration.ofSeconds(30)).untilAsserted(() -> {
            assertThat(Config.MESSAGES).contains("Hello World!");
        });
    }

    @Test
    void serviceBusTemplateCanSendAndReceiveMessage() {
        waitAtMost(Duration.ofSeconds(120)).pollInterval(Duration.ofSeconds(2)).untilAsserted(() -> {
            serviceBusTemplate.sendAsync("queue.1",
                MessageBuilder.withPayload("Hello from template!").build())
                .block(Duration.ofSeconds(10));
        });

        waitAtMost(Duration.ofSeconds(30)).untilAsserted(() -> {
            assertThat(Config.MESSAGES).contains("Hello from template!");
        });
    }

    @Configuration(proxyBeanMethods = false)
    @ImportAutoConfiguration(classes = {
            AzureGlobalPropertiesAutoConfiguration.class,
            AzureServiceBusAutoConfiguration.class,
            AzureServiceBusMessagingAutoConfiguration.class})
    static class Config {

        private static final Set<String> MESSAGES = ConcurrentHashMap.newKeySet();

        @Bean
        ServiceBusRecordMessageListener processMessage() {
            return context -> MESSAGES.add(context.getMessage().getBody().toString());
        }

        @Bean
        ServiceBusErrorHandler errorHandler() {
            return (context) -> { };
        }
    }
}
```

## Spring Boot 2.x Pattern

**Spring Boot 2.x does NOT support `@ServiceConnection` or `spring-boot-testcontainers`.** Use `@DynamicPropertySource` to inject the emulator connection string into the Spring context.

```java
@SpringBootTest
@ActiveProfiles("test")  // MANDATORY
@Testcontainers
@Tag("Layer1")
class MessageServiceL1Test {

    static final Network NETWORK = Network.newNetwork();

    @Container
    static final MSSQLServerContainer<?> SQL_SERVER = new MSSQLServerContainer<>(
            "mcr.microsoft.com/mssql/server:2022-CU14-ubuntu-22.04")
            .acceptLicense()
            .withPassword("yourStrong(!)Password")
            .withNetwork(NETWORK)
            .withNetworkAliases("mssql");

    @Container
    static final GenericContainer<?> SERVICE_BUS = new GenericContainer<>(
            "mcr.microsoft.com/azure-messaging/servicebus-emulator:1.1.2")
            .withExposedPorts(5672)
            .withNetwork(NETWORK)
            .withEnv("ACCEPT_EULA", "Y")
            .withEnv("MSSQL_SA_PASSWORD", "yourStrong(!)Password")
            .withEnv("SQL_SERVER", "mssql")
            .withCopyFileToContainer(
                    MountableFile.forClasspathResource("Config.json"),
                    "/ServiceBus_Emulator/ConfigFiles/Config.json")
            .dependsOn(SQL_SERVER)
            .waitingFor(Wait.forLogMessage(".*Emulator Service is Successfully Up!.*", 1)
                    .withStartupTimeout(Duration.ofMinutes(3)));

    // NO @MockBean — all beans wired from the real emulator
    @DynamicPropertySource
    static void serviceBusProperties(DynamicPropertyRegistry registry) {
        String connectionString = String.format(
            "Endpoint=sb://%s:%d;SharedAccessKeyName=RootManageSharedAccessKey;"
            + "SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;",
            SERVICE_BUS.getHost(), SERVICE_BUS.getMappedPort(5672));
        registry.add("spring.cloud.azure.servicebus.connection-string", () -> connectionString);
        registry.add("spring.cloud.azure.servicebus.namespace", () -> "sbemulatorns");
        // Disable managed identity — use the emulator connection string instead
        registry.add("spring.cloud.azure.credential.managed-identity-enabled", () -> "false");
    }

    @Autowired
    private MessageService messageService;  // The app's own service class

    @Test
    void sendMessageThroughApplicationService() {
        // ALWAYS test through the application's own classes, not the SDK directly
        Awaitility.await()
            .atMost(Duration.ofSeconds(120))
            .pollInterval(Duration.ofSeconds(2))
            .untilAsserted(() -> {
                messageService.sendMessage("test-queue", "Hello from test!");
            });
    }
}
```

## Handle ServiceBusAdministrationClient
Service Bus emulator does not support ServiceBusAdministrationClient, so for code that uses ServiceBusAdministrationClient:
- Set up Service Bus emulator
- Set up the Spring Boot configuration or Java configuration to exclude the ServiceBusAdministrationClient configuration
- Configure the ServiceBusSenderClient/ServiceBusReceiverClient/ServiceBusProcessorClient to use the connection string provided by the emulator
- Test the code

## Handle Object/Bean creation with Azure Token Credential/TokenCredential/DefaultAzureCredential
- If the object/bean is initialized using TokenCredential. 
  + If the configuration can be replaced with a Spring test config, construct the bean using connection string / key instead in the test configuration. 

    Original bean in prduction code:
    ```java
    @Bean
    public ServiceBusAdministrationClient adminClient(AzureServiceBusProperties properties, TokenCredential credential) {
        return new ServiceBusAdministrationClientBuilder()
                .credential(properties.getFullyQualifiedNamespace(), credential)
                .buildClient();
    }
    ```

    Add a test config, and construct a bean using eumulator connection string. And exclude the original configuration or bean.

    ```java
    @Configuration
    public class TestConfig {
        @Bean
        public ServiceBusAdministrationClient adminClient(String connectionString) {
        return new ServiceBusAdministrationClientBuilder()
                .connectionString(connectionString)
                .buildClient();
        }
    }
    ```

## Emulator Readiness and Retry

The Service Bus emulator takes significantly longer to start than Azurite because it depends on SQL Server initializing messaging entities. **Always use Awaitility retry/polling for initial send operations — never `Thread.sleep()`.**

```java
// Typical total time from container start to first successful send: 60-120 seconds
waitAtMost(Duration.ofSeconds(120))
    .pollInterval(Duration.ofSeconds(2))
    .untilAsserted(() -> {
        senderClient.sendMessage(new ServiceBusMessage("test"));
    });
```

## Emulator fails to start
If the emulator won't start (Docker not available, timeout, resource limits), **do NOT fall back to mocking.** Instead:
1. Increase the startup timeout (the emulator needs 60-120s)
2. Check Docker resources (emulator + SQL Server need ~4GB RAM)
3. Verify config.json is correctly mounted
4. Check the emulator logs for specific errors

## Common Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| `ClassNotFoundException: ServiceBusEmulatorContainer` | testcontainers version < 1.20.5 | Upgrade to >= 1.20.5 OR use GenericContainer approach |
| `cannot find symbol: @ServiceConnection` | Spring Boot < 3.1 | Use `@DynamicPropertySource` instead (see Spring Boot 2.x pattern) |
| `UnsatisfiedDependencyException: TokenCredential` | Custom `@Configuration` creates Azure beans without correct emulator properties | Add `@ActiveProfiles("test")` AND provide emulator connection string via `@DynamicPropertySource` so all beans connect to the real emulator |
| `ServiceBusException: Entity not found` | Emulator entities not yet initialized | Use `waitAtMost` retry pattern with Awaitility |
| `Connection refused on port 5672` | SQL Server not ready when emulator starts | Use `dependsOn(SQL_SERVER)` + `waitingFor` log message strategy |
| `Config.json not found` | Wrong mount path | Ensure `MountableFile.forClasspathResource("Config.json")` matches file in `src/test/resources/` |
| Queue/topic name mismatch | Config.json names don't match test properties | Verify `entity-name` matches Config.json `Name` field |
| `No qualifying bean of type ServiceBusSenderClient` | Missing auto-configuration imports | Add `@ImportAutoConfiguration` with `AzureGlobalPropertiesAutoConfiguration`, `AzureServiceBusAutoConfiguration`, `AzureServiceBusMessagingAutoConfiguration` |
| `Checkpointer is null` | `auto-complete` not disabled | Set `spring.cloud.stream.servicebus.bindings.<fn>-in-0.consumer.auto-complete=false` |
| `InvalidDestinationException` on context start | Test context loads production JMS `@Configuration` that connects to fake endpoint | Add `@ActiveProfiles("test")` and provide correct emulator connection properties via `@DynamicPropertySource` |
| Tests hang during context startup | `@SpringBootTest` loads full context with real Azure/DB connections | Add `@ActiveProfiles("test")` and provide all emulator properties via `@DynamicPropertySource`, or narrow context with `classes = {...}` |
