---
name: migration-activemq-servicebus
description: Migrates Java Spring Boot applications from ActiveMQ JMS messaging to Azure Service Bus JMS. Replaces ActiveMQ dependencies with Spring Cloud Azure Service Bus JMS starter and updates connection configuration. Use when migrating Spring JMS applications from ActiveMQ to Azure Service Bus or modernizing on-premises messaging to Azure.
---

## Migration Steps

1. Update build configuration file.
    - Remove the Spring JMS ActiveMQ dependencies with artifactId in [spring-boot-starter-activemq, activemq-broker].
    - Use spring-cloud-azure-dependencies (bom) to manage the Spring Cloud Azure dependency version.bChoose a version of spring-cloud-azure-dependencies that is compatible with your Spring Boot version:
        - For projects using spring-boot:2.x, spring-cloud-azure-dependencies' version should >=`4.20.0` and < `5.0.0`.
        - For projects using spring-boot:3.x, spring-cloud-azure-dependencies' version should >= `5.22.0` and < `7.0.0`.
        - For projects using spring-boot:4.x, spring-cloud-azure-dependencies' version should >=`7.1.0`.
    - Add dependency: com.azure.spring:spring-cloud-azure-starter-servicebus-jms.

2. Update properties.
    Migrate the ActiveMQ connection settings to Service Bus connection settings. Please follow these guidelines:
    - **DO NOT** optimize the code blocks that are not directly related to the migration changes.
    - **KEEP** the commented-out code and minimize the amount of code changes.
    1. **Add Service Bus Connection Settings:**
        - For properties starting with `spring.activemq` and named `broker-url`, `username`, or `password`:
          - Add the following Service Bus connection settings:
            - Managed Identity Enabled:
              - Property: `spring.cloud.azure.credential.managed-identity-enabled`
              - Value: `true`
            - Client ID:
              - Property: `spring.cloud.azure.credential.client-id`
              - Value: `${AZURE_CLIENT_ID}`
            - Namespace:
              - Property: `spring.jms.servicebus.namespace`
              - Value: `${SERVICE_BUS_NAMESPACE}`
            - Pricing Tier:
              - Property: `spring.jms.servicebus.pricing-tier`
              - Value: `${PRICING_TIER}`
            - Passwordless Enabled:
              - Property: `spring.jms.servicebus.passwordless-enabled`
              - Value: `true`
          - Remove the ActiveMQ connection properties that match `spring.activemq.{broker-url, username, password}`.
    2. **Replace ActiveMQ Resource Settings:**
        - Find properties with the keyword `activemq` in their names and replace `activemq` with `servicebus`.
    3. **Update Comments:**
        - Replace the string `activemq` with `Service Bus` in commented-out lines.
    4. **Update Docker Compose Files:**
        - If the file is a docker-compose file and contains a container starting with ActiveMQ images, remove the ActiveMQ container and related usages.

3. Update Java code.
  Your task is to migrate a Java file from using the ActiveMQ ConnectionFactory methods to the Azure Service Bus while maintaining the same functionality.
  ActiveMQ uses ConnectionFactory to init connection to the ActiveMQ server. In Service Bus scenario, we use Managed Identity and environment variables to auto connect to Azure Service Bus Instance.
  Remove the ConnectionFactory code and all the class variables used by ConnectionFactory.
  The variables includes [broker-url, username, password]
  Important guidelines:
    1. ConnectionFactory Bean Removal:
        - Completely remove any beans, configurations and variables related to ActiveMQ ConnectionFactory
        - DO NOT create any Service Bus connection beans as replacements
        - Azure Service Bus uses auto-configuration with Managed Identity, so no explicit connection beans are required
        - Example of code to remove entirely:
          ```java
          // before
          @Bean
          public ActiveMQConnectionFactory activeMQConnectionFactory() {
              return new ActiveMQConnectionFactory(user, password, brokerUrl);
          }
          @Bean
          public DefaultJmsListenerContainerFactory jmsListenerContainerFactory() {
              DefaultJmsListenerContainerFactory factory = new DefaultJmsListenerContainerFactory();
              factory.setConnectionFactory(activeMQConnectionFactory());
              factory.setConcurrency("50");

              return factory;
          }

          //after
          @Bean
          public DefaultJmsListenerContainerFactory jmsListenerContainerFactory(ConnectionFactory connectionFactory) {
              DefaultJmsListenerContainerFactory factory = new DefaultJmsListenerContainerFactory();
              factory.setConnectionFactory(connectionFactory);
              factory.setConcurrency("50");

              return factory;
          }
          ```
    2. Import Cleanup:
        - Remove all AMQP-related imports after migration
        - All imports from packages starting with 'org.apache.activemq'
        - Any other unused imports that were related to ActiveMQ
    Remember to maintain the same functionality while removing ActiveMQ-specific code. The Azure Service Bus auto-configuration will handle connection management.
    Below are the key information of the rabbitmq and service bus classes, interfaces and annotations for your reference:
    Interface: ConnectionFactory
      Package: javax.jms.ConnectionFactory
