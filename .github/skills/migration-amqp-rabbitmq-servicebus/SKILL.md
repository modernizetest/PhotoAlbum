---
name: migration-amqp-rabbitmq-servicebus
description: Migrate from RabbitMQ with AMQP to Azure Service Bus for messaging.
---

# amqp-rabbitmq-servicebus

## Overview

Your task is to migrate from RabbitMQ with AMQP to Azure Service Bus for messaging.
Below are the specific instructions for different migration tasks, please follow the instructions to complete the migration. 

## Knowledge Base Content

* Title: Migrate RabbitMQ properties
* Description: Migrate RabbitMQ properties to Azure Service Bus properties in Spring Messaging
* Content: 
## Migrate RabbitMQ ConnectionFactory

Migrate RabbitMQ ConnectionFactory logic

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `rabbit\.connection\.`

### Instruction

Your task is to migrate the java code from using RabbitMQ ConnectionFactory methods to the Azure Service Bus while maintaining the same functionality.
RabbitMQ uses ConnectionFactory to init connection to the rabbitmq server. In Service Bus scenario, we use Managed Identity and environment variables to auto connect to Azure Service Bus Instance.
Remove the ConnectionFactory related code including the Spring Bean, class member and variables.
The variables includes [host, port, username, password, virtual-host, ssl.enabled]

Important guidelines:

1. ConnectionFactory Bean Removal:
   - Completely remove any beans, class members and variables of the RabbitMQ ConnectionFactory type.
   - DO NOT create the Service Bus connection factory bean as replacement since the underlying Azure Service Bus library provides auto-configuration for it.
   - Example of code to remove entirely:
     ```java
     @Bean
     public ConnectionFactory connectionFactory() {
         CachingConnectionFactory connectionFactory = new CachingConnectionFactory();
         connectionFactory.setHost(rabbitMQHost);
         connectionFactory.setPort(rabbitMQPort);
         connectionFactory.setUsername(rabbitMQUsername);
         connectionFactory.setPassword(rabbitMQPassword);
         connectionFactory.setVirtualHost(rabbitMQVirtualHost);
         return connectionFactory;
     }
     ```

2. Import Cleanup:
   - Remove all AMQP-related imports after migration
   - All imports from packages starting with 'org.springframework.amqp'
   - All imports from packages starting with 'com.rabbitmq'
   - Any other unused imports that were related to RabbitMQ

Remember to maintain the same functionality while removing RabbitMQ-specific code. The Azure Service Bus auto-configuration will handle connection management.



## Migrate RabbitMQ Listener

Migrate RabbitMQ Listener to Azure Service Bus Listener

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `RabbitListener|RabbitHandler|EnableRabbit|AmqpHeaders`

### Instruction

Your task is to migrate a Java file from using the RabbitMQ listener methods to the Azure Service Bus listener methods while maintaining the same functionality.
Migrate the messaging listeners follow the items one by one:
  - Remove annotation @EnableRabbit.
  - Change annotation @RabbitListener to @ServiceBusListener and add a new annotation @EnableAzureMessaging to the class.
  - Update @ServiceBusListener parameters based on the RabbitMQ topology from the dependency file by checking Spring Beans of RabbitMQ queues, exchanges and bindings, and collect names of RabbitMQ resources before migration.
    - If there are only Beans of org.springframework.amqp.core.Queue without any Exchange or Binding, then this is a queue topology that the RabbitMQ Queue name should be migrated to Service Bus Queue name. You should migrate the "queues" parameter of RabbitListener to "@ServiceBusListener(destination=<queue name>)".
    - If there are Beans of org.springframework.amqp.core.Exchange (as well as its implementation types) or org.springframework.amqp.core.Binding, then this is a topic and subscription topology. You should firstly analyze the binding relationships between queues and exchanges according to the Binding beans before migration.
      Then when migrating to Service Bus, the RabbitMQ Exchange name should be migrated to Service Bus Topic name, and RabbitMQ Queue name should be migrated to Service Bus Subscription name. You should migrate the "queues" parameter of RabbitListener to "@ServiceBusListener(destination=<topic name>, group=<subscription name>)".
  - For the parameters in the listener function, follow the rules to migrate. Don't add new parameters not in the original listener:
    - If there is Typed parameter "T msg", migrate it to "T msg".
    - If there is a custom domain-specific object parameter, keep the parameter signature exactly as is without changing the type or name.
    - If there is Channel parameter, migrate to "@Header(ServiceBusMessageHeaders.RECEIVED_MESSAGE_CONTEXT) ServiceBusReceivedMessageContext context", in the listener body migrate channel.basicAck to context.complete, channel.basicNack to context.abandon. Add null-check for the injected context before invoking it.
    - If there is "Message" parameter of type org.springframework.amqp.core.Message, migrate to "Message<T>" of type org.springframework.messaging.Message, where T is the message payload type.
    - Keep the "@Headers Map<String, Object> headers" to "@Headers Map<String, Object> headers".
  - For RabbitListener with parameter `bindings = @QueueBinding`:
    - Map [Exchange name, Queue name] to Service Bus [Topic name, Subscription name]. If there is only [Exchange name] from RabbitListener, then generate the [Subscription name] by adding a "sub" suffix of the [Topic name].
    - In ServiceBusListener set destination to Topic name and group to Subscription name.
    - Ignore the key settings for `bindings`.
  - For RabbitListener with parameter `group =`:
    - don't migrate it to Service Bus since there is no associated parameter in ServiceBusListener.
  - Map the other parameters between @RabbitListener and @ServiceBusListener.
  - For the functions of RabbitListener that are not supported by the ServiceBusListener, please directly use the com.azure.messaging.servicebus.ServiceBusProcessorClient behind the ServiceBusListener. To leverage the ServiceBusProcessorClient, use the Spring Bean of com.azure.messaging.servicebus.ServiceBusClientBuilder which is provided by the Spring Cloud Azure Starter automatically, then create the processor client by the client builder:
      1. Autowire the bean of ServiceBusClientBuilder, com.azure.identity.DefaultAzureCredential and com.azure.spring.cloud.autoconfigure.implementation.servicebus.properties.AzureServiceBusProperties from the application context
      2. Create the ServiceBusProcessorClient(s) from the ServiceBusClientBuilder using the DefaultAzureCredential bean as the credential and fully qualified namespace from the AzureServiceBusProperties
      3. Configure the queue or topic/subscription to the processor according to the topology
      4. Convert the RabbitListener method handler to type of Consumer<ServiceBusReceivedMessageContext> and pass it to the processMessage() method of the client builder. Convert the error handling code from the source code if any to a type of Consumer<ServiceBusErrorContext>, otherwise just add some logging for the error handling.
      5. After creating required processor clients, call the "start" method to start them.
      6. Find the proper place to close the clients.

  - Remove all AMQP-related imports after migration
    - All imports from packages starting with 'org.springframework.amqp'
    - All imports from packages starting with 'com.rabbitmq'
    - Any other unused imports that were related to RabbitMQ
  - When migrating code to service bus, make sure to add the necessary imports for every newly add class.

