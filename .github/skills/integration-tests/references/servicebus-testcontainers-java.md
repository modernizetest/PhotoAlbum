# Azure Service Bus Emulator

Based on "org.testcontainers:testcontainers-azure:2.0.2":

## Configuring the Azure Service Bus Emulator container

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
                "Topics": []
            }
        ],
        "Logging": {
            "Type": "File"
        }
    }
}
```

## Start Azure Service Bus Emulator during a test

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

## Using Azure Service Bus clients

Configure the sender and the processor clients:

### Configuring the sender client

```java
ServiceBusSenderClient senderClient = new ServiceBusClientBuilder()
    .connectionString(emulator.getConnectionString())
    .sender()
    .queueName("queue.1")
    .buildClient();
```

### Configuring the processor client

```java
ServiceBusProcessorClient processorClient = new ServiceBusClientBuilder()
    .connectionString(emulator.getConnectionString())
    .processor()
    .queueName("queue.1")
    .processMessage(messageConsumer)
    .processError(errorConsumer)
    .buildProcessorClient();
```

