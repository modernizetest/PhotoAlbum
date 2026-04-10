---
name: migration-spring-jms-rabbitmq-servicebus
description: Migrate from RabbitMQ with JMS to Azure Service Bus for a managed messaging service with JMS API support.
---

# spring-jms-rabbitmq-servicebus

## Overview

Your job is to migrate from RabbitMQ with JMS to Azure Service Bus for a managed messaging service with JMS API support.
Below are the specific instructions for different migration tasks, please follow the instructions to complete the migration. 

## Migrate RabbitMQ ConnectionFactory

Remove RabbitMQ ConnectionFactory

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `RMQConnectionFactory`

### Instruction

Your task is to migrate a Java file using the RabbitMQ RMQConnectionFactory methods while maintaining the same functionality.
Spring JMS RabbitMQ has to define a RMQConnectionFactory bean to init connection to the rabbitmq server. In Service Bus, it automatically
provides a bean of ConnectionFactory to connect to Azure Service Bus Instance.
So you need to remove the ConnectionFactory code, reference and all the class variables used by ConnectionFactory from RabbitMQ.
The variables used by ConnectionFactory can include [host, port, username, password, virtual-host, ssl.enabled]

Below are the APIs provided for your reference:
Class: RMQConnectionFactory
  Package: com.rabbitmq.jms.admin

Important guidelines:

1. Remove RMQConnectionFactory Bean:
    - Completely remove any beans, reference, configurations and variables related to RabbitMQ RMQConnectionFactory
    - DO NOT create any Service Bus ConnectionFactory beans as replacements
    - Example of code to remove ConnectionFactory bean entirely:
      ```java
      import com.rabbitmq.jms.admin.RMQConnectionFactory;
      // ignore other imports irrelevant with jms

      @Bean
      public ConnectionFactory connectionFactory() {
          RMQConnectionFactory factory = new RMQConnectionFactory();
          factory.setHost(properties.getHost());
          factory.setPort(properties.getPort());
          factory.setUsername(properties.getUsername());
          factory.setPassword(properties.getPassword());
          factory.setVirtualHost(properties.getVirtualHost());
          factory.setSsl(properties.isSslEnabled());
          return factory;
      }
      ```
    - When other beans depend on the ConnectionFactory bean creation method, modify their method signatures to add ConnectionFactory as a parameter instead of calling the factory method directly:
      ```java
      // before
      @Bean
      public ConnectionFactory connectionFactory(){
        RMQConnectionFactory connectionFactory = new RMQConnectionFactory();
        connectionFactory.setUsername(rabbitProps.getUsername());
        connectionFactory.setPassword(rabbitProps.getPassword());
        connectionFactory.setHost(rabbitProps.getHost());
        connectionFactory.setPort(5672);
        return connectionFactory;
      }

      @Bean
      public JmsTemplate jmsTemplate() {
        return new JmsTemplate(connectionFactory());
      }

      //after
      @Bean
      public JmsTemplate jmsTemplate(ConnectionFactory connectionFactory) {
        return new JmsTemplate(connectionFactory);
      }
      ```

2. Import Cleanup:
   - All imports from packages starting with 'com.rabbitmq.jms'
   - Any other unused imports that were related to RabbitMQ



## Migrate Spring JMS RabbitMQ Destination

Migrate Spring JMS RabbitMQ Destination

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `RMQDestination`

### Instruction

Your task is to migrate the usage of RabbitMQ Destination to common JMS Destination. When there is a bean or variable
created with the type of "RMQDestination", remove the creation of RMQDestination and define a common JMS destination instance of Queue or Topic
according to the semantics of RMQDestination if the source code doesn't define it.

Below are the APIs provided for your reference:
  Class: RMQDestination
    Package: com.rabbitmq.jms.admin

  Class: Destination
    Package: jakarta.jms|javax.jms

  Class: Queue
    Package: jakarta.jms|javax.jms

  Class: Topic
    Package: jakarta.jms|javax.jms

Important guidelines:

1. Remove the creation of RMQDestination and create a JMS Destination instead when the source code doesn't create a common JMS Destination,
  when creating the common JMS Destination, you need to analyse the semantics of the original RMQDestination to decide whether a queue or topic Destination should be created:
  - Example of code that need to create the JMS Queue Destination:
    ```java
    // before for the JMS Queue case:
    @Bean
    public Queue queue() throws Exception {
      String queueName = (amqpProperties.amqpQueueName != null && !"".equals(amqpProperties.amqpQueueName)) ? amqpProperties.amqpQueueName : jmsProperties.queueName;
      Queue queue = new RMQDestination(amqpProperties.amqpExchangeName, amqpProperties.amqpExchangeName, queueName, null);
      return queue;
    }

    // after
    @Bean
    public Queue queue() throws Exception {
      Queue queue = jmsSession.createQueue(jmsProperties.queueName);
      return queue;
    }
    ```
  - Example of code that need to create the JMS Topic Destination:
    ```java
    // before for the JMS Topic case:
    @Bean
    public Topic topic() throws Exception {
      Topic topic = new RMQDestination(amqpProperties.amqpExchangeName, amqpProperties.amqpExchangeName, jmsProperties.topicName, null);
      return topic;
    }

    // after
    @Bean
    public Topic topic() throws Exception {
      Topic topic = jmsSession.createTopic(jmsProperties.topicName);
      return topic;
    }
    ```