Below are the key information of the rabbitmq and service bus classes, interfaces and annotations for your reference:

Annotation: RabbitListener
  Package: org.springframework.amqp.rabbit.annotation
  Properties:
    - id: The unique identifier of the container managing for this endpoint.
    - containerFactory: The bean name of the RabbitListenerContainerFactory to use to create the message listener container responsible to serve this endpoint.
    - queues: The queues for this listener. The entries can be 'queue name', 'property-placeholder keys' or 'expressions'.
    - concurrency: Set the concurrency of the listener container for this listener.
    - group: Assigns a consumer group name to the listener container to manage the listeners in the client side. Don't migrate this parameter to ServiceBusListener's 'group' parameter.

Annotation: QueueBinding, Queue, Exchange
  Package: org.springframework.amqp.rabbit.annotation

Class: ExchangeTypes
  Package: org.springframework.amqp.core

Interface: Message
  Package: org.springframework.amqp.core

Class: MessageProperties
  Package: org.springframework.amqp.core

Interface: Channel
  Package: com.rabbitmq.client

Annotation: ServiceBusListener
  Package: com.azure.spring.messaging.servicebus.implementation.core.annotation
  Properties:
    - id: The unique identifier of the container managing this endpoint.
    - containerFactory: The bean name of the MessageListenerContainerFactory to use to create the message listener container responsible for serving this endpoint.
    - destination: The destination name for this listener, resolved through the container-wide.
    - group: The name for the durable group, if any. It should be the name for a Service Bus Subscription, which is different from RabbitListener's 'group' parameter.
    - concurrency: Override the container factory's concurrency setting for the listener. It should be an int value.

Annotation: EnableAzureMessaging
  Package: com.azure.spring.messaging.implementation.annotation

Interface: Message<T>
  Package: org.springframework.messaging
  Methods:
    - getPayload()
      Description: Return the message payload.
      Returns: T
    - getHeaders()
      Description: Return message headers for the message.
      Returns: MessageHeaders

Class: ServiceBusReceivedMessageContext
  Package: com.azure.messaging.servicebus

Class: ServiceBusMessageHeaders
  Package: com.azure.spring.messaging.servicebus.support

Class: ServiceBusProcessorClient
  Package: com.azure.messaging.servicebus
  Description: The processor client for processing Service Bus messages.
  Methods: 
    - start()
      Description: Starts the processor in the background.
      Returns: void
    - close()
      Description: Stops message processing and closes the processor. 
      Returns: void  

Sample Migrations:
1. listener with payload
```java
// before
public void listener(T payload) {
}

// after
public void listener(T payload) {
}
```

2. listener with org.springframework.amqp.core.Message
```java
// before
public void listener(Message message) {
    T body = JSON.parseObject(message.getBody(), T.class);
    ...
}

// after
public void listener(Message<T> message) {
    T body = message.getPayload();
    ...
}
```

3. listener with payload and headers
```java
// before
public void listener(T msg, @Headers Map<String, Object> headers) {
    ...
}

// after
public void listener(T msg, @Headers Map<String, Object> headers) {
    ...
}
```

4. listener with payload, Message and Channel
```java
// before
public void listener(T payload, Message message, Channel channel) {
   ...
}

// after
public void listener(T payload, Message<T> message, @Header(ServiceBusMessageHeaders.RECEIVED_MESSAGE_CONTEXT) ServiceBusReceivedMessageContext context) {
   ...
}
```

5. RabbitListener with `bindings = @QueueBinding`
```java
// before
@RabbitListener(bindings = @QueueBinding(
      key = "contractEvents.*",
      value = @Queue("queueName"),
      exchange = @Exchange(value = "exchangeName", type = ExchangeTypes.TOPIC)
))
public void listener(T message) {
}

// after
@ServiceBusListener(destination = "exchangeName", group = "queueName")
public void listener(T message) {
}
```

6. RabbitListener with a domain-specific custom object
```java
// before
public void listener(EventeumMessage message) {
}

// after
public void listener(EventeumMessage message) {
}
```

