---
name: migration-sqs-to-servicebus
description: Migrates Java applications from AWS Simple Queue Service (SQS) to Azure Service Bus for message queuing. Replaces AWS SQS SDK dependencies with Azure Service Bus SDK, updates message sending and receiving code, and migrates queue configuration. Use when migrating Java applications from AWS SQS to Azure Service Bus, replacing SQS client code, or modernizing cloud message queuing to Azure.
---

## Migrate dependencies from AWS Simple Queue Service to Azure Service Bus

- Remove AWS Simple Queue Service dependencies.
    - com.amazonaws:aws-java-sdk-sqs
    - software.amazon.awssdk:sqs
- Add Azure Service Bus dependencies.
    - com.azure:azure-messaging-servicebus
    - com.azure:azure-identity
- Use com.azure:azure-sdk-bom to manage the versions of Azure SDK.

## Remove AWS Simple Queue Service configuration

- Remove all AWS Simple Queue Service configuration properties. Look for properties containing "aws.sqs" or "sqs" in their names and delete them.
- After removing AWS SQS configuration, check if the configuration class (e.g., `AwsConfig`) is now empty or only contains a `@Configuration` annotation with no beans or properties. If so, remove the entire class and its file. Do NOT leave empty configuration classes with only a `@Configuration` annotation.

## Migrate Java code from AWS Simple Queue Service to Azure Service Bus

- Migrate Java code from using AWS Simple Queue Service to Azure Service Bus while maintaining the same functionality.

### Migrate AWS Simple Queue Service Client Configuration to Azure Service Bus Client

- For AWS SDK v1 (com.amazonaws.services.sqs), replace AmazonSQSClientBuilder with ServiceBusClientBuilder
- For AWS SDK v2 (software.amazon.awssdk.services.sqs), replace SqsClient with ServiceBusClientBuilder
- Replace AWS credentials and region settings with Azure Service Bus fully qualified namespace settings and use environment variables to get the Service Bus setting values.
- Example:
    ```diff
    -// AWS SQS v1
    -AmazonSQS sqsClient = AmazonSQSClientBuilder.standard()
    -    .withCredentials(new DefaultAWSCredentialsProviderChain())
    -    .withRegion(Regions.US_WEST_2)
    -    .build();
    -// AWS SQS v2
    -SqsClient sqsClient = SqsClient.builder()
    -    .region(Region.US_WEST_2)
    -    .credentialsProvider(DefaultCredentialsProvider.create())
    -    .build();
    +// Azure Service Bus Client using managed identity
    +ServiceBusClientBuilder builder = new ServiceBusClientBuilder()
    +    .fullyQualifiedNamespace(System.getenv("AZURE_SERVICEBUS_FQDN"))
    +    .credential(new DefaultAzureCredentialBuilder().build());
    ```
- Client Specialization. Understand the context of SQS to recognize the scenario of sending or receiving messages, or both. Then generate the Azure Service Bus specialized clients for sending and receiving:
    ```java
    // Create a sender client for a specific queue
    ServiceBusSenderClient sender = builder.sender()
        .queueName(queueName)
        .buildClient();
    // Create a receiver client for a specific queue
    ServiceBusReceiverClient receiver = builder.receiver()
        .queueName(queueName)
        .buildClient();
    ```

### Migrate AWS Simple Queue Service message receiving operations to Azure Service Bus