2. Remove the creation of RMQDestination and don't need to create a JMS Destination instead when the source code already contains the logic of creating a common JMS Destination.
  - Example of code that remove the RMQDestination code entirly:
    ```java
    //before
    @Bean
    public Queue queue() throws Exception {
      Queue queue = null;
      if(amqpProperties.amqpExchangeName != null && !"".equals(amqpProperties.amqpExchangeName)) {
        String queueName = (amqpProperties.amqpQueueName != null && !"".equals(amqpProperties.amqpQueueName)) ? amqpProperties.amqpQueueName : jmsProperties.queueName;
        log.info("rmqExchangeName is set, using native RMQDestination to create MessageProducer.  queueName="+queueName+", amqpExchangeName="+amqpProperties.amqpExchangeName);
        queue = new RMQDestination(amqpProperties.amqpExchangeName, amqpProperties.amqpExchangeName, queueName, null);
      }
      else {
        log.info("Creating MessageProducer using JMS Queue obj for queueName="+jmsProperties.queueName);
        queue = jmsSession.createQueue(jmsProperties.queueName);
      }
      return queue;
    }

    //after
    @Bean
    public Queue queue() throws Exception {
      Queue queue = null;
      log.info("Creating MessageProducer using JMS Queue obj for queueName="+jmsProperties.queueName);
      queue = jmsSession.createQueue(jmsProperties.queueName);
      return queue;
    }
    ```

3. Import Cleanup:
   - All imports from packages starting with 'com.rabbitmq.jms'
   - Any other unused imports that were related to RabbitMQ



## Migrate Spring JMS RabbitMQ properties

Migrate Spring JMS RabbitMQ properties to Spring Cloud Azure Service Bus JMS properties

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.{yml,yaml,properties}`
- Regex pattern to find code lines: `.*`

### Instruction

Your task is to add Service Bus JMS connection settings only when the application uses Spring JMS with RabbitMQ, to be more specificlly, when there are explicit calling of the class com.rabbitmq.jms.admin.RMQConnectionFactory.
Step 1. Search codebase to see whether the application uses `RMQConnectionFactory` or not.
Step 2. If the application uses RMQConnectionFactory, then add Service Bus connection settings if the application uses RMQConnectionFactory.
Step 3. If there is no explicit call of class RMQConnectionFactory, then this knowledge doesn't apply for this project and please directly end applying it.
*DO NOT* optimize the code blocks not directly related to the migration changes, *KEEP* those commented out code, minimize the amount of code changes.
*DO NOT* modify any existing properties even though they are related for RabbitMQ, AMQP or JMS.
*Do* create the configuration property file if the project doesn't have one and add below settings.

Service Bus connection settings:
  - managed-identity-enabled
    property: spring.cloud.azure.credential.managed-identity-enabled
    value: true
  - client-id
    property: spring.cloud.azure.credential.client-id
    value: ${AZURE_CLIENT_ID}
  - pricing-tier
    property: spring.jms.servicebus.pricing-tier
    value: premium
  - namespace
    property: spring.jms.servicebus.namespace
    value: ${SERVICE_BUS_NAMESPACE}
  - passwordless-enabled
    property: spring.jms.servicebus.passwordless-enabled
    value: true



## Migrate Spring JMS RabbitMQ dependencies

Change dependencies (pom.xml for maven dependency or build.gradle or build.gradle.kts for gradle dependency) for Spring Cloud Azure Service Bus JMS support

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/{pom.xml,build.gradle,build.gradle.kts}`
- Regex pattern to find code lines: `rabbitmq-jms`

### Instruction

In pom.xml or build.gradle or build.gradle.kts: when the com.rabbitmq.jms:rabbitmq-jms library exists and either of spring-jms or spring-boot-starter-jms exists, then remove the RabbitMQ and Spring JMS dependencies with artifactId in [rabbitmq-jms, spring-boot-starter-jms, spring-jms]. 
Add the required dependencies for the Spring Cloud Azure Service Bus JMS.
Only update the lines related to JMS RabbitMQ, Spring JMS and Service Bus, don't modify other lines and keep the changes minimized.

Note: Delete the rabbitmq and spring jms dependency blocks, do not comment out.

Add the Azure Service Bus dependencies:
1. Managed dependency:
  groupId: com.azure.spring
  artifactId: spring-cloud-azure-dependencies
  version: 5.22.0
  scope: import
  type: pom
  Note:
    - If the code is using Spring Boot 2.x, be sure to set the spring-cloud-azure-dependencies version to 4.19.0. If the code is using Spring Boot 3.x, Please check the latest version of the dependency, and update the version if possible.
    - Define a new property named spring-cloud-azure.version for spring-cloud-azure-dependencies.
    - This Bill of Material (BOM) should be configured in the <dependencyManagement> section for pom.xml
    - This Bill of Material (BOM) should be imported with the "platform" keyword for build.gradle or build.gradle.kts files. 
2. Dependencies:
  groupId: com.azure.spring
  artifactId: spring-cloud-azure-starter-servicebus-jms