7. ServiceBusListener on topic and subscription
```java
// before
@Bean("demoExchange")
public DirectExchange demoExchange(){
    return new DirectExchange("demoExchange");
}

@Bean("demoQueue")
public Queue demoQueue(){
    return QueueBuilder.durable("demoQueue").build();
}

@Bean
public Binding demoBinding(){
    return BindingBuilder.bind(demoQueue()).to(demoExchange()).with("demo.key").noargs();
}

@RabbitListener(queues = "demoQueue")
public void listener(T message) {
}

// after, exchange to topic, queue to subscription, Binding to the rule options on subscription create.
@Bean
ServiceBusAdministrationClient adminClient(AzureServiceBusProperties properties, TokenCredential credential) {
    return new ServiceBusAdministrationClientBuilder()
            .credential(properties.getFullyQualifiedNamespace(), credential)
            .buildClient();
}

@Bean("demoTopic")
public TopicProperties demoTopic(ServiceBusAdministrationClient adminClient) {
    try {
        return adminClient.getTopic("demoTopic");
    } catch (ResourceNotFoundException e) {
        return adminClient.createTopic("demoTopic");
    }
}

@Bean("demoSubscription")
@DependsOn("demoTopic")
public SubscriptionProperties demoSubscription(ServiceBusAdministrationClient adminClient) {
    try {
        return adminClient.getSubscription("demoTopic", "demoSubscription");
    } catch (ResourceNotFoundException e) {
        CorrelationRuleFilter ruleFilter = new CorrelationRuleFilter();
        ruleFilter.setLabel("demo.key");
        CreateRuleOptions createRuleOptions = new CreateRuleOptions().setFilter(ruleFilter);
        return adminClient.createSubscription("demoTopic", "demoSubscription",
                "default_rule_name", new CreateSubscriptionOptions(), createRuleOptions);
    }
}

// listener with destination + group
@ServiceBusListener(destination = "demoTopic", group = "demoSubscription")
public void listener(T message) {
}
```



## Migrate RabbitMQ MessageConverter

Migrate RabbitMQ MessageConverter to Azure Service Bus MessageConverter

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `org\.springframework\.amqp\.support\.converter\.`

### Instruction

Your task is to migrate the bean or class member of MessageConverter from RabbitMQ to ServiceBus.
*DO NOT* optimize the code blocks not directly related to the migration changes, *KEEP* those commented out code, minimize the amount of code changes.

Important guidelines:

1. Locate the message converter classes from the package "org.springframework.amqp.support.converter", understand the usage and follow the orders of the scenarios below:
  - If the message converter is initialized without any customizations, then remove the bean or the class member entirely and don't add any replacement.
    Example of what to remove without replacement:
    ```java
    import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
    import org.springframework.amqp.support.converter.MessageConverter;

    @Bean
    public MessageConverter converter() {
        return new Jackson2JsonMessageConverter();
    }
    ```
  - If the message converter is of Jackson2JsonMessageConverter and it has a customized ObjectMapper, replace it with ServiceBusMessageConverter and customize its ObjectMapper with the same customizations. For example:
    ```java
    // before
    import com.fasterxml.jackson.annotation.JsonInclude;
    import com.fasterxml.jackson.databind.ObjectMapper;
    import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
    import org.springframework.context.annotation.Bean;

    @Bean
    public Jackson2JsonMessageConverter producerJackson2MessageConverter() {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
        return new Jackson2JsonMessageConverter(objectMapper);
    }

    // after
    import com.fasterxml.jackson.annotation.JsonInclude;
    import com.fasterxml.jackson.databind.ObjectMapper;
    import com.azure.spring.messaging.servicebus.implementation.support.converter.ServiceBusMessageConverter;
    import org.springframework.context.annotation.Bean;

    @Bean
    public ServiceBusMessageConverter serviceBusMessageConverter() {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
        return new ServiceBusMessageConverter(objectMapper);
    }
    ```
  - For the class members of message converter type, also handle all the references to them accordingly.
2. For the RabbitTemplate or AmqpTemplate setup that includes setMessageConverter() calls:
  - Completely remove the RabbitTemplate or AmqpTemplate bean definition and DO NOT create a ServiceBusTemplate bean as a replacement.
  - ServiceBusTemplate is automatically provided by the Azure ServiceBus auto-configuration, so there's no need to define a custom bean for it.
  - Example of what to remove without replacement:
    ```java
    // Remove this code entirely without creating a ServiceBusTemplate replacement
    import org.springframework.amqp.rabbit.connection.ConnectionFactory;
    import org.springframework.amqp.rabbit.core.RabbitTemplate;
    import org.springframework.context.annotation.Bean;

    @Bean
    public RabbitTemplate rabbitTemplate(final ConnectionFactory connectionFactory) {
        final RabbitTemplate rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(producerJackson2MessageConverter());
        return rabbitTemplate;
    }
    ```
3. Remove all AMQP-related imports after migration
  - All imports of classes starting with 'org.springframework.amqp'
  - All imports of classes starting with 'com.rabbitmq'



## Migrate RabbitTemplate

Migrate RabbitTemplate to ServiceBusTemplate

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `(?i)RabbitTemplate|AmqpTemplate|AmqpHeaders`

### Instruction