- Message Receiving Operations:
    - For AWS SDK v1 (com.amazonaws.services.sqs), replace receiveMessage operations with ServiceBusReceiverClient receiveMessages operations
    - For AWS SDK v2 (software.amazon.awssdk.services.sqs), replace receiveMessage operations with ServiceBusReceiverClient receiveMessages operations
    - AWS Simple Queue Service uses explicit message deletion; in the Azure Service Bus example below, ServiceBusReceiverClient uses explicit completion via receiver.complete(message), or you can configure ServiceBusReceiveMode.RECEIVE_AND_DELETE for fire-and-forget semantics
    - Example of AWS SQS v1 message receiving to replace:
        ```java
        // Using direct method
        ReceiveMessageResult result = sqsClient.receiveMessage(queueUrl);
        List<Message> messages = result.getMessages();
        // Using request object with options
        ReceiveMessageRequest receiveRequest = new ReceiveMessageRequest()
            .withQueueUrl(queueUrl)
            .withMaxNumberOfMessages(10)
            .withWaitTimeSeconds(20)
            .withVisibilityTimeout(30)
            .withMessageAttributeNames("All");
        ReceiveMessageResult result = sqsClient.receiveMessage(receiveRequest);
        List<Message> messages = result.getMessages();
        ```
    - Example of AWS SQS v2 message receiving to replace:
        ```java
        // Using builder pattern
        ReceiveMessageResponse response = sqsClient.receiveMessage(ReceiveMessageRequest.builder()
            .queueUrl(queueUrl)
            .maxNumberOfMessages(10)
            .waitTimeSeconds(20)
            .visibilityTimeout(30)
            .messageAttributeNames("All")
            .build());
        List<Message> messages = response.messages();
        ```
    - Azure Service Bus replacement:
        ```java
        // Create receiver with specific options
        ServiceBusReceiverClient receiver = new ServiceBusClientBuilder()
            .fullyQualifiedNamespace("your-namespace.servicebus.windows.net")
            .credential(new DefaultAzureCredentialBuilder().build())
            .receiver()
            .queueName(queueName)
            .buildClient();
        // Receive messages with timeout
        IterableStream<ServiceBusReceivedMessage> messages = receiver.receiveMessages(10, Duration.ofSeconds(20));
        // Process each received message
        for (ServiceBusReceivedMessage message : messages) {
            // Access message body and properties
            String body = message.getBody().toString();
            Map<String, Object> properties = message.getApplicationProperties();
            // Process the message...
            // Complete the message (equivalent to SQS deleteMessage)
            receiver.complete(message);
        }
        ```
- Message Deletion/Completion:
    - Example of AWS SQS v1 message deletion to replace:
        ```java
        // Using direct method
        sqsClient.deleteMessage(queueUrl, message.getReceiptHandle());
        // Using request object
        DeleteMessageRequest deleteRequest = new DeleteMessageRequest()
            .withQueueUrl(queueUrl)
            .withReceiptHandle(message.getReceiptHandle());
        sqsClient.deleteMessage(deleteRequest);
        ```
    - Example of AWS SQS v2 message deletion to replace:
        ```java
        sqsClient.deleteMessage(DeleteMessageRequest.builder()
            .queueUrl(queueUrl)
            .receiptHandle(message.receiptHandle())
            .build());
        ```
    - Azure Service Bus replacement:
        ```java
        // Complete a message (equivalent to SQS deleteMessage)
        receiver.complete(message);
        ```
- Message Attributes Access:
    - AWS SQS v1 message attributes access to replace:
        ```java
        Map<String, MessageAttributeValue> attributes = message.getMessageAttributes();
        String attributeValue = attributes.get("AttributeName").getStringValue();
        ```
    - AWS SQS v2 message attributes access to replace:
        ```java
        Map<String, MessageAttributeValue> attributes = message.messageAttributes();
        String attributeValue = attributes.get("AttributeName").stringValue();
        ```
    - Azure Service Bus replacement:
        ```java
        Map<String, Object> properties = message.getApplicationProperties();
        String attributeValue = (String) properties.get("AttributeName");
        ```

### Migrate AWS Simple Queue Service message sending operations to Azure Service Bus

- Message Sending Operations:
    - For AWS SDK v1 (com.amazonaws.services.sqs), replace sendMessage operations with ServiceBusSenderClient send operations
    - For AWS SDK v2 (software.amazon.awssdk.services.sqs), replace sendMessage operations with ServiceBusSenderClient send operations
    - AWS Simple Queue Service uses queue URLs, while Azure Service Bus uses queue names
- Single Message Sending:
    - Example of AWS SQS v1 message sending to replace:
        ```java
        // Using direct method
        sqsClient.sendMessage(queueUrl, messageBody);
        // Using request object
        SendMessageRequest sendMessageRequest = new SendMessageRequest()
            .withQueueUrl(queueUrl)
            .withMessageBody(messageBody)
            .withDelaySeconds(delaySeconds)
            .withMessageAttributes(messageAttributes);
        sqsClient.sendMessage(sendMessageRequest);
        ```
    - Example of AWS SQS v2 message sending to replace:
        ```java
        // Using direct method
        sqsClient.sendMessage(SendMessageRequest.builder()
            .queueUrl(queueUrl)
            .messageBody(messageBody)
            .delaySeconds(delaySeconds)
            .messageAttributes(messageAttributes)
            .build());
        ```
    - Azure Service Bus replacement:
        ```java
        // Create a message with properties
        ServiceBusMessage message = new ServiceBusMessage(messageBody);
        // Set properties (equivalent to SQS message attributes)
        if (messageAttributes != null) {
            for (Map.Entry<String, MessageAttributeValue> entry : messageAttributes.entrySet()) {
                message.getApplicationProperties().put(entry.getKey(), entry.getValue().getStringValue());
            }
        }
        // Set scheduled enqueue time (equivalent to SQS delay seconds)
        if (delaySeconds > 0) {
            message.setScheduledEnqueueTime(OffsetDateTime.now().plusSeconds(delaySeconds));
        }
        // Send the message
        sender.sendMessage(message);
        ```
