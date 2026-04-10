---
name: migration-activemq-servicebus
description: Migrate from ActiveMQ Artemis to Azure Service Bus for messaging.
---

# activemq-servicebus

## Overview

Your job is to migrate from ActiveMQ Artemis to Azure Service Bus for messaging.
Below are the specific instructions for different migration tasks, please follow the instructions to complete the migration. 

## Migrate ActiveMQ ConnectionFactory

Remove ActiveMQ ConnectionFactory

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `org.apache.activemq.`

### Instruction

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



## Migrate ActiveMQ properties

Migrate ActiveMQ properties to Azure Service Bus properties

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.{yml,yaml,properties}`
- Regex pattern to find code lines: `(?i)activemq`

### Instruction

Your task is to migrate the ActiveMQ connection settings to Service Bus connection settings. Please follow these guidelines:

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



## Migrate ActiveMQ dependencies

Change dependencies (pom.xml for maven dependency or build.gradle or build.gradle.kts for gradle dependency) for Azure Service Bus with Spring JMS support

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/{pom.xml,build.gradle,build.gradle.kts}`
- Regex pattern to find code lines: `(spring-boot-starter-activemq|activemq-broker)`

### Instruction

In pom.xml or build.gradle or build.gradle.kts: Remove the Spring JMS ActiveMQ dependencies. Add the required dependencies for the Spring Cloud Azure Service Bus with Spring JMS.
Only update the lines related to ActiveMQ or Service Bus, don't modify other lines and keep the changes minimized.

Remove the ActiveMQ dependencies with artifactId in [spring-boot-starter-activemq, activemq-broker]
Note: Delete the ActiveMQ dependency blocks, do not comment out.

Add the Azure Service Bus dependencies:
1. Managed dependency:
  groupId: com.azure.spring
  artifactId: spring-cloud-azure-dependencies
  version: 5.22.0
  scope: import
  type: pom
  Note:
    - If the code is using Spring Boot 2.x, be sure to set the spring-cloud-azure-dependencies version to 4.20.0. If the code is using Spring Boot 3.x, Please check the latest version of the dependency, and update the version if possible.
    - Define a new property named spring-cloud-azure.version for spring-cloud-azure-dependencies.
    - This Bill of Material (BOM) should be configured in the <dependencyManagement> section for pom.xml
    - This Bill of Material (BOM) should be imported with the "platform" keyword for build.gradle or build.gradle.kts files. 
2. Dependencies:
  -
  groupId: com.azure.spring
  artifactId: spring-cloud-azure-starter-servicebus-jms