Your task is to migrate a Java file from using the RabbitMQ send methods to the Azure Service Bus send methods while maintaining the same functionality. Below is a reference to the relevant APIs for your convenience. You can tell whether it's a rabbitmq or Azure API from the package name.
Try replace all references to RabbitMQ APIs with equivalent Azure Service Bus APIs, using the provided API descriptions as guidance.
Ensure the resulting code is clean, efficient, and preserves the original functionality.
These rules are required when do the migration:
  - When constructing the service bus message, check if there is a routing key in the context. If a routing key is present, set it as the message header named ServiceBusMessageHeaders.SUBJECT. If there is no routing key, do not set the SUBJECT header.
  - When migrating RabbitMQ message properties / headers to service bus message headers, find the other associated message headers from org.springframework.messaging.MessageHeaders and com.azure.spring.messaging.servicebus.support.ServiceBusMessageHeaders.
    1. If RabbitMQ uses the Spring standard message headers, then don't need to migrate them.
    2. If RabbitMQ uses its own properties, try to find any applicable Spring standard Message Headers first, otherwise replace with Service Bus Message Headers.
    3. Remove RabbitMQ properties directly if there is no associated message headers from Spring or Service Bus.
  - ServiceBusTemplate with empty or null parameter is not allowed.
  - *DO NOT* optimize the code blocks not directly related to the migration changes, *KEEP* those commented out code, minimize the amount of code changes.
  - When migrating code to service bus, make sure to add the necessary imports for every newly add class.
  - RabbitTemplate#receive, RabbitTemplate#receiveAndConvert methods and other overloadings are not supported to be migrated to ServiceBusTemplate. You need to use com.azure.messaging.servicebus.ServiceBusReceiverClient to receive messages. To leverage the ServiceBusReceiverClient, use the Spring Bean of com.azure.messaging.servicebus.ServiceBusClientBuilder which is provided by the Spring Cloud Azure Starter automatically, then create the receiver client by the client builder:
      1. Autowire the bean of ServiceBusClientBuilder, com.azure.identity.DefaultAzureCredential and com.azure.spring.cloud.autoconfigure.implementation.servicebus.properties.AzureServiceBusProperties from the application context
      2. Create the ServiceBusReceiverClient(s) from the ServiceBusClientBuilder using the DefaultAzureCredential bean as the credential and fully qualified namespace from the AzureServiceBusProperties
      3. Configure the queue or topic/subscription to the receiver according to the topology
      4. Replace the source code of receiving messages from RabbitTemplate to ServiceBusReceiverClient.
      5. Find the proper place to close the client(s).
  - RabbitTemplate#sendAndReceive, RabbitTemplate#convertSendAndReceive and other overloads can be migrated to ServiceBusTemplate#sendAndReceive. Note for ServiceBusTemplate, there are no overloads for the sendAndReceive method, so you should use this method for all the RPC scenarios. The introduction of ServiceBusTemplate#sendAndReceive can be found in the next API section.
    To use ServiceBusTemplate#sendAndReceive method, there are several prerequisites:
      1. Define a Spring Bean of PropertiesSupplier<ConsumerIdentifier, ConsumerProperties> to enable the session property for receiver client used within ServiceBusTemplate.
      2. Analyse the codebase to find the RabbitMQ reply_to entity, and convert it to a Service Bus entity.
      3. Every time before calling the sendAndReceive method, you should configure the org.springframework.messaging.MessageHeaders.REPLY_CHANNEL header with the reply_to queue/topic entity name for the message to be sent.
  - For the scenario of receive and reply, which is calling RabbitTemplate to send messages within a @RabbitListener, and the sending target is from the message header similar as "amqp_replyTo", then you should migrate is to ServiceBusTemplate following the below instuctions:
      1. get the sending target from the message header of org.springframework.messaging.MessageHeaders.REPLY_CHANNEL.
      2. when sending messages as the reply, set the message header com.azure.spring.messaging.servicebus.support.ServiceBusMessageHeaders.SESSION_ID with the value from the header ServiceBusMessageHeaders.REPLY_TO_SESSION_ID of the incoming messages.
  - The RabbitTemplate#setReturnsCallback and RabbitTemplate#setConfirmCallback methods are not compatable with Service Bus, and need to be removed directly instead of being migrated.
  - Import Cleanup:
    - Remove all AMQP-related imports after migration
    - All imports from packages starting with 'org.springframework.amqp'
    - All imports from packages starting with 'com.rabbitmq'
    - Any other unused imports that were related to RabbitMQ

Below are the APIs provided for your reference:

Interface: RabbitTemplate
  Package: org.springframework.amqp.rabbit.core
  Methods:
    - RabbitTemplate()
      Description: Convenient constructor for use with setter injection.
    - RabbitTemplate(ConnectionFactory connectionFactory)
      Description: Create a rabbit template with default strategies and settings.
    - setMessageConverter(MessageConverter messageConverter)
      Description: Set the message converter for this template.
      Parameters:
        - messageConverter: The message converter
      Returns: Void
    - convertAndSend(Object object)
      Description: Convert a Java object to an Amqp Message and send it to a default exchange with a default routing key.
      Parameters:
        - object: a message to send
      Returns: Void
    - convertAndSend(String routingKey, Object object)
      Description: Convert a Java object to an Amqp Message and send it to a default exchange with a specific routing key.
      Parameters:
        - routingKey: the routing key
        - object: a message to send
      Returns: Void
    - convertAndSend(String exchange, String routingKey, Object object)
      Description: Convert a Java object to an Amqp Message and send it to a specific exchange with a specific routing key.
      Parameters:
        - exchange: the name of the exchange
        - routingKey: the routing key
        - object: a message to send
      Returns: Void
    - setReturnsCallback(ReturnCallback returnCallback)
      Description: Set a callback to receive returned messages. When migrating to Service Bus, this method does not need to be migrated because ServiceBusTemplate doesn't support receive messages, so it should be removed directly.
      Parameters:
        - returnCallback: the callback.
      Returns: Void
    - setConfirmCallback(ConfirmCallback confirmCallback)
      Description: Set a callback function to receive the message publishing confirmation result
      Parameters:
        - confirmCallback: the callback
      Returns: Void
    - receive()
      Description: Receive a message from a default queue. Note: all receive() method and other overloadings should be migrated to ServiceBusReceiverClient's various receive methods, which can be autowired into a Bean from the application context.
       Parameters: void
      Returns: Message
    - receiveAndConvert()
      Description: Receive a message if there is one from a default queue and convert it to a Java object. Returns immediately, possibly with a null value. Note: all receiveAndConvert() method and other overloadings should be migrated to ServiceBusReceiverClient's various receive methods, which can be autowired into a Bean from the application context.
       Parameters: void
      Returns: Object

