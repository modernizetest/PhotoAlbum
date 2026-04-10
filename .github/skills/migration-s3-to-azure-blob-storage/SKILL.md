---
name: migration-s3-to-azure-blob-storage
description: Migrate AWS S3 to Azure Blob Storage
---

name: 'Migrate S3 Access Policy to Azure Blob SAS Token'
description: "Migrate Amazon S3 access policy logic to Azure Blob Storage using SAS token generation."
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    PutBucketPolicyRequest|DeleteBucketPolicyRequest|GetBucketPolicyRequest|AccessControlPolicy
steps:
  - description: "Migrate Amazon S3 access policy logic to Azure Blob SAS token generation"
    type: "instruction"
    content: |
      Your task is to migrate code that relies on Amazon S3 access policies (which use JSON policy documents, bucket policies, or IAM-based controls) to the Azure Storage Blob model that uses Shared Access Signature (SAS) tokens.

      In Amazon S3:
      - Access policies are typically defined in JSON format and attached to buckets or objects.
      - They specify allowed actions (e.g., s3:GetObject, s3:PutObject) and conditions under which these actions are permitted.

      In Azure Storage Blob:
      - SAS tokens are generated to delegate specific permissions (e.g., read, write, delete) for a given container or blob.
      - These tokens are created using methods such as BlobContainerClient.generateSas() or BlobServiceClient.generateUserDelegationSas(), and include parameters like expiry time, permissions, and optionally IP restrictions.

      Note:
        1. The package of `BlobClient` is com.azure.storage.blob and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here.
        2. The package of `BlobContainerClient` is com.azure.storage.blob.BlobContainerClient, don't make mistake here.

      Here are the APIs for reference, don't forget to import the package whenever you are adding a new class reference in code edit

      Interface: PutBucketPolicyRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - PutBucketPolicyRequest.Builder bucket​(String bucket)
            Description: The name of the bucket.
            Parameters:
              - bucket - The name of the bucket.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - PutBucketPolicyRequest.Builder policy​(String policy)
            Description: The bucket policy as a JSON document.
            Parameters:
              - policy - The bucket policy as a JSON document.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: DeleteBucketPolicyRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - DeleteBucketPolicyRequest.Builder bucket​(String bucket)
            Description: The name of the bucket.
            Parameters:
              - bucket - The name of the bucket.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: GetBucketPolicyRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - GetBucketPolicyRequest.Builder bucket​(String bucket)
            Description: The name of the bucket.
            Parameters:
              - bucket - The name of the bucket.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: AccessControlPolicy.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - AccessControlPolicy.Builder grants​(Collection<Grant> grants)
            Description: A list of grants.
            Parameters:
              - grants - A list of grants.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - AccessControlPolicy.Builder grants​(Grant... grants)
            Description: A list of grants.
            Parameters:
              - grants - A list of grants.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - AccessControlPolicy.Builder owner​(Owner owner)
            Description: Container for the bucket owner's display name and ID.
            Parameters:
              - owner - Container for the bucket owner's display name and ID.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface Grant.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - Grant.Builder permission​(String permission)
            Description: Specifies the permission given to the grantee.
            Parameters:
              - permission - Specifies the permission given to the grantee.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - Grant.Builder grantee​(Grantee grantee)
            Description: The person being granted permissions.
            Parameters:
              - grantee - The person being granted permissions.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - AccessControlPolicy.Builder owner​(Owner owner)
            Description: Container for the bucket owner's display name and ID.
            Parameters:
              - owner - Container for the bucket owner's display name and ID.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Class: BlobClient
        Package: com.azure.storage.blob
        Note: `The package of `BlobClient` is com.azure.storage.blob and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here.
        Methods:
          - public String generateSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues)
            Description: Generates a service SAS for the blob using the specified BlobServiceSasSignatureValues
            Parameters:
              - blobServiceSasSignatureValues - BlobServiceSasSignatureValues
            Returns: A String representing the SAS query parameters.
          - public String generateSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues, Context context)
            Description: Generates a service SAS for the blob using the specified BlobServiceSasSignatureValues
            Parameters:
              - blobServiceSasSignatureValues - BlobServiceSasSignatureValues
              - context - Additional context that is passed through the code when generating a SAS.
            Returns: A String representing the SAS query parameters.
          - public String generateUserDelegationSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues, UserDelegationKey userDelegationKey)
            Description: Generates a user delegation SAS for the blob using the specified BlobServiceSasSignatureValues.
            Parameters:
              - blobServiceSasSignatureValues - BlobServiceSasSignatureValues
              - userDelegationKey - A UserDelegationKey object used to sign the SAS values. See getUserDelegationKey(OffsetDateTime start, OffsetDateTime expiry) for more information on how to get a user delegation key.
            Returns: A String representing the SAS query parameters.
          - public String generateUserDelegationSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues, UserDelegationKey userDelegationKey, String accountName, Context context)
            Description: Generates a user delegation SAS for the blob using the specified BlobServiceSasSignatureValues.
            Parameters:
              - blobServiceSasSignatureValues - BlobServiceSasSignatureValues
              - userDelegationKey - A UserDelegationKey object used to sign the SAS values. See getUserDelegationKey(OffsetDateTime start, OffsetDateTime expiry) for more information on how to get a user delegation key.
              - accountName - The account name.
              - context - Additional context that is passed through the code when generating a SAS.
            Returns: A String representing the SAS query parameters.

      Class: BlobServiceSasSignatureValues
        Package: com.azure.storage.blob.sas
        Description: Used to initialize parameters for a Shared Access Signature (SAS) for an Azure Blob Storage service.
        Constructors:
          - BlobServiceSasSignatureValues(OffsetDateTime expiryTime, BlobSasPermission permissions)
            Description: Creates a BlobServiceSasSignatureValues object with the specified expiry time and permissions.
            Parameters:
              - expiryTime: The time after which the SAS will expire.
              - permissions: The permissions to set for the SAS.
          - BlobServiceSasSignatureValues(OffsetDateTime expiryTime, BlobContainerSasPermission  permissions)
            Description: Creates a BlobServiceSasSignatureValues object with the specified expiry time and permissions.
            Parameters:
              - expiryTime: The time after which the SAS will expire.
              - permissions - BlobContainerSasPermission allowed by the SAS.
        Methods:
          - BlobServiceSasSignatureValues setExpiryTime(OffsetDateTime expiryTime)
            Description: Sets when the SAS will expire.
            Parameters:
              - expiryTime: The time after which the SAS will expire.
            Returns: The updated BlobServiceSasSignatureValues object.
          - BlobServiceSasSignatureValues setPermissions(BlobSasPermission permissions)
            Description: Sets the permissions for the SAS.
            Parameters:
              - permissions: The permissions to set for the SAS.
            Returns: The updated BlobServiceSasSignatureValues object.

      Class: BlobSasPermission
        Package: com.azure.storage.blob.sas
        Methods:
          - public BlobSasPermission setReadPermission(boolean hasAddPermission)
            Description: Sets if the permission allows for read operations.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setWritePermission(boolean hasAddPermission)
            Description: Sets if the permission allows for write operations.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setCreatePermission(boolean hasAddPermission)
            Description: Sets if the permission allows for create operations.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setDeletePermission(boolean hasAddPermission)
            Description: Sets if the permission allows for delete operations.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setAddPermission(boolean hasAddPermission)
            Description: Sets the add permission status.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setExecutePermission(boolean hasExecutePermission)
            Description: Sets the add permission status.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setListPermission(boolean hasExecutePermission)
            Description: Sets the add permission status.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setReadPermission(boolean hasExecutePermission)
            Description: Sets the add permission status.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setWritePermission(boolean hasExecutePermission)
            Description: Sets the add permission status.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.

       Class: BlobServiceClient
        Package: com.azure.storage.blob
        Methods:
          - BlobContainerClient getBlobContainerClient(String containerName)
            Description: Gets a client pointing to the container.
            Parameters:
              - containerName: The name of the container to point to.
            Returns: A BlobContainerClient object pointing to the specified container.

      Class: BlobContainerClient
        Package: com.azure.storage.blob
        Methods:
          - BlobClient getBlobClient(String blobName)
            Description: Gets a client pointing to the blob.
            Parameters:
              - blobName: The name of the blob to point to.
            Returns: A BlobClient object pointing to the specified blob.
          - public String generateSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues, Context context)
            Description: Generates a service SAS for the container using the specified BlobServiceSasSignatureValues
            Parameters: 
              - blobServiceSasSignatureValues: Configurations for the service SAS.
              - userDelegationKey : Additional context that is passed through the code when generating a SAS.
            Returns: A String representing the SAS query parameters.
          - public String generateUserDelegationSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues, UserDelegationKey userDelegationKey)
            Description: Generates a user delegation SAS for the container using the specified BlobServiceSasSignatureValues.
            Parameters: 
              - blobServiceSasSignatureValues: Configurations for the service SAS.
              - context: A UserDelegationKey object used to sign the SAS values. 
            Returns: A String representing the SAS query parameters.
          - public String generateSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues)
            Description: Generates a service SAS for the container using the specified BlobServiceSasSignatureValues
            Parameters:
              - blobServiceSasSignatureValues: Configurations for the service SAS.
            Returns: A String representing the SAS query parameters.
          - public void setAccessPolicy(PublicAccessType accessType, List<BlobSignedIdentifier> identifiers)
            Description: Sets the container's permissions. The permissions indicate whether blobs in a container may be accessed publicly. Note that, for each signed identifier, we will truncate the start and expiry times to the nearest second to ensure the time formatting is compatible with the service. 
            Parameters:
              - accessType - Specifies how the data in this container is available to the public. See the x-ms-blob-public-access header in the Azure Docs for more information. Pass null for no public access.
              - identifiers - A list of BlobSignedIdentifier objects that specify the permissions for the container. Please see here for more information. Passing null will clear all access policies.
            Returns: N/A
          - public Response setAccessPolicyWithResponse(PublicAccessType accessType, List identifiers, BlobRequestConditions requestConditions, Duration timeout, Context context)
            Description: Sets the container's permissions. The permissions indicate whether blobs in a container may be accessed publicly. Note that, for each signed identifier, we will truncate the start and expiry times to the nearest second to ensure the time formatting is compatible with the service. 
            Parameters:
              - accessType - Specifies how the data in this container is available to the public. See the x-ms-blob-public-access header in the Azure Docs for more information. Pass null for no public access.
              - identifiers - A list of BlobSignedIdentifier objects that specify the permissions for the container. Please see here for more information. Passing null will clear all access policies.
              - requestConditions - BlobRequestConditions
              - timeout - An optional timeout value beyond which a RuntimeException will be raised.
              - context - Additional context that is passed through the Http pipeline during the service call.
            Returns: A response containing status code and HTTP headers

      Class: BlobAccessPolicy
        Package: com.azure.storage.blob.models
        Description: An Access policy.
        Methods:
          - public BlobAccessPolicy setExpiresOn(OffsetDateTime expiresOn)
            Description: Set the expiresOn property: the date-time the policy expires.
            Parameters:
              - expiresOn - the expiresOn value to set.
            Returns: the BlobAccessPolicy object itself.
          - public BlobAccessPolicy setPermissions(String permissions)
            Description: Set the permissions property: the permissions for the acl policy.
            Parameters:
              - permissions - the permissions value to set.
            Returns: the BlobAccessPolicy object itself.
          - public BlobAccessPolicy setStartsOn(OffsetDateTime startsOn)
            Description: Set the startsOn property: the date-time the policy is active.
            Parameters:
              - startsOn - the startsOn value to set.
            Returns: the BlobAccessPolicy object itself.

      Class: BlobSignedIdentifier
        Package: com.azure.storage.blob.models
        Description: signed identifier.
        Methods:
          - public BlobSignedIdentifier setAccessPolicy(BlobAccessPolicy accessPolicy)
            Description: Set the accessPolicy property: An Access policy.
            Parameters:
              - accessPolicy - the accessPolicy value to set.
            Returns: the BlobSignedIdentifier object itself.
          - public BlobSignedIdentifier setId(String id)
            Description: Set the id property: a unique id.
            Parameters:
              - id - the id value to set.
            Returns: the BlobSignedIdentifier object itself.

name: 'Migrate S3 project configuration to Azure Blob Storage configuration'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/application.{properties,yaml,yml}'
  codePattern: >-
    s3|bucket|key

steps:
  - description: "Migrate S3 project configuration to Azure Blob Storage configuration"
    type: "instruction"
    content: |
      Your task is to migrate an application.properties/yaml file from using the Amazon S3 related configuration to the Azure Storage Blob related. Please pay attention to the configurations namings before editing, only do the modification when you are sure this is a s3 related configuration.
      Some examples: s3.bucket.name -> blob.container.name; s3.key.name -> blob.name;
      Aws s3 has a unique property, location, which is usually not needed in Azure blob side. While Azure blob sometimes require to pass in the storage account name or entire endpoint, please provide it when it's necessary.

name: 'Migrate S3clientBuilder to BlobServiceClientBuilder'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    S3Client|S3ClientBuilder
steps:
  - description: "Migrate s3client to Azure Storage Blob client"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      When migrate S3clientBuilder to BlobServiceClientBuilder, you should replace s3 client with BlobServiceClient. Please note that avoid using connectionString of the Azure Storage Blob to init the BlobServiceClient, use AzureDefaultCredential instead. Avoid using BlockBlobClient as well.
      At the same time, you should pay attention to the package name you import when initializing the clients. Packages are listed below along with the APIs.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Note that:
      1. The resource type BlobServiceClient does not implement java.lang.AutoCloseableJava, so don't include it into an AutoCloseable like try(BlobServiceClient xxx)
      2. `The package of `BlobClient` & `BlobServiceClient` are both "com.azure.storage.blob:, and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here!
      3. By default, please choose AzureDefaultCredential + endpoint as the parameters to init the blob client.
      ```java
      // Set your storage account endpoint
      String endpoint = "https://yourstorageaccount.blob.core.windows.net";

      // Create BlobServiceClient using credential and endpoint
      BlobServiceClient blobServiceClient = new BlobServiceClientBuilder()
          .endpoint(endpoint)
          .credential(new DefaultAzureCredentialBuilder().build())
          .buildClient();
      ```
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: S3Client
        Package: software.amazon.awssdk.services.s3
        Methods:
          - static S3ClientBuilder builder()
            Description: Create a builder that can be used to configure and create a S3Client.
            Details: A builder for creating an instance of S3Client. This can be created with the static S3Client.builder() method.

      Interface: S3ClientBuilder
        Package: software.amazon.awssdk.services.s3
        Super interfaces:
          - AwsClientBuilder<S3ClientBuilder,​S3Client>
          - AwsSyncClientBuilder<S3ClientBuilder,​S3Client>
          - Buildable
          - S3BaseClientBuilder<S3ClientBuilder,​S3Client>
          - SdkBuilder<S3ClientBuilder,​S3Client>
          - SdkClientBuilder<S3ClientBuilder,​S3Client>
          - SdkSyncClientBuilder<S3ClientBuilder,​S3Client>

      Interface AwsClientBuilder<BuilderT extends AwsClientBuilder<BuilderT,ClientT>,ClientT>
        Type Parameters:
          - BuilderT: The type of builder that should be returned by the fluent builder methods in this interface.
          - ClientT: The type of client generated by this builder.
        Methods:
          - default S3ClientBuilder credentialsProvider(AwsCredentialsProvider credentialsProvider)
            Description: Configure the credentials that should be used to authenticate with AWS.
          - default S3ClientBuilder credentialsProvider(IdentityProvider<? extends AwsCredentialsIdentity> credentialsProvider)
            Description: Configure the credentials that should be used to authenticate with AWS.
          - S3ClientBuilder region(Region region)
            Description: Configure the region with which the SDK should communicate.

      Interface SdkBuilder<B extends SdkBuilder<B,T>,T>
        Type Parameters:
          - T: the type that the builder will build
          - B: the builder type (this)
        Methods:
          - ​S3Client build()
            Description: An immutable object that is created from the properties that have been set on the builder.
            Returns: An instance of T

      Class BlobServiceClientBuilder
        Package: com.azure.storage.blob
        Description: Creates a builder instance that is able to configure and construct BlobServiceClient and BlobServiceAsyncClient.
        Methods:
          - public BlobServiceClient buildClient()
            Returns: a BlobServiceClient created from the configurations in this builder.
          - public BlobServiceClientBuilder connectionString(String connectionString)
            Description: Sets the connection string to connect to the service.
            Parameters:
              - connectionString - Connection string of the storage account.
            Returns: the updated BlobServiceClientBuilder
          - public BlobServiceClientBuilder credential(AzureSasCredential credential)
            Description: Sets the AzureSasCredential used to authorize requests sent to the service.
            Parameters:
              - credential: AzureSasCredential used to authorize requests sent to the service.
            Returns: the updated BlobServiceClientBuilder.
          - public BlobServiceClientBuilder credential(TokenCredential credential)
            Description: Sets the TokenCredential used to authorize requests sent to the service. Refer to the Azure SDK for Java identity and authentication documentation for more details on proper usage of the TokenCredential type.
            Parameters:
            - credential: TokenCredential used to authorize requests sent to the service.
            Returns: the updated BlobServiceClientBuilder
          - public BlobServiceClientBuilder credential(StorageSharedKeyCredential credential)
            Description: Sets the StorageSharedKeyCredential used to authorize requests sent to the service.
            Parameters:
            - credential: StorageSharedKeyCredential.
            Returns: the updated BlobServiceClientBuilder
          - public BlobServiceClientBuilder endpoint(String endpoint)
            Description: Sets the blob service endpoint, additionally parses it for information (SAS token)
            Parameters:
            - endpoint: URL of the service
            Returns: the updated BlobServiceClientBuilder.

      Class DefaultAzureCredentialBuilder
        Package: com.azure.identity
        MavenArtifact: com.azure:azure-identity
        Methods:
          public DefaultAzureCredential build()
          Description: Creates new DefaultAzureCredential with the configured options set.
          Returns: a DefaultAzureCredential with the current configurations.