- Batch Message Sending:
    - Example of AWS SQS v1 batch message sending to replace:
        ```java
        // Create batch request entries
        List<SendMessageBatchRequestEntry> entries = new ArrayList<>();
        entries.add(new SendMessageBatchRequestEntry("id1", "message1"));
        entries.add(new SendMessageBatchRequestEntry("id2", "message2"));
        // Send batch
        SendMessageBatchRequest batchRequest = new SendMessageBatchRequest()
            .withQueueUrl(queueUrl)
            .withEntries(entries);
        sqsClient.sendMessageBatch(batchRequest);
        ```
    - Example of AWS SQS v2 batch message sending to replace:
        ```java
        // Create batch request entries
        List<SendMessageBatchRequestEntry> entries = Arrays.asList(
            SendMessageBatchRequestEntry.builder()
                .id("id1")
                .messageBody("message1")
                .build(),
            SendMessageBatchRequestEntry.builder()
                .id("id2")
                .messageBody("message2")
                .build()
        );
        // Send batch
        sqsClient.sendMessageBatch(SendMessageBatchRequest.builder()
            .queueUrl(queueUrl)
            .entries(entries)
            .build());
        ```
    - Azure Service Bus replacement:
        ```java
        // Create a list of messages
        List<ServiceBusMessage> messages = Arrays.asList(
            new ServiceBusMessage("message1"),
            new ServiceBusMessage("message2")
        );
        // Send the batch of messages
        sender.sendMessages(messages);
        ```
- Message Attributes Mapping:
    - Map AWS SQS message attributes to Azure Service Bus application properties:
        ```java
        // AWS SQS v1
        Map<String, MessageAttributeValue> attributes = new HashMap<>();
        attributes.put("AttributeName", new MessageAttributeValue()
            .withDataType("String")
            .withStringValue("AttributeValue"));
        // AWS SQS v2
        Map<String, MessageAttributeValue> attributes = new HashMap<>();
        attributes.put("AttributeName", MessageAttributeValue.builder()
            .dataType("String")
            .stringValue("AttributeValue")
            .build());
        // Azure Service Bus equivalent
        ServiceBusMessage message = new ServiceBusMessage(messageBody);
        message.getApplicationProperties().put("AttributeName", "AttributeValue");
        ```
- Message ID Retrieval:
    - **IMPORTANT**: AWS SQS returns a server-generated message ID from the send response (e.g., `response.messageId()` for v2 or `result.getMessageId()` for v1). Azure Service Bus `sendMessage()` returns void and does NOT provide a server-generated message ID. `ServiceBusMessage.getMessageId()` only returns the ID that was explicitly set before sending — it will return null if no ID was set.
    - When the original code retrieves a message ID from the SQS send response, explicitly set a unique message ID on the ServiceBusMessage before sending, then use that same value.
    - **NEVER** return a generic success string like `"Message sent successfully"` when the original code returned a message ID. The migrated method MUST preserve the same return type and semantics — return the actual message ID that was set on the `ServiceBusMessage`.
    - Example of AWS SQS v1 message ID retrieval to replace:
        ```java
        SendMessageResult result = sqsClient.sendMessage(queueUrl, messageBody);
        String messageId = result.getMessageId();
        ```
    - Example of AWS SQS v2 message ID retrieval to replace:
        ```java
        SendMessageResponse response = sqsClient.sendMessage(SendMessageRequest.builder()
            .queueUrl(queueUrl)
            .messageBody(messageBody)
            .build());
        String messageId = response.messageId();
        ```
    - Azure Service Bus replacement:
        ```java
        ServiceBusMessage message = new ServiceBusMessage(messageBody);
        // Explicitly set a unique message ID before sending
        message.setMessageId(UUID.randomUUID().toString());
        sender.sendMessage(message);
        // Retrieve the message ID that was set
        String messageId = message.getMessageId();
        ```

### Migrate AWS Simple Queue Service queue management operations to Azure Service Bus

- Queue Management Client:
    - For AWS SDK v1 (com.amazonaws.services.sqs), replace administrative operations with ServiceBusAdministrationClient
    - For AWS SDK v2 (software.amazon.awssdk.services.sqs), replace administrative operations with ServiceBusAdministrationClient
    - Example of Azure Service Bus administration client:
        ```java
        // Create administration client
        ServiceBusAdministrationClient adminClient = new ServiceBusAdministrationClientBuilder()
            .fullyQualifiedNamespace(System.getenv("AZURE_SERVICEBUS_FQDN"))
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildClient();
        ```