Interface: ServiceBusTemplate
  Package: com.azure.spring.messaging.servicebus.core
  Description: Azure Service Bus template to support send Message
  Methods:
    - setMessageConverter(AzureMessageConverter<ServiceBusReceivedMessage, ServiceBusMessage> messageConverter)
      Description: Set the message converter to use.
      Parameters:
        - messageConverter: the message converter
      Returns: Void
    - send(String destination, Message<T> message)
      Description: Send a Message to the given destination synchronously.
      Parameters:
        - destination: destination
        - message: message
      Returns: Void
    - sendAsync(String destination, Message<T> message)
      Description: Send a Message to the given destination asynchronously.
      Parameters:
        - destination: destination
        - message: message
      Returns: Void
    - sendAndReceive(String destination, ServiceBusEntityType entityType, Message<T> message)
      Description: Basic RPC pattern usage. Send a message to the destination and wait for a reply message from the replay channel, which must be specified by the message header org.springframework.messaging.MessageHeaders#REPLY_CHANNEL and the session must be enabled
      Parameters:
        - destination: the destination topic or queue name
        - entityType: type of Service Bus entity
        - message: Message to be sent to the Service Bus entity.
      Returns: ServiceBusReceivedMessage - the reply message of the response. If the reply message fails to be obtained, null is returned.

Class: ServiceBusReceiverClient
  Package: com.azure.messaging.servicebus
  Description: A synchronous receiver responsible for receiving ServiceBusReceivedMessage from a queue or topic/subscription on Azure Service Bus.
  Methods: 
    - receiveMessages(int maxMessages)
      Description: Receives an iterable stream of messages from the Service Bus entity.
      Parameters:
        - maxMessages: The maximum number of messages to receive.
      Returns: IterableStream<ServiceBusReceivedMessage>
    - abandon(ServiceBusReceivedMessage message)
      Description: Abandons a message.
      Parameters:
        - message: The ServiceBusReceivedMessage to perform this operation.
      Returns: Void
    - complete(ServiceBusReceivedMessage message)
      Description: Completes a message.
      Parameters:
        - message: The ServiceBusReceivedMessage to perform this operation.
      Returns: Void

Interface: Message<T>
  Package: org.springframework.messaging
  Description: A generic message representation with headers and body.
  Methods:
    - getPayload()
      Returns: T
    - getHeaders()
      Returns: MessageHeaders

Interface: MessageBuilder<T>
  Package: org.springframework.messaging.support
  Description: A builder for creating GenericMessage, where T is the message payload type
  Methods:
    - setHeader(String headerName, @Nullable Object headerValue)
      Description: Set the value for the given header name. If the provided value is null, the header will be removed.
      Parameters:
        - headerName: the name of the header
        - headerValue: the value of the header
      Returns: MessageBuilder<T>
    - withPayload(<T> payload)
      Description: Create a new builder for a message with the given payload.
      Parameters:
        - payload: the payload
      Returns: MessageBuilder<T>
    - build()
      Description: build a message
      Returns: Message<T>

Below are the supported Spring and Service Bus message headers:

Constants: CONTENT_TYPE
  Class: MessageHeaders
  Package: org.springframework.messaging
  Description: The RFC2045 Content-Type descriptor of the message.

Constants: REPLY_CHANNEL
  Class: MessageHeaders
  Package: org.springframework.messaging
  Description: The address of an entity to send replies to.

Constants: CORRELATION_ID
  Class: ServiceBusMessageHeaders
  Package: com.azure.spring.messaging.servicebus.support
  Description: The correlation ID of the message.

Constants: REPLY_TO_SESSION_ID
  Class: ServiceBusMessageHeaders
  Package: com.azure.spring.messaging.servicebus.support
  Description: The ReplyToGroupId property value of the message.

Constants: SCHEDULED_ENQUEUE_TIME
  Class: ServiceBusMessageHeaders
  Package: com.azure.spring.messaging.servicebus.support
  Description: The datetime at which the message should be enqueued in Service Bus, this header should be mapped with RabbitMQ's delay message property.

Constants: SESSION_ID
  Class: ServiceBusMessageHeaders
  Package: com.azure.spring.messaging.servicebus.support
  Description: The session identifier for a session-aware entity.

Constants: TIME_TO_LIVE
  Class: ServiceBusMessageHeaders
  Package: com.azure.spring.messaging.servicebus.support
  Description: The duration of time before this message expires.

Constants: SUBJECT
  Class: ServiceBusMessageHeaders
  Package: com.azure.spring.messaging.servicebus.support
  Description: The subject for the message.

Example migrations:

1. Migrate the RabbitTemplate.convertAndSend to ServiceBusTemplate.send with routing key
  ```java
  // before
  rabbitTemplate.convertAndSend("topic", "routing.key", strMessage);

  // after
  Message<String> message = MessageBuilder.withPayload(strMessage)
      .setHeader(ServiceBusMessageHeaders.SUBJECT, "routing.key").build();
  serviceBusTemplate.send("topic", message);
  ```

2. Migrate the RabbitTemplate.convertAndSend to ServiceBusTemplate.send without routing key
  ```java
  // before
  rabbitTemplate.convertAndSend("queueName", strMessage);

  // after
  Message<String> message = MessageBuilder.withPayload(strMessage).build();
  serviceBusTemplate.send("queueName", message);
  ```

3. Example of migrating rabbitmq message properties to Spring standard message headers:
  ```java
  // before
  MessageProperties properties = new MessageProperties();
  properties.setContentType(MessageProperties.CONTENT_TYPE_JSON);
  Message responseMessage = new Message(responseString.getBytes(), properties);

  // after
  Message<String> responseMessage = MessageBuilder.withPayload(responseString)
      .setHeader(MessageHeaders.CONTENT_TYPE, "application/json")
      .build();
  ```

4. Example of migrating rabbitmq message properties to Service Bus message headers:
  ```java
  // before
  long delayTime = ChronoUnit.MILLIS.between(LocalDateTime.now(), localDateTime);
  MessageProperties properties = new MessageProperties();
  properties.setDelay((int) delayTime);
  Message message = new Message(payload, messageProperties);
  rabbitTemplate.convertAndSend("destination","binding-key", message);

  // after
  Message<String> responseMessage = MessageBuilder.withPayload(payload)
      .setHeader(ServiceBusMessageHeaders.SUBJECT, "binding-key")
      .setHeader(ServiceBusMessageHeaders.SCHEDULED_ENQUEUE_TIME, OffsetDateTime.now().plus(Duration.ofMillis(delayTime)))
      .build();
  serviceBusTemplate.send("destination", message);
  ```