name: 'Migrate S3client copyObject to Azure Blob Storage'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    copyObject|CopyObjectRequest|CopyObjectResponse

steps:
  - description: "Migrate s3client with copyObject API to Azure Blob Storage BlobClient.beginCopy"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      Note:
        1. `The package of `BlobClient` is com.azure.storage.blob
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: S3Client
        Package: software.amazon.awssdk.services.s3
        Methods:
        - default CopyObjectResponse copyObject​(CopyObjectRequest copyObjectRequest) throws ObjectNotInActiveTierErrorException, AwsServiceException, SdkClientException, S3Exception
          Description: Creates a copy of an object that is already stored in Amazon S3. You can store individual objects of up to 5 TB in Amazon S3. You create a copy of your object up to 5 GB in size in a single atomic action using this API. However, to copy an object greater than 5 GB, you must use the multipart upload Upload Part - Copy (UploadPartCopy) API. For more information, see Copy Object Using the REST Multipart Upload API. You can copy individual objects between general purpose buckets, between directory buckets, and between general purpose buckets and directory buckets.
          Parameters:
          - copyObjectRequest:
          Returns: Result of the CopyObject operation returned by the service.

      Class: CopyObjectRequest
        Package: software.amazon.awssdk.services.s3.model
        Methods:
        - public final String destinationBucket()
          Description: The name of the destination bucket.
          Returns: The name of the destination bucket.
        - public final String sourceBucket()
          Description: The name of the bucket containing the object to copy. The provided input will be URL encoded. The sourceBucket, sourceKey, and sourceVersionId parameters must not be used in conjunction with the copySource parameter.
          Returns: The name of the bucket containing the object to copy. The provided input will be URL encoded. The sourceBucket, sourceKey, and sourceVersionId parameters must not be used in conjunction with the copySource parameter.

      Class: CopyObjectResponse
        Package: software.amazon.awssdk.services.s3.model
        Methods:
        - public final CopyObjectResult copyObjectResult()
          Description: Container for all response elements.
          Returns: Container for all response elements.

      Class: CopyObjectResult
        Package: software.amazon.awssdk.services.s3.model
        Description: Container for all response elements.
        Methods:
        - public final <T> Optional<T> getValueForField​(String fieldName, Class<T> clazz)

      Class BlobClient
        Package: com.azure.storage.blob
        Note: `The package of `BlobClient` is com.azure.storage.blob and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here.
        Methods:
        - public SyncPoller beginCopy(BlobBeginCopyOptions options)
          Description: Copies the data at the source URL to a blob.
          This method triggers a long-running, asynchronous operations. The source may be another blob or an Azure File. If the source is in another account, the source must either be public or authenticated with a SAS token. If the source is in the same account, the Shared Key authorization on the destination will also be applied to the source. The source URL must be URL encoded.
          Parameters:
          - options: BlobBeginCopyOptions
          Returns: A SyncPoller<T,U> to poll the progress of blob copy operation.
        - public SyncPoller beginCopy(String sourceUrl, Duration pollInterval)
          Description: Copies the data at the source URL to a blob.This method triggers a long-running, asynchronous operations. The source may be another blob or an Azure File. If the source is in another account, the source must either be public or authenticated with a SAS token. If the source is in the same account, the Shared Key authorization on the destination will also be applied to the source. The source URL must be URL encoded.
          Parameters:
          - sourceUrl: The source URL to copy from. URLs outside of Azure may only be copied to block blobs.
          - pollInterval: Duration between each poll for the copy status. If none is specified, a default of one second is used.
          Returns: A SyncPoller<T,U> to poll the progress of blob copy operation.

name: 'Migrate S3client createBucket to Azure Blob Storage containerClient.create'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    CreateBucketRequest|CreateBucketResponse
steps:
  - description: "Migrate s3client with restoreObject API to Azure Blob Storage blob copy"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: CreateBucketRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - CreateBucketRequest.Builder bucket​(String bucket)
            Description: The name of the bucket to create.
            Parameters:
              - bucket - The name of the bucket to create.
            Returns:
              - Returns a reference to this object so that method calls can be chained together.

      Interface: CreateBucketResponse.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods: No useful methods.

      Class: BlobContainerClient
        Description: Client to a container. It may only be instantiated through a BlobContainerClientBuilder or via the method getBlobContainerClient(String containerName). This class does not hold any state about a particular container but is instead a convenient way of sending off appropriate requests to the resource on the service. It may also be used to construct URLs to blobs. This client contains operations on a container. Operations on a blob are available on BlobClient through getBlobClient(String blobName), and operations on the service are available on BlobServiceClient.
        Package: com.azure.storage.blob
        Methods:
          - void create()
            Description: Creates a new container within a storage account. If a container with the same name already exists, the operation fails.
            Parameters: N/A
            Returns: N/A
          - boolean createIfNotExists()
            Description: Creates a new container within a storage account if it does not exist.
            Parameters: N/A
            Returns: true if container is successfully created, false if container already exists.

name: 'Migrate S3client deleteBucket to Azure Blob Storage containerClient.delete'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    DeleteBucketRequest|DeleteBucketResponse
steps:
  - description: "Migrate s3client with restoreObject API to Azure Blob Storage blob copy"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: DeleteBucketRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - DeleteBucketRequest.Builder bucket​(String bucket)
            Description: Specifies the bucket being deleted.
            Parameters:
              - bucket - Specifies the bucket being deleted.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: DeleteBucketResponse.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods: No useful methods

      Class: BlobContainerClient
        Description: Client to a container. It may only be instantiated through a BlobContainerClientBuilder or via the method getBlobContainerClient(String containerName). This class does not hold any state about a particular container but is instead a convenient way of sending off appropriate requests to the resource on the service. It may also be used to construct URLs to blobs. This client contains operations on a container. Operations on a blob are available on BlobClient through getBlobClient(String blobName), and operations on the service are available on BlobServiceClient.
        Package: com.azure.storage.blob
        Methods:
          - void delete()
            Description: Marks the specified container for deletion. The container and any blobs contained within it are later deleted during garbage collection.
            Parameters: N/A
            Returns: N/A
          - boolean deleteIfExists()
            Description: Marks the specified container for deletion if it exists. The container and any blobs contained within it are later deleted during garbage collection.
            Parameters: N/A
            Returns: true if container is successfully deleted, false if container does not exist.