- Queue Creation:
    - Example of AWS SQS v1 queue creation to replace:
        ```java
        // Using direct method
        CreateQueueResult result = sqsClient.createQueue(queueName);
        String queueUrl = result.getQueueUrl();
        // Using request object with attributes
        Map<String, String> attributes = new HashMap<>();
        attributes.put(QueueAttributeName.VisibilityTimeout.toString(), "60");
        attributes.put(QueueAttributeName.MessageRetentionPeriod.toString(), "86400");
        CreateQueueRequest createQueueRequest = new CreateQueueRequest()
            .withQueueName(queueName)
            .withAttributes(attributes);
        CreateQueueResult result = sqsClient.createQueue(createQueueRequest);
        ```
    - Example of AWS SQS v2 queue creation to replace:
        ```java
        // Using builder pattern
        CreateQueueResponse response = sqsClient.createQueue(CreateQueueRequest.builder()
            .queueName(queueName)
            .attributes(Map.of(
                QueueAttributeName.VISIBILITY_TIMEOUT, "60",
                QueueAttributeName.MESSAGE_RETENTION_PERIOD, "86400"
            ))
            .build());
        String queueUrl = response.queueUrl();
        ```
    - Azure Service Bus replacement:
        ```java
        // Create queue with options
        CreateQueueOptions queueOptions = new CreateQueueOptions()
            .setLockDuration(Duration.ofSeconds(60)) // Equivalent to visibility timeout
            .setMaxSizeInMegabytes(1024)            // Size in MB
            .setMaxDeliveryCount(10);               // Max delivery attempts
        adminClient.createQueue(queueName);
        // or with properties
        adminClient.createQueue(queueName, queueOptions);
        ```
- Queue Deletion:
    - Example of AWS SQS v1 queue deletion to replace:
        ```java
        // Using direct method
        sqsClient.deleteQueue(queueUrl);
        // Using request object
        DeleteQueueRequest deleteQueueRequest = new DeleteQueueRequest(queueUrl);
        sqsClient.deleteQueue(deleteQueueRequest);
        ```
    - Example of AWS SQS v2 queue deletion to replace:
        ```java
        sqsClient.deleteQueue(DeleteQueueRequest.builder()
            .queueUrl(queueUrl)
            .build());
        ```
    - Azure Service Bus replacement:
        ```java
        adminClient.deleteQueue(queueName);
        ```
- Queue Listing:
    - Example of AWS SQS v1 queue listing to replace:
        ```java
        // Using direct method
        ListQueuesResult result = sqsClient.listQueues();
        List<String> queueUrls = result.getQueueUrls();
        // Using request object
        ListQueuesRequest listQueuesRequest = new ListQueuesRequest()
            .withQueueNamePrefix("prefix");
        ListQueuesResult result = sqsClient.listQueues(listQueuesRequest);
        ```
    - Example of AWS SQS v2 queue listing to replace:
        ```java
        ListQueuesResponse response = sqsClient.listQueues(ListQueuesRequest.builder()
            .queueNamePrefix("prefix")
            .build());
        List<String> queueUrls = response.queueUrls();
        ```
    - Azure Service Bus replacement:
        ```java
        // List all queues
        PagedIterable<QueueProperties> queues = adminClient.listQueues();
        // Use the queues
        for (QueueProperties queue : queues) {
            String queueName = queue.getName();
            // Do something with the queue
        }
        ```

### Import Cleanup
- Remove all AWS SQS-related imports after migration:
    - All imports from packages starting with 'com.amazonaws.services.sqs'
    - All imports from packages starting with 'software.amazon.awssdk.services.sqs'
- Add required Azure Service Bus imports

### Migrate all remaining AWS Simple Queue Service related code to Azure Service Bus

After completing the specific migrations above, scan the entire codebase to ensure no AWS Simple Queue Service references remain. All residual SQS code must be migrated to Azure Service Bus equivalents.

1. **Search for remaining SQS usage** by looking for these patterns in Java files:
    - `software.amazon.awssdk.services.sqs` (AWS SDK v2 imports)
    - `com.amazonaws.services.sqs` (AWS SDK v1 imports)
    - `SQS` (class names, variable names, and other references)
2. **Migrate each remaining reference** to its Azure Service Bus equivalent, following the API mappings documented in the sections above.
3. **Rename files** whose names contain "SQS" to reflect Azure Service Bus naming (e.g., `SQSService.java` → `ServiceBusService.java`).
4. **Verify** that no SQS-related imports, class names, or string literals remain in any Java source file.
