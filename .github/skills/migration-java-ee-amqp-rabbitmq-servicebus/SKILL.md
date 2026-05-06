---
name: migration-java-ee-amqp-rabbitmq-servicebus
description: Migrates Java EE/Jakarta EE applications from RabbitMQ AMQP messaging to Azure Service Bus SDK. Replaces RabbitMQ client dependencies, migrates publishers and consumers, updates connection management, and maps RabbitMQ concepts (exchanges, queues) to Service Bus equivalents (topics, subscriptions). Use when migrating Java EE or Jakarta EE applications from RabbitMQ to Azure Service Bus.
---

## Migration Scope

This guide focuses **exclusively** on migrating Java EE/Jakarta EE applications from RabbitMQ messaging to Azure Service Bus.

### What is Included:
- RabbitMQ AMQP client dependency replacement with Azure Service Bus SDK
- Java code migration (publishers, consumers, connection management)
- Message broker concept mapping (exchanges to topics, queues to subscriptions)
- Configuration file updates for connection strings and messaging properties
- Build file dependency updates (Maven POM, Gradle build files)
- Message acknowledgment pattern migration (basicAck to complete/abandon)
- Connection factory and channel management refactoring
- Message routing and delivery callback implementations
- Spring XML and properties file configuration updates

### What is NOT Included:
- **Other message brokers**: This guide does not cover migration from other messaging systems (e.g., Apache Kafka, ActiveMQ, Amazon SQS, etc.)
- **External service dependencies**: Any integrations with compute services, database systems, storage services, or other cloud/third-party services should be handled by their respective migration guides
- **Infrastructure and deployment**: Infrastructure-as-code, CI/CD pipelines, and deployment configurations are out of scope
- **Message content transformation**: Changes to message formats, serialization, or business logic are not covered
- **Azure Service Bus infrastructure setup**: Creating Service Bus namespaces, queues, topics, and access policies in Azure

**Important**: This guide only handles the application's RabbitMQ client code and configuration. If your application uses other services, those integrations must be migrated separately using their dedicated migration guides.
