# Azure Event Hubs Emulator TestContainers Coding Reference

## Contents
- 1. MANDATORY - Choose Approach based on Spring/non-Spring, Spring Boot version, TestContainers version
- 2. MANDATORY - Scan all event hubs before writing code
- 3. DO NOT mock
- 4. Example of Event Hubs Emulator config.json
- 5. Spring Cloud Azure Version Compatibility
- 6. Emulator with EventHubsEmulatorContainer (testcontainers >= 1.20.5)
  + Setting up a network
  + Starting a SQL Server container as dependency
  + Starting a Event Hubs Emulator container
  + Using Azure Event Hubs clients
- 7. Emulator with GenericContainer (testcontainers < 1.20.5)
- 8. Using Spring Cloud Azure with @ServiceConnection (Spring Boot >= 3.1)
  + Container setup with @ServiceConnection
- 9. Spring Boot 2.x Pattern
- 10. Connection String to the Emulator/TestContainers
- You can reference https://learn.microsoft.com/en-us/azure/event-hubs/test-locally-with-event-hub-emulator for more info.

## MANDATORY - Choose Approach based on Spring/non-Spring, Spring Boot version, TestContainers version

**You MUST check the project's testcontainers and Spring Boot versions BEFORE writing any Event Hubs test code.** Using the wrong approach wastes significant time on compilation and runtime failures that are impossible to fix.