name: 'Migrate S3client deleteObject(s) to Azure Blob Storage deleteBlobs'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    DeleteObjectRequest|DeleteObjectResponse|DeleteObjectsRequest|DeleteObjectsResponse
steps:
  - description: "Migrate s3client with deleteObject(s) API to Azure Blob Storage deleteBlobs"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      You should pay attention that only the BlobBatchClient can do multiple blob deletes via function deleteBlobs.
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: DeleteObjectRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - DeleteObjectRequest.Builder bucket​(String bucket)
            Description: The bucket name of the bucket containing the object.
            Parameters:
              - bucket - The bucket name of the bucket containing the object.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - DeleteObjectRequest.Builder key(String key)
            Description: Key name of the object to delete.
            Parameters:
              - key - Key name of the object to delete.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - DeleteObjectRequest.Builder versionId​(String versionId)
            Description: Version ID used to reference a specific version of the object.
            Parameters:
              - versionId - Version ID used to reference a specific version of the object.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: DeleteObjectResponse.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - DeleteObjectResponse.Builder deleteMarker​(Boolean deleteMarker)
            Description: Indicates whether the specified object version that was permanently deleted was (true) or was not (false) a delete marker before deletion. In a simple DELETE, this header indicates whether (true) or not (false) the current version of the object is a delete marker.
            Parameters:
              - deleteMarker - Indicates whether the specified object version that was permanently deleted was (true) or was not (false) a delete marker before deletion. In a simple DELETE, this header indicates whether (true) or not (false) the current version of the object is a delete marker.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - DeleteObjectResponse.Builder versionId​(String versionId)
            Description: Returns the version ID of the delete marker created as a result of the DELETE operation.
            Parameters:
              - versionId - Returns the version ID of the delete marker created as a result of the DELETE operation.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: DeleteObjectsRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - DeleteObjectsRequest.Builder bucket​(String bucket)
            Description: The bucket name containing the objects to delete.
            Parameters:
              - bucket - The bucket name containing the objects to delete.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - DeleteObjectsRequest.Builder delete​(Delete delete)
            Description: Container for the request.
            Parameters:
              - delete - Container for the request.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Class: Delete
        Description: Container for the objects to delete.
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - Delete.Builder builder()
          - List<ObjectIdentifier> objects()
            Description: The object to delete.
            Parameters: N/A
            Returns: The object to delete.

      Interface: DeleteObjectsResponse.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - DeleteObjectsResponse.Builder deleted​(Collection<DeletedObject> deleted)
            Description: Container element for a successful delete. It identifies a collection of objects that was successfully deleted.
            Parameters:
              - deleted - Container element for a successful delete. It identifies a collection of objects that was successfully deleted.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - DeleteObjectsResponse.Builder deleted​(DeletedObject... deleted)
            Description: Container element for a successful delete. It identifies the object that was successfully deleted.
            Parameters:
              - deleted - Container element for a successful delete. It identifies the object that was successfully deleted.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - DeleteObjectsResponse.Builder errors​(Collection<S3Error> errors)
            Description: Container for a failed delete action that describes the object that Amazon S3 attempted to delete and the error it encountered.
            Parameters:
              - errors - Container for a failed delete action that describes the object that Amazon S3 attempted to delete and the error it encountered.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - DeleteObjectsResponse.Builder errors​(S3Error... errors)
            Description: Container for a failed delete action that describes the object that Amazon S3 attempted to delete and the error it encountered.
            Parameters:
              - errors - Container for a failed delete action that describes the object that Amazon S3 attempted to delete and the error it encountered.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Class: DeletedObject
        Description: Information about the deleted object.
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - Boolean deleteMarker()
            Description: Indicates whether the specified object version that was permanently deleted was (true) or was not (false) a delete marker before deletion. In a simple DELETE, this header indicates whether (true) or not (false) the current version of the object is a delete marker.
            Parameters: N/A
            Returns: Indicates whether the specified object version that was permanently deleted was (true) or was not (false) a delete marker before deletion. In a simple DELETE, this header indicates whether (true) or not (false) the current version of the object is a delete marker.
          - String key()
            Description: The name of the deleted object.
            Parameters: N/A
            Returns: The name of the deleted object.
          - String versionId()
            Description: This functionality is not supported for directory buckets.
            Parameters: N/A
            Returns: This functionality is not supported for directory buckets.

      Class: BlobBatchClient
        Description: This class provides a client that contains all operations that apply to Azure Storage Blob batching.This client offers the ability to delete and set access tier on multiple blobs at once and to submit a BlobBatch.
        Package: com.azure.storage.blob.batch
        Methods:
          - PagedIterable> deleteBlobs(List blobUrls, DeleteSnapshotsOptionType deleteOptions)
            Description: Delete multiple blobs in a single request to the service.
            Parameters:
              - blobUrls - Urls of the blobs to delete. Blob names must be encoded to UTF-8.
              - deleteOptions - The deletion option for all blobs.
            Returns: The status of each delete operation.

      Enum: DeleteSnapshotsOptionType
        Package: com.azure.storage.blob.models
        Description: Defines values for DeleteSnapshotsOptionType.
        Fields:
          - INCLUDE
          - ONLY

      Class: BlobClientBase
        Description: This class provides a client that contains all operations that apply to any blob type.
        Note: `The package of `BlobClient` is com.azure.storage.blob and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here.
        Package: com.azure.storage.blob.specialized
        Methods:
          - void delete()
            Description: Deletes the specified blob or snapshot. To delete a blob with its snapshots use deleteWithResponse(DeleteSnapshotsOptionType deleteBlobSnapshotOptions, BlobRequestConditions requestConditions, Duration timeout, Context context) and set DeleteSnapshotsOptionType to INCLUDE.
            Parameters: N/A
            Returns: N/A
          - public boolean deleteIfExists()
            Description: Deletes the specified blob or snapshot if it exists. To delete a blob with its snapshots use deleteIfExistsWithResponse(DeleteSnapshotsOptionType deleteBlobSnapshotOptions, BlobRequestConditions requestConditions, Duration timeout, Context context) and set DeleteSnapshotsOptionType to INCLUDE.
            Parameters: N/A
            Returns: true if delete succeeds, or false if blob does not exist.

name: 'Migrate S3 exceptions to Azure Blob Storage exceptions'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    BucketAlreadyExistsException|InvalidWriteOffsetException|NoSuchBucketException|NoSuchKeyException
steps:
  - description: "Migrate S3 exceptions to Azure Blob Storage exceptions"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Below are the exception related APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Class: BucketAlreadyExistsException extends S3Exception
        Description: The requested bucket name is not available. The bucket namespace is shared by all users of the system. Select a different name and try again.
        Package: software.amazon.awssdk.services.s3.model

      Class: InvalidRequestException extends S3Exception
        Description: You may receive this error in multiple cases. Depending on the reason for the error, you may receive one of the messages below:
          - Cannot specify both a write offset value and user-defined object metadata for existing objects.
          - Checksum Type mismatch occurred, expected checksum Type: sha1, actual checksum Type: crc32c.
          - Request body cannot be empty when 'write offset' is specified.

      Class: InvalidWriteOffsetException extends S3Exception
        Description: The write offset value that you specified does not match the current object size.
        Package: software.amazon.awssdk.services.s3.model

      Class: NoSuchBucketException extends S3Exception
        Description: The specified bucket does not exist.
        Package: software.amazon.awssdk.services.s3.model

      Class: NoSuchKeyException extends S3Exception
        Description: The specified key does not exist.
        Package: software.amazon.awssdk.services.s3.model

      Class: S3Exception extends AwsServiceException
        Package: software.amazon.awssdk.services.s3.model

      Class: AwsServiceException
        Description: AwsServiceException provides callers several pieces of information that can be used to obtain more information about the error and why it occurred.
        Package: software.amazon.awssdk.awscore.exception.AwsServiceException
        Methods:
          - public String getMessage()

      Class: BlobErrorCode
        Description: Error codes returned by the service.
        Package: com.azure.storage.blob.models
        Fields:
          - public static final BlobErrorCode CONTAINER_ALREADY_EXISTS
          - public static final BlobErrorCode INVALID_BLOB_OR_BLOCK
          - public static final BlobErrorCode APPEND_POSITION_CONDITION_NOT_MET
          - public static final BlobErrorCode CONTAINER_NOT_FOUND
          - public static final BlobErrorCode BLOB_NOT_FOUND

name: 'Migrate S3client getObject to Azure Blob Storage download'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    GetObjectRequest|getObject
steps:
  - description: "Migrate s3client with getObject API to Azure Blob Storage download"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      Pay attention to the download scenario with range specified, you should try to use APIs like downloadStreamWithResponse in which you can specific the range parameter.
      Note:
        1. Leverage downloadToFile method to download a blob to a file. Don't create your own api.
        2. `The package of `BlobClient` is com.azure.storage.blob and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here.
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: S3Client
        Package: software.amazon.awssdk.services.s3
        Methods:
          - default ResponseInputStream<GetObjectResponse> getObject​(GetObjectRequest getObjectRequest) throws NoSuchKeyException, InvalidObjectStateException, AwsServiceException, SdkClientException, S3Exception
            Description: Retrieves an object from Amazon S3.
            Details: Specify the full key name for the object in the GetObject request.
            Parameters:
            - getObjectRequest

      Class: GetObjectRequest
        Package:software.amazon.awssdk.services.s3.model
        Methods:
          - public static GetObjectRequest.Builder builder()

      Interface: GetObjectRequest.Builder
        Methods:
          - GetObjectRequest.Builder bucket(String bucket)
            Description: The bucket name containing the object.
            Parameters:
            - bucket: The bucket name containing the object.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - GetObjectRequest.Builder key(String key)
            Description: Key of the object to get.
            Parameters:
            - key: Key of the object to get.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - GetObjectRequest.Builder range​(String range)
            Description: Downloads the specified byte range of an object. For more information about the HTTP Range header, see https://www.rfc-editor.org/rfc/rfc9110.html#name -range.
            Parameters:
            - range - Downloads the specified byte range of an object. For more information about the HTTP Range header, see https://www.rfc-editor.org/rfc/rfc9110 .html#name-range.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Class BlobServiceClient
        Package: com.azure.storage.blob
        Methods:
          - public BlobContainerClient getBlobContainerClient(String containerName)
            Description: Initializes a BlobContainerClient object pointing to the specified container. This method does not create a container. It simply constructs the URL to the container and offers access to methods relevant to containers.
            Parameters:
            - containerName: The name of the container to point to.
            Returns: A BlobContainerClient object pointing to the specified container.

      Class BlobContainerClient
        Package: com.azure.storage.blob
        Methods:
        - public BlobClient getBlobClient(String blobName)
          Description: Initializes a new BlobClient object by concatenating blobName to the end of ContainerAsyncClient's URL. The new BlobClient uses the same request policy pipeline as the ContainerAsyncClient.
          Parameters:
          - blobName: A String representing the name of the blob. If the blob name contains special characters, pass in the url encoded version of the blob name.
          Returns: A new BlobClient object which references the blob with the specified name in this container.
        - public boolean exists()
          Description: Gets if the container this client represents exists in the cloud.
          Returns: true if the container exists, false if it doesn't

      Class: BlobClient
        Package: com.azure.storage.blob
        Note: `The package of `BlobClient` is com.azure.storage.blob and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here.
        Methods:
          - public BinaryData downloadContent()
            Description: Downloads the entire blob. This method supports downloads up to 2GB of data. Content will be buffered in memory. If the blob is larger, use downloadStream(OutputStream stream) to download larger blobs.
            Returns: The content of the blob.
          - public void downloadStream(OutputStream stream)
            Description: Downloads the entire blob into an output stream.
            Parameters:
              - stream: A non-null OutputStream instance where the downloaded data will be written.
          - public BlobDownloadResponse downloadStreamWithResponse(OutputStream stream, BlobRange range, DownloadRetryOptions options, BlobRequestConditions requestConditions, boolean getRangeContentMd5, Duration timeout, Context context)
            Description: Downloads a range of bytes from a blob into an output stream.
            Parameters:
              - stream - A non-null OutputStream instance where the downloaded data will be written.
              - range - BlobRange
              - options - DownloadRetryOptions
              - requestConditions - BlobRequestConditions
              - getRangeContentMd5 - Whether the contentMD5 for the specified blob range should be returned.
              - timeout - An optional timeout value beyond which a RuntimeException will be raised.
              - context - Additional context that is passed through the Http pipeline during the service call.
            Returns: A response containing status code and HTTP headers.
          - public BlobProperties downloadToFile(String filePath, boolean overwrite)
            Description: Downloads the entire blob into a file specified by the path. If overwrite is set to false, the file will be created and must not exist, if the file already exists a FileAlreadyExistsException will be thrown.
            Parameters:
              - filePath: A String representing the filePath where the downloaded data will be written.
              - overwrite: Whether to overwrite the file, should the file exist.
            Returns: The blob properties and metadata.
          - public BlobDownloadContentResponse downloadContentWithResponse(DownloadRetryOptions options, BlobRequestConditions requestConditions, BlobRange range, boolean getRangeContentMd5, Duration timeout, Context context)
            Description: Downloads a range of bytes from a blob into an output stream.
            Parameters:
              - options - DownloadRetryOptions
              - requestConditions - BlobRequestConditions
              - range - BlobRange
              - getRangeContentMd5 - Whether the contentMD5 for the specified blob range should be returned.
              - timeout - An optional timeout value beyond which a RuntimeException will be raised.
              - context - Additional context that is passed through the Http pipeline during the service call.

      Class: BlobRange
        Package: com.azure.storage.blob.models
        Description: This is a representation of a range of bytes on a blob, typically used during a download operation.
        Constructors:
          - public BlobRange(long offset)
          - public BlobRange(long offset, Long count)

      class: BlobDownloadToFileOptions
        Package: com.azure.storage.blob.options
        Description: Extended options that may be passed when downloading a blob to a file.
        Methods:
          - public BlobDownloadToFileOptions setDownloadRetryOptions(DownloadRetryOptions downloadRetryOptions)
            Description: set download retry options
            Parameters:
              - downloadRetryOptions - DownloadRetryOptions
            Returns: The updated options.
          - public BlobDownloadToFileOptions setRange(BlobRange range)
            Parameters:
              - range - BlobRange
            Returns: The updated options.

name: 'Migrate S3 gradle dependency to Azure Blob Storage gradle dependency'
description: "Converts Amazon S3 Gradle dependencies to Azure Blob Storage dependencies"
codeLocation:
  type: textsearch
  filePattern: '**/build.gradle'
  codePattern: >-
    software.amazon.awssdk:s3|io.awspring.cloud:spring-cloud-aws-starter-s3|com.amazonaws:aws-java-sdk-s3

steps:
  - description: "Migrate S3 gradle dependency to Azure Blob Storage gradle dependency"
    type: "instruction"
    content: |
      Your task is to migrate a Gradle build file from using the Amazon S3 API dependencies to the Azure Storage Blob API dependencies.
      Pay attention that, you should only update the specific dependency declarations and keep the rest of the file, you cannot replace the whole file. What you return must be a valid, complete Gradle build file.
      Below are some references for you, please replace the dependencies in the Gradle file accordingly.
      Please note that the three Azure-related dependencies should all be provided: one for the blob operations, one for batch operations, and one for authentication credentials.

      S3 related dependencies (could appear in any of these formats):
      ```gradle
      implementation 'software.amazon.awssdk:s3:X.Y.Z'
      implementation 'io.awspring.cloud:spring-cloud-aws-starter-s3:X.Y.Z'
      implementation 'com.amazonaws:aws-java-sdk-s3:X.Y.Z'
      ```

      Or in Kotlin DSL format:
      ```kotlin
      implementation("software.amazon.awssdk:s3:X.Y.Z")
      implementation("io.awspring.cloud:spring-cloud-aws-starter-s3:X.Y.Z")
      implementation("com.amazonaws:aws-java-sdk-s3:X.Y.Z")
      ```

      Azure Blob Storage dependencies to use as replacements:
      ```gradle
      implementation platform('com.azure:azure-sdk-bom:1.2.36')

      implementation 'com.azure:azure-storage-blob'
      implementation 'com.azure:azure-storage-blob-batch'
      implementation 'com.azure:azure-identity'
      ```

      Or in Kotlin DSL format:
      ```kotlin
      implementation(platform("com.azure:azure-sdk-bom:1.2.36"))

      implementation("com.azure:azure-storage-blob")
      implementation("com.azure:azure-storage-blob-batch")
      implementation("com.azure:azure-identity:1.16.3")
      ```

name: 'Migrate S3client headBucket to Azure Blob Storage'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    headBucket|HeadBucketRequest|HeadBucketResponse

steps:
  - description: "Migrate s3client with headBucket API to Azure Blob Storage BlobContainerClient.getProperties()"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: S3Client
        Package: software.amazon.awssdk.services.s3
        Methods:
        - default HeadBucketResponse headBucket​(HeadBucketRequest headBucketRequest) throws NoSuchBucketException, AwsServiceException, SdkClientException, S3Exception
          Description: You can use this operation to determine if a bucket exists and if you have permission to access it. The action returns a 200 OK if the bucket exists and you have permission to access it. If the bucket does not exist or you do not have permission to access it, the HEAD request returns a generic 400 Bad Request, 403 Forbidden or 404 Not Found code. A message body is not included, so you cannot determine the exception beyond these HTTP response codes. You must make requests for this API operation to the Zonal endpoint. These endpoints support virtual-hosted-style requests in the format https://bucket-name.s3express-zone-id.region-code.amazonaws.com. Path-style requests are not supported.
          Parameters:
          - headBucketRequest:
          Returns: Result of the HeadBucket operation returned by the service.

      Class: HeadBucketRequest
        Package: software.amazon.awssdk.services.s3.model
        Methods:
        - public final String bucket()
          Description: The bucket name.
          Returns: The bucket name.

      Class: HeadBucketResponse
        Package: software.amazon.awssdk.services.s3.model
        Methods:
        - public final String bucketRegion()
          Description: The Region that the bucket is located.
          Returns: The Region that the bucket is located.

      Class BlobContainerClient
        Package: com.azure.storage.blob
        Methods:
        - public BlobContainerProperties getProperties()
          Description: Returns the container's metadata and system properties.
          Returns: The container properties.
        - public Response getPropertiesWithResponse(String leaseId, Duration timeout, Context context)
          Description: Returns the container's metadata and system properties.
          Parameters:
          - leaseId: The lease ID the active lease on the container must match.
          - timeout: An optional timeout value beyond which a RuntimeException will be raised.
          -context: Additional context that is passed through the Http pipeline during the service call.
          Returns: The container properties.

name: 'Migrate S3client headObject to Azure Blob Storage getProperties'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    HeadObjectRequest|HeadObjectResponse
steps:
  - description: "Migrate s3client with headObject API to Azure Blob Storage getProperties"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: HeadObjectRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - HeadObjectRequest.Builder	bucket​(String bucket)
            Description: The name of the bucket that contains the object.
            Parameters:
              - bucket - The name of the bucket that contains the object.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - HeadObjectRequest.Builder	bucket​(String bucket)
            Description: The object key.
            Parameters:
              - bucket - The object key.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - HeadObjectRequest.Builder versionId​(String versionId)
            Description: Version ID used to reference a specific version of the object.
            Parameters:
              - versionId - Version ID used to reference a specific version of the object.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Class: HeadObjectResponse
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - Long contentLength()
            Description: Returns Size of the body in bytes.
            Parameters: N/A
            Returns: Size of the body in bytes.
          - String eTag()
            Description: An entity tag (ETag) is an opaque identifier assigned by a web server to a specific version of a resource found at a URL.
            Parameters: N/A
            Returns: An entity tag (ETag) is an opaque identifier assigned by a web server to a specific version of a resource found at a URL.
          - String versionId()
            Description: Version ID of the object.
            Parameters: N/A
            Returns: Version ID of the object.

      Class: BlobClientBase
        Package: com.azure.storage.blob.specialized
        Note: `The package of `BlobClient` is com.azure.storage.blob and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here.
        Methods:
          - BlobProperties getProperties()
            Description: Returns the blob's metadata and properties.
            Parameters: N/A
            Returns: The blob properties and metadata.

      Class: BlobProperties
        Package: com.azure.storage.blob.models
        Methods:
          - long getBlobSize()
            Description: Returns the size of the blob in bytes
            Parameters: N/A
            Returns: The size of the blob in bytes
          - String getETag()
            Description: Returns the eTag of the blob
            Parameters: N/A
            Returns: The eTag of the blob
          - String String getVersionId()
            Description: Returns the version identifier the blob.
            Parameters: N/A
            Returns: Returns the version identifier the blob.