5. Example of migrating RabbitTemplate#sendAndReceive to ServiceBusTemplate#sendAndReceive
  ```java
  // before for RabbitMQ
  Message msg = new Message(message.getBytes());
  log.info("RPC INVOCATION TO RABBITMQ");
  Object response = rabbitTemplate.sendAndReceive(inputBinding.getExchangeName(), inputBinding.getRoutineKey(), msg);
  if (response instanceof byte[]) {
      return new String((byte[]) response, StandardCharsets.UTF_8);
  }

  //after for Service Bus
  // 1. add a Bean of PropertiesSupplier<ConsumerIdentifier, ConsumerProperties> in a Configuration class
  @Bean
  PropertiesSupplier<ConsumerIdentifier, ConsumerProperties> consumerPropertiesSupplier() {
      return key -> {
          ConsumerProperties consumerProperties = new ConsumerProperties();
          consumerProperties.setSessionEnabled(true);
          return consumerProperties;
      };
  }
  // 2. Analyse the source codebase to find the reply_to rabbitmq entity and its migrated Service Bus entity, then set the message header of REPLY_CHANNEL with that entity
  Map<String, Object> headers = new HashMap<>();
  headers.put(MessageHeaders.REPLY_CHANNEL, RPC_QUEUE_REPLY_NAME);
  Message<ProductOfferEvent> message = MessageBuilder.createMessage(message.getBytes(), new MessageHeaders(headers));
  // 3. call ServiceBusTemplate#sendAndReceive
  ServiceBusReceivedMessage replyMessage = serviceBusTemplate.sendAndReceive(inputBinding.getExchangeName(), ServiceBusEntityType.QUEUE, message);
  if (replyMessage != null && replyMessage.getBody() != null) {
      return message.getBody().toString();
  }
  ```
6. Example of Receive and Reply, ignore the difference for the listener annotation:
  ```java
  // before for RabbitMQ
  @RabbitListener(bindings = {
          @QueueBinding(
                  value = @Queue,
                  exchange = @Exchange(value = RabbitMQConfiguration.EXCHANGE_NAME, type = ExchangeTypes.TOPIC),
                  key = "prepend"
          )
  })
  public void onMessage(StringMessage msg, Message message) {
      String text = msg.getBody();
      System.out.println("PrependHello.onMessage - " + text);
      String result = "hello, " + text;
      template.convertAndSend(message.getMessageProperties().getReplyTo(), new StringMessage(result));
  }
  //after for Service Bus
  @ServiceBusListener(destination = RabbitMQConfiguration.EXCHANGE_NAME, group = RabbitMQConfiguration.SUBSCRIPTION_PREPEND)
  public void onMessage(StringMessage msg, Message<?> message) {
      String text = msg.getBody();
      System.out.println("PrependHello.onMessage - " + text);
      String result = "hello, " + text;

      Message<?> sbMessage = MessageBuilder
              .withPayload(new StringMessage(result))
              .setHeader(ServiceBusMessageHeaders.SESSION_ID, message.getHeaders().get(ServiceBusMessageHeaders.REPLY_TO_SESSION_ID))
              .build();

      serviceBusTemplate.send(message.getHeaders().get(MessageHeaders.REPLY_CHANNEL).toString(), sbMessage);
  }
  ```



## Migrate RabbitMQ resources

Migrate RabbitMQ resource creation to Azure Service Bus resources

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `amqp\.core\.`

### Instruction

Your task is to migrate a Java file with Spring Bean configurations of RabbitMQ resource to Azure Service Bus resource beans.
Describe the code to find queues, exchanges and bindings relationships, tell if there is a binding to exchange for each queue or queue only and begin the migration:
  - If there are only Beans of RabbitMQ Queue, then it should be migrated to the Beans of QueueProperties in service bus.
  - If there are Beans of RabbitMQ Queue, Binding and Exchange, then migrate the two beans of Queue and Binding to a single bean of SubscriptionProperties. And migrate the bean of Exchange to TopicProperties in Service bus. To keep the same functionality, do not create service bus queue in this scenario.
  - Find the resource names in the source file, and reuse the names when create new service bus resources.
More RabbitMQ to Service bus resources mapping relationships:
  - Migrate Objects or Beans of AmqpAdmin or RabbitAdmin to ServiceBusAdministrationClient.
  - When constructing the ServiceBusAdministrationClient, autowire the AzureServiceBusProperties and TokenCredential beans from Spring Context, 
    use AzureServiceBusProperties#getFullyQualifiedNamespace and TokenCredential to initialize the client.
  - Migrate Objects or Beans of TopicExchange / DirectExchange / CustomExchange to TopicProperties.
  - Migrate Objects or Beans of RabbitListenerContainerFactory / SimpleRabbitListenerContainerFactory / DirectRabbitListenerContainerFactory to PropertiesSupplier<ConsumerIdentifier, ProcessorProperties>, and map the properties configured to the rabbit container factory to the ProcessorProperties except for message converter or connection factory.
  - Add a Bean of PropertiesSupplier<String, ProducerProperties> when there are any customized properties configured for RabbitTemplate except for message converter and connection factory, and configure the ProducerProperties as how RabbitTemplate are configured.

Remove all amqp imports after migration.
Remove all unused imports after migration.
Add the necessary imports for every newly add class.
Do all the above code migration in the original file instead of creating a new file for Service Bus Configuration.

Below are the APIs provided for your reference:
Class: AzureServiceBusProperties
  Package: com.azure.spring.cloud.autoconfigure.implementation.servicebus.properties

Class: TokenCredential
  Package: com.azure.core.credential

Class: ResourceNotFoundException
  Package: com.azure.core.exception

Class: TopicProperties, SubscriptionProperties, QueueProperties, CorrelationRuleFilter, CreateRuleOptions, CreateSubscriptionOptions
  Package: com.azure.messaging.servicebus.administration.models

