---
name: migration-spring-jms-rabbitmq-servicebus
description: Migrates Java Spring Boot applications from RabbitMQ JMS messaging to Azure Service Bus JMS. Replaces RabbitMQ JMS dependencies with Spring Cloud Azure Service Bus JMS starter and updates connection configuration. Use when migrating Spring JMS applications from RabbitMQ to Azure Service Bus, replacing RMQConnectionFactory, or modernizing JMS messaging to Azure.
---

Migrate a Spring JMS application from RabbitMQ to Azure Service Bus.

## Migrate dependencies
1. Remove the dependencies used for using RabbitMQ via Spring JMS. For example: rabbitmq-jms, spring-boot-starter-jms, spring-jms.
2. Use spring-cloud-azure-dependencies (bom) to manage the Spring Cloud Azure dependency version. Choose a version of spring-cloud-azure-dependencies that is compatible with your Spring Boot version:
    - For projects using spring-boot:2.x, spring-cloud-azure-dependencies' version should >= `4.20.0` and < `5.0.0`.
    - For projects using spring-boot:3.x, spring-cloud-azure-dependencies' version should >= `5.22.0` and < `7.0.0`.
    - For projects using spring-boot:4.x, spring-cloud-azure-dependencies' version should >= `7.1.0`.
3. Add a new dependency: com.azure.spring:spring-cloud-azure-starter-servicebus-jms.
4. Only update the lines related to JMS RabbitMQ, Spring JMS and Service Bus, don't modify other lines and keep the changes minimal.

## Migrate properties
1. Locate the configuration file (e.g., `application.properties` or `application.yml`); create one if it does not exist.
2. Remove RabbitMQ JMS properties.
3. Add Azure Service Bus JMS properties. Example:
    ```diff
    +spring:
    +  cloud:
    +    azure:
    +      credential:
    +        managed-identity-enabled: true
    +        client-id: ${AZURE_CLIENT_ID}
    +  jms:
    +    servicebus:
    +      pricing-tier: premium
    +      namespace: ${SERVICE_BUS_NAMESPACE}
    +      passwordless-enabled: true
    ```

## Migrate Java Code

### Migrate RabbitMQ JMS ConnectionFactory to Service Bus Configuration
1. Search for Java files that use `RMQConnectionFactory` (class: `com.rabbitmq.jms.admin.RMQConnectionFactory`).
2. Remove any `RMQConnectionFactory` bean definitions and all related variables (e.g., host, port, username, password, virtual-host, ssl.enabled). Service Bus auto-provides a `ConnectionFactory` bean, so do **not** create a replacement.
3. Refactor code that depends on the removed `RMQConnectionFactory`:
    3.1. If other beans depend on the removed bean method, change them to accept `ConnectionFactory` as a parameter. Example:
        ```diff
        -import com.rabbitmq.jms.admin.RMQConnectionFactory;
        -
        -@Bean
        -public ConnectionFactory connectionFactory(){
        -  RMQConnectionFactory connectionFactory = new RMQConnectionFactory();
        -  connectionFactory.setUsername(rabbitProps.getUsername());
        -  connectionFactory.setPassword(rabbitProps.getPassword());
        -  connectionFactory.setHost(rabbitProps.getHost());
        -  connectionFactory.setPort(5672);
        -  return connectionFactory;
        -}
        -
        -@Bean
        -public JmsTemplate jmsTemplate() {
        -  return new JmsTemplate(connectionFactory());
        -}
        +@Bean
        +public JmsTemplate jmsTemplate(ConnectionFactory connectionFactory) {
        +  return new JmsTemplate(connectionFactory);
        +}
        ```
    3.2. If a method creates a new `RMQConnectionFactory` directly, change it to inject the auto-configured `ConnectionFactory` bean instead.
        ```diff
        -import com.rabbitmq.jms.admin.RMQConnectionFactory;
        -
        -@Bean
        -public Connection jmsConnection() {
        -  RMQConnectionFactory connectionFactory = new RMQConnectionFactory();
        -  connectionFactory.setUsername("user");
        -  connectionFactory.setPassword("pass");
        -  connectionFactory.setHost("localhost");
        -  connectionFactory.setPort(5672);
        -  try {
        -    Connection conn = connectionFactory.createConnection();
        -    return conn;
        -  } catch (JMSException ex) { ... }
        -  return null;
        -}
        +@Bean
        +public Connection jmsConnection(ConnectionFactory connectionFactory) throws JMSException {
        +  Connection conn = connectionFactory.createConnection();
        +  conn.start();
        +  return conn;
        +}
        ```

### Migrate RabbitMQ Destination to Common JMS Destination
1. Search for Java files that use `RMQDestination` (class: `com.rabbitmq.jms.admin.RMQDestination`).
2. Replace each `RMQDestination` with a standard JMS `Queue` or `Topic` creation using `session.createQueue(queueName)` or `session.createTopic(topicName)`, based on the semantics of the original destination. Preserve the queue/topic name from the original `RMQDestination` (e.g., the value passed to `setAmqpQueueName()` or `setDestinationName()`) and use it in the replacement `session.createQueue()`/`session.createTopic()` call. If no `Session` bean exists in the codebase, create one from the auto-configured `ConnectionFactory`. Example:
    ```diff
    -import com.rabbitmq.jms.admin.RMQDestination;
    -
    +@Bean(destroyMethod = "close")
    +public Connection jmsConnection(ConnectionFactory connectionFactory) throws JMSException {
    +  Connection connection = connectionFactory.createConnection();
    +  connection.start();
    +  return connection;
    +}
    +
    +@Bean
    +public Session jmsSession(Connection jmsConnection) throws JMSException {
    +  return jmsConnection.createSession(false, Session.AUTO_ACKNOWLEDGE);
    +}
    +
     @Bean
    -public Queue queue() {
    -  RMQDestination destination = new RMQDestination();
    -  destination.setAmqpQueueName("my-queue");
    -  destination.setDestinationName("my-queue");
    -  return destination;
    +public Queue queue(Session jmsSession) throws JMSException {
    +  return jmsSession.createQueue("my-queue");
     }
    ```
3. If the code already contains a fallback path that creates a common JMS Destination (e.g., `jmsSession.createQueue()`), remove the `RMQDestination` branch entirely and keep only the standard JMS path. Example:
    ```diff
    -import com.rabbitmq.jms.admin.RMQDestination;
    -
     @Bean
     public Queue queue() throws Exception {
    -  Queue queue = null;
    -  if(amqpProperties.amqpExchangeName != null && !"".equals(amqpProperties.amqpExchangeName)) {
    -    String queueName = (amqpProperties.amqpQueueName != null && !"".equals(amqpProperties.amqpQueueName)) ? amqpProperties.amqpQueueName : jmsProperties.queueName;
    -    queue = new RMQDestination(amqpProperties.amqpExchangeName, amqpProperties.amqpExchangeName, queueName, null);
    -  }
    -  else {
    -    queue = jmsSession.createQueue(jmsProperties.queueName);
    -  }
    +  Queue queue = jmsSession.createQueue(jmsProperties.queueName);
       return queue;
     }
    ```

### Clean up

1. Rename classes, files, packages, variables, and properties referencing "RabbitMQ" to "ServiceBus".
2. Remove unused imports, methods, variables, and files left over from the migration.