name: 'Migrate S3client listBuckets to Azure Blob Storage BlobServiceClient.listBlobContainers'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    ListBucketsRequest|ListBucketsResponse|listBuckets
steps:
  - description: "Migrate S3client listBuckets to Azure Blob Storage BlobServiceClient.listBlobContainers"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface ListBucketsRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - ListBucketsRequest.Builder bucketRegion​(String bucketRegion)
            Description: Limits the response to buckets that are located in the specified Amazon Web Services Region. The Amazon Web Services Region must be expressed according to the Amazon Web Services Region code, such as us-west-2 for the US West (Oregon) Region. For a list of the valid values for all of the Amazon Web Services Regions, see Regions and Endpoints. Requests made to a Regional endpoint that is different from the bucket-region parameter are not supported. For example, if you want to limit the response to your buckets in Region us-west-2, the request must be made to an endpoint in Region us-west-2.
            Parameters:
              - bucketRegion: Limits the response to buckets that are located in the specified Amazon Web Services Region. The Amazon Web Services Region must be expressed according to the Amazon Web Services Region code, such as us-west-2 for the US West (Oregon) Region. For a list of the valid values for all of the Amazon Web Services Regions, see Regions and Endpoints.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - ListBucketsRequest.Builder maxBuckets​(Integer maxBuckets)
            Description: Maximum number of buckets to be returned in response. When the number is more than the count of buckets that are owned by an Amazon Web Services account, return all the buckets in response.
            Parameters:
              - maxBuckets： Maximum number of buckets to be returned in response. When the number is more than the count of buckets that are owned by an Amazon Web Services account, return all the buckets in response.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - ListBucketsRequest.Builder prefix​(String prefix)
            Description: Limits the response to bucket names that begin with the specified bucket name prefix.
            Parameters:
            - prefix: Limits the response to bucket names that begin with the specified bucket name prefix.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: S3Client
        Package: software.amazon.awssdk.services.s3
        Methods:
          - default ListBucketsResponse listBuckets() throws AwsServiceException, SdkClientException, S3Exception
            Description: Returns a list of all buckets owned by the authenticated sender of the request. To grant IAM permission to use this operation, you must add the s3:ListAllMyBuckets policy action.
            Returns: Result of the ListBuckets operation returned by the service.
          - default ListBucketsResponse listBuckets​(ListBucketsRequest listBucketsRequest) throws AwsServiceException, SdkClientException, S3Exception
            Description: Returns a list of all buckets owned by the authenticated sender of the request. To grant IAM permission to use this operation, you must add the s3:ListAllMyBuckets policy action.
            Returns: Result of the ListBuckets operation returned by the service.

      Class: BlobServiceClient
        Package: com.azure.storage.blob
        Methods:
          - public PagedIterable<BlobContainerItem> listBlobContainers()
            Description: Returns a lazy loaded list of BlobContainerItem in this account.
            Parameters: N/A
            Returns: The list of containers.
          - public PagedIterable<BlobContainerItem> listBlobContainers(ListBlobContainersOptions options, Duration timeout)
            Description: Returns a lazy loaded list of BlobContainerItem in this account.
            Parameters:
              - options - A `ListBlobContainersOptions` which specifies what data should be returned by the service. If iterating by page, the page size passed to byPage methods such as PagedIterable#iterableByPage(int) will be preferred over the value set on these options.
              - timeout - An optional timeout value beyond which a RuntimeException will be raised.
            Returns: The list of BlobContainerItem.

      Class: BlobContainerItem
        Package: com.azure.storage.blob.models
        Methods:
          - public Map<String, String> getMetadata()
            Description: Get the metadata property.
            Parameters: N/A
            Returns: the metadata value.
          - public String getName()
            Description: Get the name property
            Parameters: N/A
            Returns: the name value.
          - public BlobContainerItemProperties getProperties()
            Description: Get the properties property
            Parameters: N/A
            Returns: the properties value.
          - public Boolean isDeleted()
            Description: Get the deleted property
            Parameters: N/A
            Returns: the deleted value.
          - public BlobContainerItem setDeleted(Boolean deleted)
            Description: Set the deleted property
            Parameters:
              - deleted - the deleted value to set.
            Returns: the BlobContainerItem object itself.
          - public BlobContainerItem setMetadata(Map metadata)
            Description: Set the metadata property
            Parameters:
              - metadata - the metadata value to set.
            Returns: the BlobContainerItem object itself.
          - public BlobContainerItem setName(String name)
            Description: Set the name property
            Parameters:
              - name - the name value to set.
            Returns: the BlobContainerItem object itself.
          - public BlobContainerItem setProperties(BlobContainerItemProperties properties)
            Description: Set the properties property
            Parameters:
              - properties - the properties value to set.
            Returns: the BlobContainerItem object itself.

      Class: ListBlobContainersOptions
        Package: com.azure.storage.blob.models
        Methods:
          - public BlobContainerListDetails getDetails()
            Description: Returns the details of the ListBlobContainersOptions
            Parameters: N/A
            Returns: Returns the details of the ListBlobContainersOptions
          - public Integer getMaxResultsPerPage()
            Description: Specifies the maximum number of blobs to return, including all BlobPrefix elements. If the request does not specify maxResultsPerPage or specifies a value greater than 5,000, the server will return up to 5,000 items.
            Parameters: N/A
            Returns: the number of containers to be returned in a single response
          - public String getPrefix()
            Description: Filters the results to return only blobs whose names begin with the specified prefix.
            Parameters: N/A
            Returns: the prefix a container must start with to be returned
          - public ListBlobContainersOptions setDetails(BlobContainerListDetails details)
            Description: Set the details
            Parameters:
              - details - The details for listing specific containers
            Returns: the updated ListBlobContainersOptions object
          - public ListBlobContainersOptions setMaxResultsPerPage(Integer maxResultsPerPage)
            Description: Specifies the maximum number of blobs to return, including all BlobPrefix elements. If the request does not specify maxResultsPerPage or specifies a value greater than 5,000, the server will return up to 5,000 items.
            Parameters:
              - maxResultsPerPage - The number of containers to return in a single response
            Returns: the updated ListBlobContainersOptions object
          - public ListBlobContainersOptions setPrefix(String prefix)
            Description: Filters the results to return only blobs whose names begin with the specified prefix.
            Parameters:
              - prefix - The prefix that a container must match to be returned
            Returns: the updated ListBlobContainersOptions object

name: 'Migrate S3client listObject to Azure Blob Storage listBlobs'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    ListObjectsV2Request|ListObjectsV2

