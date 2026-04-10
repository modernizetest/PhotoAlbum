---
name: migration-kafka-to-eventhubs
description: Migrate from Kafka to Azure Event Hubs for Apache Kafka with managed identity for secure, credential-free authentication.
---

# kafka-to-eventhubs

## Overview

Migrate from Apache Kafka to Azure Event Hubs for Apache Kafka using passwordless connections via managed identity.

## Instructions

1. Add the Spring Cloud Azure BOM and starter alongside existing Kafka dependencies:
   - BOM: `com.azure.spring:spring-cloud-azure-dependencies` (version `5.22.0` for Spring Boot 3.x, `4.19.0` for Spring Boot 2.x)
   - Dependency: `com.azure.spring:spring-cloud-azure-starter`

2. Replace Kafka bootstrap server values with the Azure Event Hubs namespace endpoint: `spring.kafka.bootstrap-servers=$AZ_EVENTHUBS_NAMESPACE_NAME.servicebus.windows.net:9093`.

3. Make sure you do not introduce non-existing classes