- If Spring Boot **>= 3.1**, use `@ServiceConnection` for auto-wiring: [Using Spring Cloud Azure with @ServiceConnection](#using-spring-cloud-azure-with-serviceconnection-spring-boot--31)
- If Spring Boot **2.x**, use `@DynamicPropertySource` — `@ServiceConnection` is NOT available: [Spring Boot 2.x pattern](#spring-boot-2x-pattern)
- If testcontainers **>= 1.20.5**, use `EventHubsEmulatorContainer` from `org.testcontainers:azure`: [Emulator with EventHubsEmulatorContainer](#emulator-with-eventhubsemulatorcontainer-testcontainers--1205)
- If testcontainers **< 1.20.5**, use `GenericContainer` with the emulator Docker image: [Emulator with GenericContainer](#emulator-with-genericcontainer-testcontainers--1205)

**CRITICAL: `EventHubsEmulatorContainer` does NOT exist in testcontainers before 1.20.5.** If you see `ClassNotFoundException` or `cannot find symbol: class EventHubsEmulatorContainer`, the project's testcontainers version is too old. Switch to the GenericContainer approach or upgrade testcontainers. The Maven artifact is `org.testcontainers:azure` (NOT `testcontainers-azure`).

## MANDATORY - Scan all event hubs before writing code
The event hubs cannot be created on the fly, so they should be created before the application starts. So every such resource need to be declared in the config.json. So scan the project to see what event hubs need to be declared. And then define them in config.json.

## Do NOT mock
**NEVER MOCK** the `EventHubConsumerClient`, `EventHubProducerClient`, `EventHubProcessorClient` or **ANY bean related to the migrated service.**

## Example of Event Hubs Emulator config.json
Place this file at `src/test/resources/config.json`:

```json
{
  "UserConfig": {
    "NamespaceConfig": [
      {
        "Type": "EventHub",
        "Name": "emulatorNs1",
        "Entities": [
          {
            "Name": "eh1",
            "PartitionCount": "2",
            "ConsumerGroups": [
              {
                "Name": "cg1"
              }
            ]
          }
        ]
      }
    ],
    "LoggingConfig": {
      "Type": "File"
    }
  }
}
```

## Spring Cloud Azure Version Compatibility

Pick the Spring Cloud Azure version compatible with the project's Spring Boot version. See [aka.ms/spring/versions](https://aka.ms/spring/versions) for the compatibility matrix.

| Spring Boot | Spring Cloud Azure | Notes |
|---|---|---|
| 2.x | 4.x | No `@ServiceConnection`, no `spring-cloud-azure-testcontainers`. Use `@DynamicPropertySource`. |
| 3.1.x - 3.5.x | 5.x | `@ServiceConnection` available |
| 4.0.x | 7.x | `@ServiceConnection` available |

## Emulator with EventHubsEmulatorContainer (testcontainers >= 1.20.5)

**Requires: `org.testcontainers:azure` version >= 1.20.5**

```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>azure</artifactId>
    <version>2.0.1</version><!-- or newer; class does NOT exist before 1.20.5 -->
    <scope>test</scope>
</dependency>
```

### Starting a Event Hubs Emulator container

```java
Network network = Network.newNetwork();
AzuriteContainer azurite = new AzuriteContainer("mcr.microsoft.com/azure-storage/azurite:3.33.0")
    .withNetwork(network);
azurite.start();

var eventHubs = new EventHubsEmulatorContainer("mcr.microsoft.com/azure-messaging/eventhubs-emulator:2.0.1")
   .acceptLicense()
   .withNetwork(network)
   .withAzuriteContainer(azurite);
eventHubs.start();
```

### Using Azure Event Hubs clients

```java
EventHubProducerClient producer = new EventHubClientBuilder()
    .connectionString(emulator.getConnectionString())
    .fullyQualifiedNamespace("emulatorNs1")
    .eventHubName("your-eventhub-name")
    .buildProducerClient();
EventHubConsumerClient consumer = new EventHubClientBuilder()
    .connectionString(emulator.getConnectionString())
    .fullyQualifiedNamespace("emulatorNs1")
    .eventHubName("your-eventhub-name")
    .consumerGroup("your-consumer-group")
    .buildConsumerClient();
```

## Emulator with GenericContainer (testcontainers < 1.20.5)

**Use this when the project's testcontainers version does not include `EventHubsEmulatorContainer`.** This approach uses `GenericContainer` directly with the same emulator Docker image.

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
```

```java
@Testcontainers
@Tag("Layer1")
class EventHubsEmulatorL1Test {

    static final Network NETWORK = Network.newNetwork();

    @Container
    static finalGenericContainer<?> AZURITE = new GenericContainer<>(DockerImageName.parse("mcr.microsoft.com/azure-storage/azurite:latest"))
        .withNetwork(network)
        .withNetworkAliases("azurite") // Emulator looks for this alias by default
        .withExposedPorts(10000, 10001, 10002);
      AZURITE.start();


    @Container
    static final GenericContainer<?> EventHubs = new GenericContainer<>(
            "mcr.microsoft.com/azure-messaging/eventhubs-emulator:latest")
            .withNetwork(NETWORK)
            .withExposedPorts(5672)            
            .withEnv("ACCEPT_EULA", "Y")
            .withEnv("BLOB_SERVER", "azurite")
            .withEnv("METADATA_SERVER", "azurite")
            .withCopyFileToContainer(
                    MountableFile.forClasspathResource("config.json"),
                    "/Eventhubs_Emulator/ConfigFiles/Config.json") // the target file should be uppercase
            .dependsOn(AZURITE)
            .waitingFor(Wait.forLogMessage(".*Emulator Service is Successfully Up!.*", 1)
                    .withStartupTimeout(Duration.ofMinutes(3)));

    EventHubs.start();                

    static String getConnectionString() {
        return String.format(
            "Endpoint=sb://%s:%d;SharedAccessKeyName=RootManageSharedAccessKey;"
            + "SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;",
            SERVICE_BUS.getHost(), SERVICE_BUS.getMappedPort(5672));
    }
}
```

## Using Spring Cloud Azure with @ServiceConnection (Spring Boot >= 3.1)

**Requires:** Spring Boot >= 3.1, `spring-cloud-azure-testcontainers`, testcontainers >= 1.20.5.

`@ServiceConnection` is a Spring Boot 3.1+ feature. **Do NOT use this with Spring Boot 2.x — it will not compile.** For Spring Boot 2.x, see the [Spring Boot 2.x pattern](#spring-boot-2x-pattern) section.

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
  <!-- Use spring-messaging-azure-eventhubs for EventHubsTemplate/EventHubsProducerClient -->
  <dependency>
    <groupId>com.azure.spring</groupId>
    <artifactId>spring-messaging-azure-eventhubs</artifactId>
  </dependency>
  <!-- OR use spring-cloud-azure-stream-binder-eventhubs for Spring Cloud Stream Supplier/Consumer -->
  <!--
  <dependency>
    <groupId>com.azure.spring</groupId>
    <artifactId>spring-cloud-azure-stream-binder-eventhubs</artifactId>
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
</dependencies>
```

### Container setup with @ServiceConnection

`@ServiceConnection` tells Spring Boot to auto-configure `AzureEventHubsConnectionDetails` from the running container — no manual connection string wiring needed.


## Spring Boot 2.x Pattern

**Spring Boot 2.x does NOT support `@ServiceConnection` or `spring-boot-testcontainers`.** Use `@DynamicPropertySource` to inject the emulator connection string into the Spring context.


## Connection String to the Emulator/TestContainers
If connection string must be constructed by yourself:

- When the emulator container and interacting application are running natively on local machine, use following connection string:
```
"Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
```