steps:
  - description: "Migrate s3client with listObjects API to Azure Blob Storage listBlobs"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.

      Note:
        1. You should pay special attention to list requests that has filters, you can use the ListBlobsOptions class to achieve more during list operation.
        2. List APIs in Azure Storage Blob side don't need to control the page logic or continuationToken. It's take cared by SDK itself.
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: S3Client
        Package: software.amazon.awssdk.services.s3
        Methods:
        - default ListObjectsV2Response listObjectsV2(ListObjectsV2Request listObjectsV2Request) throws NoSuchBucketException, AwsServiceException, SdkClientException, S3Exception
          Description: Returns some or all (up to 1,000) of the objects in a bucket with each request. You can use the request parameters as selection criteria to return a subset of the objects in a bucket. A 200 OK response can contain valid or invalid XML. Make sure to design your application to parse the contents of the response and handle it appropriately.
          Parameters:
            - listObjectsV2Request:
          Returns: Result of the ListObjectsV2 operation returned by the service.

      Class: ListObjectsV2Request
        Package:software.amazon.awssdk.services.s3.model
        Methods:
          - public static ListObjectsV2Request.Builder builder()

      Class: ListObjectsV2Response
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - List<S3Object> contents()
            Description: Metadata about each object returned. Attempts to modify the collection returned by this method will result in an UnsupportedOperationException. This method will never return null. If you would like to know whether the service returned this field (so that you can differentiate between null and empty), you can use the hasContents() method.
            Returns: Metadata about each object returned.
          - public final String name()
            Description: The bucket name.
            Returns: The bucket name.
          - public final String prefix()
            Description: Keys that begin with the indicated prefix.
            Returns: Keys that begin with the indicated prefix.
          - public final String delimiter()
            Description: Causes keys that contain the same string between the prefix and the first occurrence of the delimiter to be rolled up into a single result element in the CommonPrefixes collection. These rolled-up keys are not returned elsewhere in the response. Each rolled-up result counts as only one return against the MaxKeys value.
            Returns: Causes keys that contain the same string between the prefix and the first occurrence of the delimiter to be rolled up into a single result element in the CommonPrefixes collection. These rolled-up keys are not returned elsewhere in the response. Each rolled-up result counts as only one return against the MaxKeys value.

      Interface: ListObjectsV2Request.Builder
        Methods:
          - ListObjectsV2Request.Builder bucket(String bucket)
            Description: The bucket name to which the PUT action was initiated.
            Parameters:
            - bucket: Directory buckets - When you use this operation with a directory bucket, you must use virtual-hosted-style requests in the format Bucket-name.s3express-zone-id.region-code.amazonaws.com. Path-style requests are not supported. Directory bucket names must be unique in the chosen Zone (Availability Zone or Local Zone). Bucket names must follow the format bucket-base-name--zone-id--x-s3 (for example, DOC-EXAMPLE-BUCKET--usw2-az1--x-s3). For information about bucket naming restrictions, see Directory bucket naming rules in the Amazon S3 User Guide.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - ListObjectsV2Request.Builder delimiter(String delimiter)
            Description: A delimiter is a character that you use to group keys.
            Parameters:
            - delimiter: A delimiter is a character that you use to group keys.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - ListObjectsV2Request.Builder maxKeys(Integer maxKeys)
            Description: Sets the maximum number of keys returned in the response. By default, the action returns up to 1,000 key names. The response might contain fewer keys but will never contain more.
            Parameters:
            - maxKeys: Sets the maximum number of keys returned in the response. By default, the action returns up to 1,000 key names. The response might contain fewer keys but will never contain more.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - ListObjectsV2Request.Builder prefix(String prefix)
            Description: Limits the response to keys that begin with the specified prefix.
            Parameters:
            - prefix: Limits the response to keys that begin with the specified prefix.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - public final String continuationToken()
            Description: ContinuationToken indicates to Amazon S3 that the list is being continued on this bucket with a token. ContinuationToken is obfuscated and is not a real key. You can use this ContinuationToken for pagination of the list results.
            Returns: ContinuationToken indicates to Amazon S3 that the list is being continued on this bucket with a token. ContinuationToken is obfuscated and is not a real key. You can use this ContinuationToken for pagination of the list results.

      Class BlobServiceClient
        Package: com.azure.storage.blob
        Methods:
          - public BlobContainerClient getBlobContainerClient(String containerName)
            Description: Initializes a BlobContainerClient object pointing to the specified container. This method does not create a container. It simply constructs the URL to the container and offers access to methods relevant to containers.
            Parameters:
            - containerName: The name of the container to point to.
            Returns: A BlobContainerClient object pointing to the specified container.

      Class BlobContainerClient
        Package: com.azure.storage.blob
        Methods:
        - public BlobClient getBlobClient(String blobName)
          Description: Initializes a new BlobClient object by concatenating blobName to the end of ContainerAsyncClient's URL. The new BlobClient uses the same request policy pipeline as the ContainerAsyncClient.
          Parameters:
          - blobName: A String representing the name of the blob. If the blob name contains special characters, pass in the url encoded version of the blob name.
          Returns: A new BlobClient object which references the blob with the specified name in this container.
        - public PagedIterable<BlobItem> listBlobs()
          Descriptions: Returns a lazy loaded list of blobs in this container, with folder structures flattened. The returned PagedIterable<T> can be consumed through while new items are automatically retrieved as needed.
          Parameters: None
          Returns: The listed blobs, flattened. Blob names are returned in lexicographic order.
        - public PagedIterable<BlobItem> listBlobs(ListBlobsOptions options, String continuationToken, Duration timeout)
          Descriptions: Returns a lazy loaded list of blobs in this container, with folder structures flattened. The returned PagedIterable<T> can be consumed through while new items are automatically retrieved as needed.
          Parameters:
          - options: A ListBlobsOptions object. If iterating by page, the page size passed to byPage methods,
            such as PagedIterable#iterableByPage(int), will be preferred over the value set in these options.
          - continuationToken: A String identifying the portion of the list to be returned with the next list operation.
          - timeout: A Duration specifying an optional timeout value. If the operation exceeds this duration,
            a RuntimeException will be raised.
          Returns: A PagedIterable containing the listed blobs, flattened.
        - public PagedIterable<BlobItem> listBlobs(ListBlobsOptions options, Duration timeout)
          Description: Returns a lazy-loaded list of blobs in this container, with folder structures flattened. The returned PagedIterable<T> can be consumed while new items are automatically retrieved as needed. Blob names are returned in lexicographic order.
          Parameters:
          - options: A ListBlobsOptions object. If iterating by page, the page size passed to byPage methods,
            such as PagedIterable#iterableByPage(int), will be preferred over the value set in these options.
          - timeout: A Duration specifying an optional timeout value. If the operation exceeds this duration,
            a RuntimeException will be raised.
          Returns: A PagedIterable containing the listed blobs, flattened.

      Class ListBlobsOptions
        Package: com.azure.storage.blob.models
        Methods:
        - public ListBlobsOptions setDetails(BlobListDetails details)
          Parameters:
          - details: The details for listing specific blobs.
          Returns: The updated ListBlobsOptions object.
        - public ListBlobsOptions setMaxResultsPerPage(Integer maxResultsPerPage)
          Description: Specifies the maximum number of blobs to return, including all BlobPrefix elements. If the request does not specify maxResultsPerPage or specifies a value greater than 5,000, the server will return up to 5,000 items.
          Parameters:
          - maxResultsPerPage: The number of blobs to be returned in a single response.
          Returns: The updated ListBlobsOptions object.
        - public ListBlobsOptions setPrefix(String prefix)
          Description: Filters the results to return only blobs whose names begin with the specified prefix. May be null to return all blobs.
          Parameters:
          - prefix: A prefix that a blob must match to be returned.
          Returns: The updated ListBlobsOptions object.

      Class BlobClient
        Package: com.azure.storage.blob
        Note: `The package of `BlobClient` is com.azure.storage.blob and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here.
        Methods:
        - public BlobProperties getProperties()
          Description: Returns the blob's metadata and properties.
          Returns: The blob properties and metadata.

name: 'Migrate S3client multipartUpload to Azure Blob Storage stageBlock'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    CompleteMultipartUploadRequest|CompleteMultipartUploadResponse|AbortMultipartUploadRequest|CreateMultipartUploadRequest|CreateMultipartUploadResponse|UploadPartRequest|UploadPartResponse

steps:
  - description: "Migrate s3client with multipartUpload API to Azure Blob Storage stageBlock"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      You should pay special attention that these blob related APIs should use BlockBlobClient to achieve, don't forget to import the package whenever you are adding a new class reference in code edit.
      Below are the APIs provided for your reference:

      Interface: CompleteMultipartUploadRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - CompleteMultipartUploadRequest.Builder bucket​(String bucket)
            Description: Name of the bucket to which the multipart upload was initiated.
            Parameters:
              - bucket - Name of the bucket to which the multipart upload was initiated.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - CompleteMultipartUploadRequest.Builder key​(String key)
            Description: Object key for which the multipart upload was initiated.
            Parameters:
              - key - Object key for which the multipart upload was initiated.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - CompleteMultipartUploadRequest.Builder mpuObjectSize​(Long mpuObjectSize)
            Description: The expected total object size of the multipart upload request. If there’s a mismatch between the specified object size value and the actual object size value, it results in an HTTP 400 InvalidRequest error.
            Parameters:
              - mpuObjectSize - The expected total object size of the multipart upload request.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - CompleteMultipartUploadRequest.Builder uploadId​(String uploadId)
            Description: ID for the initiated multipart upload.
            Parameters:
              - uploadId - ID for the initiated multipart upload.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: CompleteMultipartUploadResponse.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - CompleteMultipartUploadResponse.Builder bucket​(String bucket)
            Description: The name of the bucket that contains the newly created object. Does not return the access point ARN or access point alias if used.
            Parameters:
              - bucket - The name of the bucket that contains the newly created object. Does not return the access point ARN or access point alias if used.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - CompleteMultipartUploadResponse.Builder key​(String key)
            Description: The object key of the newly created object.
            Parameters:
              - key - The object key of the newly created object.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - CompleteMultipartUploadResponse.Builder expiration​(String expiration)
            Description: If the object expiration is configured, this will contain the expiration date (expiry-date) and rule ID (rule-id). The value of rule-id is URL-encoded.
            Parameters:
              - expiration - If the object expiration is configured, this will contain the expiration date ( expiry-date) and rule ID (rule-id). The value of rule-id is URL-encoded.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: AbortMultipartUploadRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - AbortMultipartUploadRequest.Builder bucket​(String bucket)
            Description: The bucket name to which the upload was taking place.
            Parameters:
              - bucket - The bucket name to which the upload was taking place.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - AbortMultipartUploadRequest.Builder key​(String key)
            Description: Key of the object for which the multipart upload was initiated.
            Parameters:
              - key - Key of the object for which the multipart upload was initiated.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - AbortMultipartUploadRequest.Builder uploadId​(String uploadId)
            Description: Upload ID that identifies the multipart upload.
            Parameters:
              - uploadId - Upload ID that identifies the multipart upload.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: CreateMultipartUploadRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - CreateMultipartUploadRequest.Builder bucket​(String bucket)
            Description: The name of the bucket where the multipart upload is initiated and where the object is uploaded.
            Parameters:
              - bucket - The name of the bucket where the multipart upload is initiated and where the object is uploaded.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - CreateMultipartUploadRequest.Builder key​(String key)
            Description: Object key for which the multipart upload is to be initiated.
            Parameters:
              - key - Object key for which the multipart upload is to be initiated.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - CreateMultipartUploadRequest.Builder expires​(Instant expires)
            Description: The date and time at which the object is no longer cacheable.
            Parameters:
              - expires - The date and time at which the object is no longer cacheable.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - CreateMultipartUploadRequest.Builder metadata​(Map<String,​String> metadata)
            Description: A map of metadata to store with the object in S3.
            Parameters:
              - metadata - A map of metadata to store with the object in S3.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: CreateMultipartUploadResponse.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - CreateMultipartUploadResponse.Builder bucket​(String bucket)
            Description: The name of the bucket to which the multipart upload was initiated. Does not return the access point ARN or access point alias if used.
            Parameters:
              - bucket - The name of the bucket to which the multipart upload was initiated.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - CreateMultipartUploadResponse.Builder key​(String key)
            Description: Object key for which the multipart upload was initiated.
            Parameters:
              - key - Object key for which the multipart upload was initiated.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - CreateMultipartUploadResponse.Builder uploadId​(String uploadId)
            Description: The date and time at which the object is no longer cacheable.
            Parameters:
              - uploadId - ID for the initiated multipart upload.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: UploadPartRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - UploadPartRequest.Builder bucket​(String bucket)
            Description: The name of the bucket to which the multipart upload was initiated.
            Parameters:
              - bucket - The name of the bucket to which the multipart upload was initiated.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - UploadPartRequest.Builder contentLength​(Long contentLength)
            Description: Size of the body in bytes. This parameter is useful when the size of the body cannot be determined automatically.
            Parameters:
              - contentLength - Size of the body in bytes. This parameter is useful when the size of the body cannot be determined automatically.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - UploadPartRequest.Builder key​(String key)
            Description: Object key for which the multipart upload was initiated.
            Parameters:
              - key - Object key for which the multipart upload was initiated.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - UploadPartRequest.Builder partNumber​(Integer partNumber)
            Description: Part number of part being uploaded. This is a positive integer between 1 and 10,000.
            Parameters:
              - partNumber - Part number of part being uploaded. This is a positive integer between 1 and 10,000.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - UploadPartRequest.Builder uploadId​(String uploadId)
            Description: Upload ID identifying the multipart upload whose part is being uploaded.
            Parameters:
              - uploadId - Upload ID identifying the multipart upload whose part is being uploaded.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Interface: UploadPartResponse.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - UploadPartResponse.Builder eTag​(String eTag)
            Description: Entity tag for the uploaded object.
            Parameters:
              - eTag - Entity tag for the uploaded object.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Class: BlockBlobClient extends BlobClientBase
        Description: Client to a block blob.
        Package: com.azure.storage.blob.specialized
        Methods:
          - public void stageBlock(String base64BlockId, BinaryData data)
            Description: Uploads the specified block to the block blob's "staging area" to be later committed by a call to commitBlockList.
            Parameters:
              - base64BlockId - A Base64 encoded String that specifies the ID for this block. Note that all block ids for a given blob must be the same length.
              - data - The data to write to the block. Note that this BinaryData must have defined length and must be replayable if retries are enabled
          - public void stageBlock(String base64BlockId, InputStream data, long length)
            Description: Uploads the specified block to the block blob's "staging area" to be later committed by a call to commitBlockList.
            Parameters:
              - base64BlockId - A Base64 encoded String that specifies the ID for this block. Note that all block ids for a given blob must be the same length.
              - data - The data to write to the block. The data must be markable. This is in order to support retries. If the data is not markable, consider using getBlobOutputStream() and writing to the returned OutputStream. Alternatively, consider wrapping your data source in a BufferedInputStream to add mark support.
              - length - The exact length of the data. It is important that this value match precisely the length of the data provided in the InputStream.
          - public Response stageBlockWithResponse(BlockBlobStageBlockOptions options, Duration timeout, Context context)
            Description: Uploads the specified block to the block blob's "staging area" to be later committed by a call to commitBlockList.
            Parameters:
              - options - BlockBlobStageBlockOptions
              - timeout - An optional timeout value beyond which a RuntimeException will be raised.
              - context - Additional context that is passed through the Http pipeline during the service call.
            Returns: A response containing status code and HTTP headers
          - public Response stageBlockWithResponse(String base64BlockId, InputStream data, long length, byte[] contentMd5, String leaseId, Duration timeout, Context context)
            Description: Uploads the specified block to the block blob's "staging area" to be later committed by a call to commitBlockList.
            Parameters:
              - base64BlockId - A Base64 encoded String that specifies the ID for this block. Note that all block ids for a given blob must be the same length.
              - data - The data to write to the block. The data must be markable. This is in order to support retries. If the data is not markable, consider using getBlobOutputStream() and writing to the returned OutputStream. Alternatively, consider wrapping your data source in a BufferedInputStream to add mark support.
              - length - The exact length of the data. It is important that this value match precisely the length of the data provided in the InputStream.
              - contentMd5 - An MD5 hash of the block content. This hash is used to verify the integrity of the block during transport. When this header is specified, the storage service compares the hash of the content that has arrived with this header value. Note that this MD5 hash is not stored with the blob. If the two hashes do not match, the operation will fail.
              - leaseId - The lease ID the active lease on the blob must match.
              - timeout - An optional timeout value beyond which a RuntimeException will be raised.
              - context - Additional context that is passed through the Http pipeline during the service call.
            Returns: A response containing status code and HTTP headers
          - public BlockBlobItem commitBlockList(List base64BlockIds)
            Description: Writes a blob by specifying the list of block IDs that are to make up the blob. In order to be written as part of a blob, a block must have been successfully written to the server in a prior stageBlock operation. You can call commitBlockList to update a blob by uploading only those blocks that have changed, then committing the new and existing blocks together. Any blocks not specified in the block list and permanently deleted.
            Parameters:
              - base64BlockIds - A list of base64 encode Strings that specifies the block IDs to be committed.
            Returns: The information of the block blob.
          - public BlockBlobItem commitBlockList(List base64BlockIds, boolean overwrite)
            Description: Writes a blob by specifying the list of block IDs that are to make up the blob. In order to be written as part of a blob, a block must have been successfully written to the server in a prior stageBlock operation. You can call commitBlockList to update a blob by uploading only those blocks that have changed, then committing the new and existing blocks together. Any blocks not specified in the block list and permanently deleted.
            Parameters:
              - base64BlockIds - A list of base64 encode Strings that specifies the block IDs to be committed.
              - overwrite - Whether to overwrite, should data exist on the blob.
            Returns: The information of the block blob.
          - public Response commitBlockListWithResponse(BlockBlobCommitBlockListOptions options, Duration timeout, Context context)
            Description: Writes a blob by specifying the list of block IDs that are to make up the blob. In order to be written as part of a blob, a block must have been successfully written to the server in a prior stageBlock operation. You can call commitBlockList to update a blob by uploading only those blocks that have changed, then committing the new and existing blocks together. Any blocks not specified in the block list and permanently deleted.
            Parameters:
              - options - BlockBlobCommitBlockListOptions
              - timeout - An optional timeout value beyond which a RuntimeException will be raised
              - context - Additional context that is passed through the Http pipeline during the service call

      Class: BlockBlobCommitBlockListOptions
        Description: Extended options that may be passed when committing a block list.
        Package: com.azure.storage.blob.options
        Methods:
          - public BlockBlobCommitBlockListOptions setHeaders(BlobHttpHeaders headers)
            Parameters:
              - headers - BlobHttpHeaders
            Returns: The updated options
          - public BlockBlobCommitBlockListOptions setMetadata(Map metadata)
            Parameters:
              - metadata - The metadata to associate with the blob.
            Returns: The updated options
          - public BlockBlobCommitBlockListOptions setTier(AccessTier tier)
            Parameters:
              - tier - AccessTier
            Returns: The updated options

      Class: BlockBlobStageBlockOptions
        Description: Extended options that may be passed when staging a block.
        Package: com.azure.storage.blob.options
        Methods:
          - public BlockBlobStageBlockOptions setContentMd5(byte[] contentMd5)
            Parameters:
              - contentMd5 - An MD5 hash of the block content. This hash is used to verify the integrity of the block during transport. When this header is specified, the storage service compares the hash of the content that has arrived with this header value. Note that this MD5 hash is not stored with the blob. If the two hashes do not match, the operation will fail.
            Returns: The updated options
          - public BlockBlobStageBlockOptions setLeaseId(String leaseId)
            Parameters:
              - leaseId - Lease ID for accessing source content.
            Returns: The updated options

name: 'Migrate S3 pom dependency to Azure Blob Storage pom dependency'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.xml'
  codePattern: >-
    spring-cloud-aws-starter-s3|<artifactId>s3</artifactId>|<artifactId>aws-java-sdk-s3</artifactId>

steps:
  - description: "Migrate S3 pom dependency to Azure Blob Storage pom dependency"
    type: "instruction"
    content: |
      Your task is to migrate a pom.xml from using the Amazon S3 API dependencies to the Azure Storage Blob API dependencies.
      Pay attention that, you should only update the specific one or two dependency blocks and keep the rest of the file, you cannot replace the whole file. What you returns must be a valid, whole, pom file.
      Below are some references for you, please replace the dependencies in pom.xml accordingly。
      Please be noted that the two blob related dependencies should both be provided, one for the credentials while initializing the client and the other for blob related APIs.
      S3 related dependencies:
      <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>s3</artifactId>
      </dependency>
      <dependency>
        <groupId>io.awspring.cloud</groupId>
        <artifactId>spring-cloud-aws-starter-s3</artifactId>
      </dependency>
      <dependency>
        <groupId>com.amazonaws</groupId>
        <artifactId>aws-java-sdk-s3</artifactId>
      </dependency>

      Blob related dependencies:
      1. Managed dependency:
        <dependencyManagement>
          <dependencies>
            <dependency>
              <groupId>com.azure</groupId>
              <artifactId>azure-sdk-bom</artifactId>
              <version>1.2.36</version> <!-- Use the latest version available -->
              <type>pom</type>
              <scope>import</scope>
            </dependency>
          </dependencies>
        </dependencyManagement>
      2. Dependencies:
        <dependency>
          <groupId>com.azure</groupId>
          <artifactId>azure-storage-blob</artifactId>
        </dependency>
        <dependency>
          <groupId>com.azure</groupId>
          <artifactId>azure-storage-blob-batch</artifactId>
        </dependency>
        <dependency>
          <groupId>com.azure</groupId>
          <artifactId>azure-identity</artifactId>
          <version>1.16.3</version>
        </dependency>

name: 'Migrate S3client presignedUrl to Azure Blob Storage sasToken'
description: "Migrate AWS S3 presigned URL generation to Azure Blob Storage SAS token generation"
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    GetObjectPresignRequest|PresignedGetObjectRequest|PutObjectPresignRequest|PresignedPutObjectRequest|generatePresignedUrl|presignGetObject|presignPutObject|GeneratePresignedUrlRequest
steps:
  - description: "Migrate AWS S3 presigned URL generation to Azure Blob Storage SAS token"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 presigned URL APIs to the Azure Storage Blob SAS token APIs while maintaining the same functionality. Below is a reference to the relevant AWS S3 and Azure Storage Blob APIs for your convenience.
      
      In AWS S3:
      - Presigned URLs provide temporary access to specific objects in S3 buckets.
      - They are created through S3Presigner (AWS SDK v2), AmazonS3 with GeneratePresignedUrlRequest (AWS SDK v1), or direct AmazonS3.generatePresignedUrl methods.
      - Presigned URLs have an expiration time and can restrict access to specific HTTP methods (GET, PUT).
      
      In Azure Storage Blob:
      - SAS tokens are generated to provide temporary access to blobs or containers.
      - These tokens can be generated via methods like BlobClient.generateSasUri() or by creating a SAS token manually and appending it to the blob URL.
      
      Some key differences to be aware of:
        1. In AWS S3, presigned URLs are generated directly. In Azure, you can either generate a full SAS URI or generate a SAS token and then append it to the blob URL.
        2. Azure Storage uses the BlobServiceSasSignatureValues class to specify SAS token parameters.
        3. When migrating code, make sure to handle expiry times correctly, as both APIs use different time unit approaches.
      
      Note:
        1. The package of `BlobClient` is com.azure.storage.blob and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here.
        2. The package of `BlobContainerClient` is com.azure.storage.blob.BlobContainerClient, don't make mistake here.
      
      Below are the APIs provided for your reference. Don't forget to import the package whenever you are adding a new class reference in code edit:

      # AWS S3 APIs

      Interface: S3Presigner
        Package: software.amazon.awssdk.services.s3.presigner
        Methods:
          - PresignedGetObjectRequest presignGetObject(GetObjectPresignRequest request)
            Description: Creates a presigned request for the getObject operation.
            Parameters:
              - request: GetObjectPresignRequest containing the details of the presign request
            Returns: A PresignedGetObjectRequest with a presigned URL and metadata about the presign process.
          - PresignedPutObjectRequest presignPutObject(PutObjectPresignRequest request)
            Description: Creates a presigned request for the putObject operation.
            Parameters:
              - request: PutObjectPresignRequest containing the details of the presign request
            Returns: A PresignedPutObjectRequest with a presigned URL and metadata about the presign process.

      Class: GetObjectPresignRequest
        Package: software.amazon.awssdk.services.s3.presigner.model
        Methods:
          - static GetObjectPresignRequest.Builder builder()
            Description: Returns a builder for creating a GetObjectPresignRequest.
            Returns: A new builder to build a GetObjectPresignRequest.

      Interface: GetObjectPresignRequest.Builder
        Methods:
          - GetObjectPresignRequest.Builder signatureDuration(Duration duration)
            Description: Sets how long the presigned URL should be valid for.
            Parameters:
              - duration: The duration of time that the presigned URL should be valid for.
            Returns: This builder for method chaining.
          - GetObjectPresignRequest.Builder getObjectRequest(GetObjectRequest getObjectRequest)
            Description: Sets the GetObjectRequest to use when presigning.
            Parameters:
              - getObjectRequest: The GetObjectRequest to use when presigning.
            Returns: This builder for method chaining.
          - GetObjectPresignRequest build()
            Description: Builds the GetObjectPresignRequest.
            Returns: A GetObjectPresignRequest based on the contents of this builder.

      Class: PutObjectPresignRequest
        Package: software.amazon.awssdk.services.s3.presigner.model
        Methods:
          - static PutObjectPresignRequest.Builder builder()
            Description: Returns a builder for creating a PutObjectPresignRequest.
            Returns: A new builder to build a PutObjectPresignRequest.

      Interface: PutObjectPresignRequest.Builder
        Methods:
          - PutObjectPresignRequest.Builder signatureDuration(Duration duration)
            Description: Sets how long the presigned URL should be valid for.
            Parameters:
              - duration: The duration of time that the presigned URL should be valid for.
            Returns: This builder for method chaining.
          - PutObjectPresignRequest.Builder putObjectRequest(PutObjectRequest putObjectRequest)
            Description: Sets the PutObjectRequest to use when presigning.
            Parameters:
              - putObjectRequest: The PutObjectRequest to use when presigning.
            Returns: This builder for method chaining.
          - PutObjectPresignRequest build()
            Description: Builds the PutObjectPresignRequest.
            Returns: A PutObjectPresignRequest based on the contents of this builder.

      Class: GeneratePresignedUrlRequest
        Package: com.amazonaws.services.s3.model
        Description: Provides options for generating a pre-signed URL for an Amazon S3 resource (bucket or object).
        Constructors:
          - GeneratePresignedUrlRequest(String bucketName, String key)
            Description: Creates a new GeneratePresignedUrlRequest for the specified bucket name and object key name.
            Parameters:
              - bucketName: The name of the bucket containing the desired object.
              - key: The key under which the desired object is stored.
          - GeneratePresignedUrlRequest(String bucketName, String key, HttpMethod method)
            Description: Creates a new GeneratePresignedUrlRequest for the specified bucket name, object key name, and HTTP method.
            Parameters:
              - bucketName: The name of the bucket containing the desired object.
              - key: The key under which the desired object is stored.
              - method: The HTTP method for which the URL will be valid.
        Methods:
          - void setExpiration(Date expiration)
            Description: Sets the expiration date for the pre-signed URL.
            Parameters:
              - expiration: The time after which the pre-signed URL will no longer be valid.
          - void setMethod(HttpMethod method)
            Description: Sets the HTTP method (GET, PUT) to be allowed by the pre-signed URL.
            Parameters:
              - method: The HTTP method to use.
          - void setBucketName(String bucketName)
            Description: Sets the name of the bucket containing the desired object.
            Parameters:
              - bucketName: The name of the bucket containing the desired object.
          - void setKey(String key)
            Description: Sets the key under which the desired object is stored.
            Parameters:
              - key: The key under which the desired object is stored.
          - void setContentType(String contentType)
            Description: Sets the content type for the request. This is especially useful for PUT requests.
            Parameters:
              - contentType: The content type to set.

      Class: AmazonS3
        Package: com.amazonaws.services.s3
        Methods:
          - URL generatePresignedUrl(String bucketName, String key, Date expiration)
            Description: Returns a pre-signed URL for accessing an Amazon S3 resource.
            Parameters:
              - bucketName: The name of the bucket containing the desired object.
              - key: The key in the specified bucket under which the desired object is stored.
              - expiration: The time at which the returned pre-signed URL will expire.
            Returns: A pre-signed URL which expires at the specified time, and can be used to allow anyone to download the specified object from S3, without exposing AWS security credentials.
          - URL generatePresignedUrl(String bucketName, String key, Date expiration, HttpMethod method)
            Description: Returns a pre-signed URL for accessing an Amazon S3 resource.
            Parameters:
              - bucketName: The name of the bucket containing the desired object.
              - key: The key in the specified bucket under which the desired object is stored.
              - expiration: The time at which the returned pre-signed URL will expire.
              - method: The HTTP method verb to use for this URL
            Returns: A pre-signed URL which expires at the specified time, and can be used to allow anyone to download the specified object from S3, without exposing AWS security credentials.
          - URL generatePresignedUrl(GeneratePresignedUrlRequest generatePresignedUrlRequest)
            Description: Returns a pre-signed URL for accessing an Amazon S3 resource, using the parameters and settings in the specified request object.
            Parameters:
              - generatePresignedUrlRequest: The request object containing all the options for generating a pre-signed URL.
            Returns: A pre-signed URL which expires at the specified time, and can be used to allow anyone to perform the operation specified in the request on the specified S3 resource, without exposing AWS security credentials.

      # Azure Blob Storage APIs

      Class: BlobClient
        Package: com.azure.storage.blob
        Methods:
          - public String getBlobUrl()
            Description: Gets the URL of the blob represented by this client.
            Returns: The URL of the blob.
          - public String generateSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues)
            Description: Generates a service SAS for the blob using the specified BlobServiceSasSignatureValues
            Parameters:
              - blobServiceSasSignatureValues - BlobServiceSasSignatureValues
            Returns: A String representing the SAS query parameters.
          - public String generateSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues, Context context)
            Description: Generates a service SAS for the blob using the specified BlobServiceSasSignatureValues
            Parameters:
              - blobServiceSasSignatureValues - BlobServiceSasSignatureValues
              - context - Additional context that is passed through the code when generating a SAS.
            Returns: A String representing the SAS query parameters.
          - public String generateUserDelegationSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues, UserDelegationKey userDelegationKey)
            Description: Generates a user delegation SAS for the blob using the specified BlobServiceSasSignatureValues.
            Parameters:
              - blobServiceSasSignatureValues - BlobServiceSasSignatureValues
              - userDelegationKey - A UserDelegationKey object used to sign the SAS values. See getUserDelegationKey(OffsetDateTime start, OffsetDateTime expiry) for more information on how to get a user delegation key.
            Returns: A String representing the SAS query parameters.
          - public String generateUserDelegationSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues, UserDelegationKey userDelegationKey, String accountName, Context context)
            Description: Generates a user delegation SAS for the blob using the specified BlobServiceSasSignatureValues.
            Parameters:
              - blobServiceSasSignatureValues - BlobServiceSasSignatureValues
              - userDelegationKey - A UserDelegationKey object used to sign the SAS values. See getUserDelegationKey(OffsetDateTime start, OffsetDateTime expiry) for more information on how to get a user delegation key.
              - accountName - The account name.
              - context - Additional context that is passed through the code when generating a SAS.
            Returns: A String representing the SAS query parameters.

      Class: BlobServiceClient
        Package: com.azure.storage.blob
        Methods:
          - BlobContainerClient getBlobContainerClient(String containerName)
            Description: Gets a client pointing to the container.
            Parameters:
              - containerName: The name of the container to point to.
            Returns: A BlobContainerClient object pointing to the specified container.

      Class: BlobContainerClient
        Package: com.azure.storage.blob
        Methods:
          - BlobClient getBlobClient(String blobName)
            Description: Gets a client pointing to the blob.
            Parameters:
              - blobName: The name of the blob to point to.
            Returns: A BlobClient object pointing to the specified blob.
          - public String generateSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues, Context context)
            Description: Generates a service SAS for the container using the specified BlobServiceSasSignatureValues
            Parameters: 
              - blobServiceSasSignatureValues: Configurations for the service SAS.
              - userDelegationKey : Additional context that is passed through the code when generating a SAS.
            Returns: A String representing the SAS query parameters.
          - public String generateUserDelegationSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues, UserDelegationKey userDelegationKey)
            Description: Generates a user delegation SAS for the container using the specified BlobServiceSasSignatureValues.
            Parameters: 
              - blobServiceSasSignatureValues: Configurations for the service SAS.
              - context: A UserDelegationKey object used to sign the SAS values. 
            Returns: A String representing the SAS query parameters.
          - public String generateSas(BlobServiceSasSignatureValues blobServiceSasSignatureValues)
            Description: Generates a service SAS for the container using the specified BlobServiceSasSignatureValues
            Parameters:
              - blobServiceSasSignatureValues: Configurations for the service SAS.
            Returns: A String representing the SAS query parameters.

      Class: BlobSasPermission
        Package: com.azure.storage.blob.sas
        Methods:
          - public BlobSasPermission setReadPermission(boolean hasAddPermission)
            Description: Sets if the permission allows for read operations.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setWritePermission(boolean hasAddPermission)
            Description: Sets if the permission allows for write operations.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setCreatePermission(boolean hasAddPermission)
            Description: Sets if the permission allows for create operations.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setDeletePermission(boolean hasAddPermission)
            Description: Sets if the permission allows for delete operations.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setAddPermission(boolean hasAddPermission)
            Description: Sets the add permission status.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setExecutePermission(boolean hasExecutePermission)
            Description: Sets the add permission status.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setListPermission(boolean hasExecutePermission)
            Description: Sets the add permission status.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setReadPermission(boolean hasExecutePermission)
            Description: Sets the add permission status.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.
          - public BlobSasPermission setWritePermission(boolean hasExecutePermission)
            Description: Sets the add permission status.
            Parameters:
              - hasAddPermission - Permission status to set
            Returns: The updated BlobSasPermission object.

      Class: BlobServiceSasSignatureValues
        Package: com.azure.storage.blob.sas
        Description: Used to initialize parameters for a Shared Access Signature (SAS) for an Azure Blob Storage service.
        Constructors:
          - BlobServiceSasSignatureValues(OffsetDateTime expiryTime, BlobSasPermission permissions)
            Description: Creates a BlobServiceSasSignatureValues object with the specified expiry time and permissions.
            Parameters:
              - expiryTime: The time after which the SAS will expire.
              - permissions: The permissions to set for the SAS.
          - BlobServiceSasSignatureValues(OffsetDateTime expiryTime, BlobContainerSasPermission  permissions)
            Description: Creates a BlobServiceSasSignatureValues object with the specified expiry time and permissions.
            Parameters:
              - expiryTime: The time after which the SAS will expire.
              - permissions - BlobContainerSasPermission allowed by the SAS.
        Methods:
          - BlobServiceSasSignatureValues setExpiryTime(OffsetDateTime expiryTime)
            Description: Sets when the SAS will expire.
            Parameters:
              - expiryTime: The time after which the SAS will expire.
            Returns: The updated BlobServiceSasSignatureValues object.
          - BlobServiceSasSignatureValues setPermissions(BlobSasPermission permissions)
            Description: Sets the permissions for the SAS.
            Parameters:
              - permissions: The permissions to set for the SAS.
            Returns: The updated BlobServiceSasSignatureValues object.

name: 'Migrate S3client putObject to Azure Blob Storage upload'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    PutObjectRequest|PutObject​
steps:
  - description: "Migrate s3client with putObject API to Azure Blob Storage download"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      Pay attention to the contentType contentLength related parameters, only if they exist, you can use BlobHttpHeaders and BlobParallelUploadOptions to achieve similar functionality.
      Mind that
      1. the package of BlobParallelUploadOptions is listed below: com.azure.storage.blob.options.
      2. When instantiating `BlobParallelUploadOptions`, you must use ONLY one of these two constructor forms, either one BinaryData or One InputStream. Also you should import BinaryData or InputStream base on your choice:
         - `new BlobParallelUploadOptions(binaryDataVariable)` OR
         - `new BlobParallelUploadOptions(inputStreamVariable)`
         Any additional parameters must be set using setter methods after the object is created (such as `setHeaders()`).
         It doesn't take a `File` type as input!
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Class: PutObjectRequest
        Package:software.amazon.awssdk.services.s3.model
        Methods:
          - public static PutObjectRequest.Builder builder()

      Interface: PutObjectRequest.Builder
        Methods:
          - PutObjectRequest.Builder bucket(String bucket)
            Description: The bucket name to which the PUT action was initiated.
            Parameters:
            - bucket: The bucket name to which the PUT action was initiated.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - PutObjectRequest.Builder key(String key)
            Description: Object key for which the PUT action was initiated.
            Parameters:
            - key: Object key for which the PUT action was initiated.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - PutObjectRequest.Builder contentType​(String contentType)
            Description: A standard MIME type describing the format of the contents.
            Parameters:
              - contentType - A standard MIME type describing the format of the contents.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - PutObjectRequest.Builder contentLength​(Long contentLength)
            Description: Size of the body in bytes. This parameter is useful when the size of the body cannot be determined automatically.
            Parameters:
              - contentLength - Size of the body in bytes.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - PutObjectRequest.Builder metadata​(Map<String,​String> metadata)
            Description: A map of metadata to store with the object in S3.
            Parameters:
              - metadata - A map of metadata to store with the object in S3.
            Returns: Returns a reference to this object so that method calls can be chained together.

      Class BlobServiceClient
        Package: com.azure.storage.blob
        Methods:
          - public BlobContainerClient getBlobContainerClient(String containerName)
            Description: Initializes a BlobContainerClient object pointing to the specified container. This method does not create a container. It simply constructs the URL to the container and offers access to methods relevant to containers.
            Parameters:
            - containerName: The name of the container to point to.
            Returns: A BlobContainerClient object pointing to the specified container.

      Class BlobContainerClient
        Package: com.azure.storage.blob
        Methods:
        - public BlobClient getBlobClient(String blobName)
          Description: Initializes a new BlobClient object by concatenating blobName to the end of ContainerAsyncClient's URL. The new BlobClient uses the same request policy pipeline as the ContainerAsyncClient.
        Parameters:
        - blobName: A String representing the name of the blob. If the blob name contains special characters, pass in the url encoded version of the blob name.
        Returns: A new BlobClient object which references the blob with the specified name in this container.

      Class: BlobClient
        Package: com.azure.storage.blob
        Note: `The package of `BlobClient` is com.azure.storage.blob and the package of `BlobClientBase` is com.azure.storage.blob.specialized, don't make mistake here.
        Methods:
          - public void upload(BinaryData data)
            Description: Creates a new blob. By default this method will not overwrite an existing blob.
            Parameters:
              - data: The data to write to the blob.
          - public void upload(BinaryData data, boolean overwrite)
            Description: Creates a new blob, or updates the content of an existing blob.
            Parameters:
              - data: The data to write to the blob.
              - overwrite: Whether or not to overwrite, should data exist on the blob.
          - public void upload(InputStream data)
            Description: Creates a new blob. By default this method will not overwrite an existing blob.
            Parameters:
              - data: The data to write to the blob. The data must be markable. This is in order to support retries. If the data is not markable, consider opening a BlobOutputStream and writing to the returned stream. Alternatively, consider wrapping your data source in a BufferedInputStream to add mark support.
          - public void upload(InputStream data, boolean overwrite)
            Description: Creates a new blob, or updates the content of an existing blob.
            Parameters:
              - data: The data to write to the blob. The data must be markable. This is in order to support retries. If the data is not markable, consider opening a BlobOutputStream and writing to the returned stream. Alternatively, consider wrapping your data source in a BufferedInputStream to add mark support.
              - overwrite: Whether or not to overwrite, should data exist on the blob.
          - public void upload(InputStream data, long length)
            Description: Creates a new blob. By default this method will not overwrite an existing blob.
            Parameters:
              - data: The data to write to the blob. The data must be markable. This is in order to support retries. If the data is not markable, consider opening a BlobOutputStream and writing to the returned stream. Alternatively, consider wrapping your data source in a BufferedInputStream to add mark support.
              - length: The exact length of the data. It is important that this value match precisely the length of the data provided in the InputStream.
          - public void upload(InputStream data, long length, boolean overwrite)
            Description: Creates a new blob, or updates the content of an existing blob.
            Parameters:
              - data: The data to write to the blob. The data must be markable. This is in order to support retries. If the data is not markable, consider opening a BlobOutputStream and writing to the returned stream. Alternatively, consider wrapping your data source in a BufferedInputStream to add mark support.
              - length: The exact length of the data. It is important that this value match precisely the length of the data provided in the InputStream.
              - overwrite: Whether or not to overwrite, should data exist on the blob.
          - public void uploadFromFile(String filePath)
            Description: Creates a new block blob. By default this method will not overwrite an existing blob.
            Parameters:
              - filePath - Path of the file to upload
          - public void uploadFromFile(String filePath, boolean overwrite)
            Description: Creates a new block blob, or updates the content of an existing block blob.
            Parameters:
              - filePath - Path of the file to upload
              - overwrite - Whether or not to overwrite, should the blob already exist
          - public Response uploadWithResponse(BlobParallelUploadOptions options, Duration timeout, Context context)
            Description: Creates a new blob, or updates the content of an existing blob.
            Parameters:
              - options - BlobParallelUploadOptions
              - timeout - An optional timeout value beyond which a RuntimeException will be raised.
              - context - Additional context that is passed through the Http pipeline during the service call.
            Returns: Information about the uploaded block blob.
          - public Response uploadFromFileWithResponse(BlobUploadFromFileOptions options, Duration timeout, Context context)
            Description: Creates a new block blob, or updates the content of an existing block blob.
            Parameters:
              - options - BlobUploadFromFileOptions
              - timeout - An optional timeout value beyond which a RuntimeException will be raised.
              - context - Additional context that is passed through the Http pipeline during the service call.
            Returns: Information about the uploaded block blob.

      Class: BlobParallelUploadOptions
        Description: Extended options that may be passed when uploading a Block Blob in parallel.
        Note: Please only use BinaryData or InputStream in the constructor, it doesn't take other types like `File`
        Package: com.azure.storage.blob.options
        Constructors:
        - public BlobParallelUploadOptions(BinaryData data)
          Description: Constructs a new BlobParallelUploadOptions.
          Parameter:
            - data - The data to write to the blob.
        - public BlobParallelUploadOptions(InputStream dataStream)
          Description: Constructs a new BlobParallelUploadOptions. Note: the InputStream must be closed by the caller.
          Parameter:
            - dataStream - The data to write to the blob.
        Methods:
        - public BlobParallelUploadOptions setHeaders(BlobHttpHeaders headers)
          Description: Sets the BlobHttpHeaders.
          Parameters:
            - headers - BlobHttpHeaders
          Returns: The updated options
        - public BlobParallelUploadOptions setMetadata(Map metadata)
          Description: Sets the metadata
          Parameters:
            - metadata - The metadata to associate with the blob.
          Returns: The updated options.

      Class: BlobUploadFromFileOptions
        Description: Extended options that may be passed when uploading a blob from a file.
        Package: com.azure.storage.blob.options
        Constructors:
        - public BlobUploadFromFileOptions(String filePath)
          Description: Constructs a BlobUploadFromFileOptions.
          Parameter:
            filePath - Path of the file to upload.
        Methods:
        - public BlobUploadFromFileOptions setHeaders(BlobHttpHeaders headers)
          Description: Sets the BlobHttpHeaders.
          Parameters:
            - headers - BlobHttpHeaders
          Returns: The updated options
        - public BlobUploadFromFileOptions setMetadata(Map metadata)
          Description: Sets the metadata
          Parameters:
            - metadata - The metadata to associate with the blob.
          Returns: The updated options.

      Class: BlobHttpHeaders
        Description: Parameter group
        Package: com.azure.storage.blob.models
        Methods:
        - public BlobHttpHeaders setContentType(String contentType)
          Description: Set the contentType property: Optional. Sets the blob's content type. If specified, this property is stored with the blob and returned with a read request.
          Parameter:
            - contentType - the contentType value to set.
          Returns: the BlobHttpHeaders object itself.