Class: ServiceBusAdministrationClient, ServiceBusAdministrationClientBuilder
  Package: com.azure.messaging.servicebus.administration

Annotation: DependsOn
  Package: org.springframework.context.annotation

Interface: PropertiesSupplier<K, V>
  Package: com.azure.spring.messaging
  Description: An interface to provide properties by providing key.
  Methods:
    - getProperties(K key)
      Returns: V
      Description: Get the properties by the key
      Parameters:
        - key: the provided key to identity the target properties instance

Class: ConsumerIdentifier
  Package: com.azure.spring.messaging
  Description: The class to describe the consumer identifier according to the consumer destination and group.
  Methods: 
    - ConsumerIdentifier(String destination)
      Description: Construct an instance via the consumer destination, which is used for Service Bus Queue.
      Parameters: 
        - destination: the consumer destination, should be a Service Bus Queue name.
    - ConsumerIdentifier(String destination, String group)
      Description: Construct an instance via the consumer destination and group, which is used for Event Hubs and Service Bus Topic.
      Parameters: 
        - destination: the consumer destination
        - group: the group

Class: ProcessorProperties
  Package: com.azure.spring.messaging.servicebus.core.properties
  Description: A service bus processor related properties.
  Methods: 
    - setMaxConcurrentCalls(Integer maxConcurrentCalls)
      Description: Set the max concurrent call number.
      Return: void
      Parameters: 
        - maxConcurrentCalls: the max concurrent call number. 
    - setAutoComplete(Boolean autoComplete)
      Description: Set whether to enable auto-complete.
      Return: void
      Parameters: 
        - autoComplete: whether auto-complete is enabled.
    - setPrefetchCount(Integer prefetchCount)
      Description: Set the prefetch count.
      Return: void
      Parameters: 
        - prefetchCount: the prefetch count
    - setSubscriptionName(String subscriptionName)
      Description: Set the subscription name.
      Return: void
      Parameters: 
        - subscriptionName: the subscription name
    - getRetry()
      Description: Get the retry configuration.
      Return: com.azure.spring.cloud.core.provider.retry.AmqpRetryProperties

Class: ProducerProperties
  Package: com.azure.spring.messaging.servicebus.core.properties
  Description: A service bus producer related properties.
  Methods: 
    - getRetry()
      Description: Get the retry configuration.
      Return: com.azure.spring.cloud.core.provider.retry.AmqpRetryProperties

Interface: AmqpRetryProperties
  Description: Unified http retry properties for all Azure SDKs based on HTTP.
  Package: com.azure.spring.cloud.core.properties.retry
  Methods: 
    - setTryTimeout(Duration tryTimeout)
      Description: Set how long to wait until a timeout.
      Return: void
      Parameters: 
        - tryTimeout: the timeout
    - setMode(RetryOptionsProvider.RetryMode mode)
      Description: Set the mode for retry backoff.
      Return: void
      Parameters: 
        - mode: the mode for retry backoff. Accept two types of value: "FIXED" and "EXPONENTIAL".
    - getFixed()
      Description: Get the retry options of the fixed retry mode.
      Return: com.azure.spring.cloud.core.properties.retry.FixedRetryProperties
    - getExponential()
      Description: Get the retry options of the exponential retry mode.
      Return: com.azure.spring.cloud.core.properties.retry.ExponentialRetryProperties
    
Class: FixedRetryProperties
  Description: Properties of the fixed retry mode.
  Package: com.azure.spring.cloud.core.properties.retry
    - setMaxRetries(Integer maxRetries)
      Description: Set the maximum number attempts.
      Return: void
      Parameters: 
        - maxRetries: the maximum number attempts.
    - setDelay(Duration delay)
      Description: Set the amount of time to wait between retry attempts.
      Return: void
      Parameters: 
        - delay: the amount of time to wait between retry attempts.
    
Class: ExponentialRetryProperties
  Description: Properties of the exponential retry mode.
  Package: com.azure.spring.cloud.core.properties.retry
    - setMaxRetries(Integer maxRetries)
      Description: Set the maximum number attempts.
      Return: void
      Parameters: 
        - maxRetries: the maximum number attempts.
    - setBaseDelay(Duration baseDelay)
      Description: Set the amount of time to wait between retry attempts.
      Return: void
      Parameters: 
        - baseDelay: The delay to wait between retry attempts.
    - setMaxDelay(Duration maxDelay)
      Description: Set the maximum permissible amount of time between retry attempts.
      Return: void
      Parameters: 
        - maxDelay: The maximum permissible amount of time between retry attempts.

Important guidelines and migration examples:

1. Init a ServiceBusAdministrationClient bean:
  ```java
  @Bean
  public ServiceBusAdministrationClient adminClient(AzureServiceBusProperties properties, TokenCredential credential) {
      return new ServiceBusAdministrationClientBuilder()
              .credential(properties.getFullyQualifiedNamespace(), credential)
              .buildClient();
  }
  ```

2. Migrate the Spring Bean of Exchange in RabbitMQ to the Bean of Topic in Service Bus
  ```java
  // before: Create exchange in RabbitMQ
  @Bean
  DirectExchange exchange() {
      return new DirectExchange(exchange);
  }

  // after: Create topic in Service Bus
  @Bean
  public TopicProperties topicProperties(ServiceBusAdministrationClient adminClient,
          String topicName) {
      try {
          return adminClient.getTopic(topicName);
      } catch (ResourceNotFoundException e) {
          return adminClient.createTopic(topicName);
      }
  }
  ```
