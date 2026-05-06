---
name: migration-kafka-to-eventhubs
description: Migrates Java applications from Kafka to Azure Event Hubs for Kafka with managed identity for secure, passwordless authentication. Updates Spring Cloud Azure dependencies, Kafka connection settings, and authentication configuration. Use when migrating Java Kafka producers or consumers to Azure Event Hubs, or enabling managed identity authentication for event streaming.
---

## Migration Steps

1. Add Spring Cloud Azure Starter when the project is using a Spring dependency of Kafka to establish the passwordless connections with Azure Event Hubs for Kafka
    - Use spring-cloud-azure-dependencies (bom) to manage the Spring Cloud Azure dependency version. Choose a version of spring-cloud-azure-dependencies that is compatible with your Spring Boot version:
        - For projects using spring-boot:2.x, spring-cloud-azure-dependencies' version should >=`4.20.0` and < `5.0.0`.
        - For projects using spring-boot:3.x, spring-cloud-azure-dependencies' version should >= `5.22.0` and < `7.0.0`.
        - For projects using spring-boot:4.x, spring-cloud-azure-dependencies' version should >=`7.1.0`.
    - Add dependency: com.azure.spring:spring-cloud-azure-starter

2. Update Kafka server configuration to use passwordless connections with Azure Event Hubs. 
    Replace existing Kafka bootstrap server values with the Azure Event Hubs namespace endpoint using port 9093:
    - Spring Kafka configurations:
        - spring.kafka.bootstrap-servers=$AZ_EVENTHUBS_NAMESPACE_NAME.servicebus.windows.net:9093
        - spring.kafka.consumer.bootstrap-servers=$AZ_EVENTHUBS_NAMESPACE_NAME.servicebus.windows.net:9093
        - spring.kafka.producer.bootstrap-servers=$AZ_EVENTHUBS_NAMESPACE_NAME.servicebus.windows.net:9093
        - spring.kafka.admin.bootstrap-servers=$AZ_EVENTHUBS_NAMESPACE_NAME.servicebus.windows.net:9093
    - Spring Cloud Stream configurations:
        - spring.cloud.stream.kafka.binder.brokers=$AZ_EVENTHUBS_NAMESPACE_NAME.servicebus.windows.net:9093
    - Native Kafka SDK configurations:
        - bootstrap.servers=$AZ_EVENTHUBS_NAMESPACE_NAME.servicebus.windows.net:9093
    If no explicit bootstrap server configuration exists but other Kafka properties are present, add the appropriate configuration based on the framework in use. Format the property according to the configuration file type (.properties or YAML).