name: 'Migrate S3client restoreObject to Azure Blob Storage blob copy'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    RestoreObjectRequest|RestoreObjectResponse
steps:
  - description: "Migrate s3client with restoreObject API to Azure Blob Storage blob copy"
    type: "instruction"
    content: |
      Your task to to migrate a java file from using amazon s3 API to Azure Storage Blob API while achieving the same functionality. The related API is listed below for your reference. You can tell whether it's an aws or Azure API from the package name.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: RestoreObjectRequest.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
        - RestoreObjectRequest.Builder bucket​(String bucket)
            Description: The bucket name containing the object to restore.
            Parameters:
                - bucket - The bucket name containing the object to restore.
            Retures: Returns a reference to this object so that method calls can be chained together.
        - RestoreObjectRequest.Builder key​(String key)
            Description: Object key for which the action was initiated.
            Parameters:
                - key - Object key for which the action was initiated.
            Retures: Returns a reference to this object so that method calls can be chained together.
        - RestoreObjectRequest.Builder versionId​(String versionId)
            Description: VersionId used to reference a specific version of the object.
            Parameters:
                - versionId  - VersionId used to reference a specific version of the object.
            Retures: Returns a reference to this object so that method calls can be chained together.

      Interface: RestoreObjectResponse.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
        - RestoreObjectResponse.Builder requestCharged​(String requestCharged)
            Description: Sets the value of the RequestCharged property for this object.
            Parameters:
                - requestCharged - The new value for the RequestCharged property for this object.
            Retures: Returns a reference to this object so that method calls can be chained together.
        - RestoreObjectResponse.Builder restoreOutputPath​(String restoreOutputPath)
            Description: Indicates the path in the provided S3 output location where Select results will be restored to.
            Parameters:
                - restoreOutputPath - Indicates the path in the provided S3 output location where Select results will be restored to.
            Retures: Returns a reference to this object so that method calls can be chained together.
        - RestoreObjectResponse.Builder requestCharged​(RequestCharged requestCharged)
            Description: Sets the value of the RequestCharged property for this object.
            Parameters:
                - requestCharged - The new value for the RequestCharged property for this object.
            Retures: Returns a reference to this object so that method calls can be chained together.

      Enum: RequestCharged
          Package: software.amazon.awssdk.services.s3.model
          Description: If present, indicates that the requester was successfully charged for the request.
          Fields:
          - REQUESTER
          - UNKNOWN_TO_SDK_VERSION

      Class: BlobClient
        Description: This class provides a client that contains generic blob operations for Azure Storage Blobs. Operations allowed by the client are uploading and downloading, copying a blob, retrieving and setting metadata, retrieving and setting HTTP headers, and deleting and un-deleting a blob.
        Package: com.azure.storage.blob
        Methods:
        - SyncPoller beginCopy(BlobBeginCopyOptions options)
          Description: Copies the data at the source URL to a blob.
          Parameters:
            options - BlobBeginCopyOptions
          Returns: A SyncPoller<T,U> to poll the progress of blob copy operation.

      Class: BlobBeginCopyOptions
          Description: Extended options that may be passed when beginning a copy operation.
          Package: com.azure.storage.blob.options
          Constructors:
          - public BlobBeginCopyOptions(String sourceUrl)
            Parameter:
              - sourceUrl - The source URL to copy from. URLs outside of Azure may only be copied to block blobs.
          Methods:
          - BlobBeginCopyOptions setTier(AccessTier tier)
              Parameters:
                  - tier - AccessTier for the destination blob.
              Returns: The updated options.
          - BlobBeginCopyOptions setRehydratePriority(RehydratePriority rehydratePriority)
              Parameters:
                  - rehydratePriority - RehydratePriority for rehydrating the blob.
              Returns: The updated options.

      Class: RehydratePriority
          Description: If an object is in rehydrate pending state then this header is returned with priority of rehydrate. Valid values are High and Standard.
          Package: com.azure.storage.blob.models
          Fields:
              - static final RehydratePriority HIGH
                  Description: Static value High for RehydratePriority.
              - static final RehydratePriority STANDARD
                  Description: Static value Standard for RehydratePriority.

      Class: AccessTier
          Description: Defines values for AccessTier.
          Package: com.azure.storage.blob.models
          Fields:
              - static final AccessTier ARCHIVE
              - static final AccessTier COLD
              - static final AccessTier HOT
              - static final AccessTier PREMIUM