3. Migrate the Spring Beans of Queue and Binding to the Bean of Subscription with rule options, don't migrate to Service Bus Queue.
  ```java
  // before: create queue and binding
  @Bean
  public Queue queue(String queueName) {
      return new Queue(queueName);
  }

  @Bean
  public Binding binding(Queue queue, DirectExchange exchange) {
      return BindingBuilder.bind(queue).to(exchange).with(routingKey);
  }

  // after: create subscription with filter rule
  @Bean
  @DependsOn("topicProperties")
  public SubscriptionProperties subscription(
          ServiceBusAdministrationClient adminClient,
          String topicName,
          String subscriptionName,
          String routeKey) {

      try {
          return adminClient.getSubscription(topicName, subscriptionName);
      } catch (ResourceNotFoundException e) {
          CreateSubscriptionOptions subOptions = new CreateSubscriptionOptions();
          CorrelationRuleFilter filter = new CorrelationRuleFilter().setLabel(routeKey); // label for subject
          CreateRuleOptions ruleOptions = new CreateRuleOptions()
                  .setFilter(filter);
          return adminClient.createSubscription(topicName, subscriptionName, "RouteKey", subOptions, ruleOptions);
      }
  }

4. If there is only Spring Bean of Queue without binding in RabbitMQ, then migrate it to the Bean of Queue in Service Bus
  ```java
  // before: create queue in RabbitMQ
  @Bean
  public Queue queue(String queueName) {
      return new Queue(queueName);
  }

  // after: create queue in Service Bus
  @Bean
  public QueueProperties queue(ServiceBusAdministrationClient adminClient, String queueName) {
      try {
          return adminClient.getQueue(queueName);
      } catch (ResourceNotFoundException e) {
          return adminClient.createQueue(queueName);
      }
  }
  ```

  ```



## Migrate RabbitMQ variable names

Migrate RabbitMQ-style variable names to match Azure Service Bus style

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `(?i)^(?!(?:\s*)(package|import|class)).*rabbitmq`

### Instruction

Your task is to migrate the RabbitMQ variable names to servicebus variable names.
Locate the java code to consume the variables in environment variables or configuration files, if the name has string 'rabbitmq', rename the string 'rabbitmq' to 'servicebus'.
Note:
  - *DO NOT* optimize the code blocks not directly related to the migration changes, *KEEP* those commented out code, minimize the amount of code changes.
  - *DO NOT* update the strings in package names, class names or function names.



## Migrate RabbitMQ properties

Migrate RabbitMQ properties to Azure Service Bus properties in Spring Messaging

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.{yml,yaml,properties}`
- Regex pattern to find code lines: `(?i)rabbitmq`

### Instruction

Your task is to migrate the RabbitMQ connection settings to Service Bus connection settings.

*DO NOT* optimize the code blocks not directly related to the migration changes, *KEEP* those commented out code, minimize the amount of code changes.

1. If the property name starts with 'spring.rabbitmq', with name in [host, port, addresses, username, password, virtual-host, ssl.enabled], do
  - Add Service Bus connection settings:
    - managed-identity-enabled
      property: spring.cloud.azure.credential.managed-identity-enabled
      value: true
    - client-id
      property: spring.cloud.azure.credential.client-id
      value: ${AZURE_CLIENT_ID}
    - entity-type
      property: spring.cloud.azure.servicebus.entity-type
      value: queue or topic. Check the dependency file first to analyze the topology of the RabbitMQ, if there are only Spring beans of Rabbit Queue object, then this is a Rabbit queue topology and should be migrated to Service Bus "queue" entity type. 
             If there are also Spring beans of Rabbit Exchange or Binding objects, then this is a Rabbit Exchange topology and should be migrated to Service Bus "topic" entity type.
    - namespace
      property: spring.cloud.azure.servicebus.namespace
      value: ${SERVICE_BUS_NAMESPACE}
  - Remove the RabbitMQ connection properties match 'spring.rabbitmq.{ host, port, addresses, username, password, virtual-host, ssl.enabled }' as well as other Spring Rabbit properties beginning with 'spring.rabbit.'.
    Don't replace these properties' prefix with 'spring.servicebus.'.

2. When adding the above properties in a yaml file, pay attention to the overall structural correctness.

3. Find the comment out line with keyword 'rabbitmq', and find the next comment out line or to the end of file, the properties between these two lines are regarded as RabbitMQ resource settings.
  The properties with keyword 'rabbitmq' in the names are RabbitMQ resource settings.
  - Replace the string 'rabbitmq' with 'Service Bus' in comment out lines.
  - If there are properties with string 'rabbitmq' in the name, replace string 'rabbitmq' with 'servicebus'.

4. If the file is a docker-compose file and there is a container start with rabbitmq images, remove the rabbitmq container and related usages.



## Migrate RabbitMQ dependencies

Migrate RabbitMQ dependencies (pom.xml for Maven or build.gradle, build.gradle.kts for Gradle) to Azure Service Bus with Spring Messaging

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/{pom.xml,build.gradle,build.gradle.kts}`
- Regex pattern to find code lines: `(spring-boot-starter-amqp|spring-rabbit|spring-amqp)`

### Instruction

In pom.xml or build.gradle or build.gradle.kts: Remove the RabbitMQ dependencies. Add the required dependencies for the Spring Cloud Azure Service Bus with spring messaging.
Only update the lines related to RabbitMQ or Service Bus, don't modify other lines and keep the changes minimized.

Remove the RabbitMQ dependencies with artifactId in [spring-boot-starter-amqp, spring-rabbit, spring-rabbit-test, spring-amqp]
Note: Delete the rabbitmq dependency blocks, do not comment out.

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
  artifactId: spring-cloud-azure-starter
  -
  groupId: com.azure.spring
  artifactId: spring-messaging-azure-servicebus



## Migrate test component RabbitMQContainer

Remove the RabbitMQContainer test component used with RabbitMQ

### Search code
Search files from workspace using below patterns:
- Glob pattern to find files: `**/*.java`
- Regex pattern to find code lines: `RabbitMQContainer`

### Instruction

Your task is to locate the usage of RabbitMQContainer, remove it and cleanup related usage.
*DO NOT* optimize the code blocks not directly related to the migration changes, *KEEP* those commented out code, minimize the amount of code changes.
Note: Delete the RabbitMQContainer blocks, do not comment out.