name: 'Migrate S3Object to Azure Blob Storage BlobItem'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    S3Object|s3Object
steps:
  - description: "Migrate s3client with restoreObject API to Azure Blob Storage blob copy"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Amazon S3 API to the Azure Storage Blob API while maintaining the same functionality. Below is a reference to the relevant Azure Storage Blob APIs for your convenience. You can tell whether it's an aws or Azure API from the package name.
      Try replace all references to S3 APIs with equivalent Azure Storage Blob APIs, using the provided API descriptions as guidance.
      Ensure the resulting code is clean, efficient, and preserves the original functionality.
      Some of the methods are of the same name under different class, please pay attention to the type before using.
      Be super careful with the BlobItem.getProperties().getContentLength() vs blobClient.getProperties().getBlobSize() .
      Below are the APIs provided for your reference, don't forget to import the package whenever you are adding a new class reference in code edit:

      Interface: S3Object.Builder
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - S3Object.Builder eTag​(String eTag)
            Description: The entity tag is a hash of the object. The ETag reflects changes only to the contents of an object, not its metadata.
            Parameters:
              - eTag - The entity tag is a hash of the object. The ETag reflects changes only to the contents of an object, not its metadata.
            Returns: Returns a reference to this object so that method calls can be chained together.
          - S3Object.Builder size​(Long size)
            Description: Size in bytes of the object
            Parameters:
              - size - Size in bytes of the object
            Returns: Returns a reference to this object so that method calls can be chained together.

      Class: S3Object
        Description: An object consists of data and its descriptive metadata.
        Package: software.amazon.awssdk.services.s3.model
        Methods:
          - public final String eTag()
            Description: The entity tag is a hash of the object. The ETag reflects changes only to the contents of an object, not its metadata.
            Returns: The entity tag is a hash of the object.
          - public final Long size()
            Description: Size in bytes of the object
            Returns: Size in bytes of the object

      Class: BlobItem
        Description: An Azure Storage Blob.
        Package: com.azure.storage.blob.models
        Methods:
          - public Map getMetadata()
            Description: Get the metadata property: The metadata property.
            Returns: the metadata value.
          - public String getName()
            Description: Get the name property: The name property.
            Returns: the name value.
          - public BlobItemProperties getProperties()
            Description: Get the properties property: The properties property.
            Returns: the properties value.

      Class: BlobItemProperties
        Description: Properties of a blob.
        Package: com.azure.storage.blob.models
        Methods:
          - public AccessTier getAccessTier()
            Description: Get the accessTier property: Possible values include: 'P4', 'P6', 'P10', 'P15', 'P20', 'P30', 'P40', 'P50', 'P60', 'P70', 'P80', 'Hot', 'Cool', 'Archive'.
            Returns: the accessTier value.
          - public String getContentEncoding()
            Description: Get the contentEncoding property: The contentEncoding property.
            Returns: the contentEncoding value.
          - public Long getContentLength()
            Description: Get the contentLength property: Size in bytes.
            Returns: the contentLength value.

name: 'Migrate from AWS S3 to Azure Blob Storage Supported Packages'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/*.java'
  codePattern: >-
    com.amazonaws.services.s3|software.amazon.awssdk.services.s3

steps:
  - description: "Migrate from AWS S3 to Azure Blob Storage"
    type: "instruction"
    content: |
      Your task is to migrate a Java application from AWS S3 storage to Azure Blob Storage.
      
      Here are the correct import statements for Azure Blob Storage classes:
      ```java
      // Core Azure Blob Storage classes - CORRECT IMPORTS
      import com.azure.storage.blob.BlobClient;               // NOT in the models package
      import com.azure.storage.blob.BlobContainerClient;      // NOT in the models package
      import com.azure.storage.blob.BlobServiceClient;        // NOT in the models package
      import com.azure.storage.blob.BlobServiceClientBuilder; // NOT in the models package
      
      // Models and other supporting classes
      import com.azure.storage.blob.models.BlobItem;
      import com.azure.storage.blob.models.BlobProperties;
      import com.azure.storage.blob.options.BlobParallelUploadOptions;
      ```
      
      # IMPORTANT: BlobClient is NOT in the models package!
      # The import com.azure.storage.blob.models.BlobClient is INCORRECT
      # Always use import com.azure.storage.blob.BlobClient instead

