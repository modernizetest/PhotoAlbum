---
name: migration-cryptography-operations-to-azure-key-vault
description: Migrates Java cryptographic operations (Cipher, Signature) from local key management to Azure Key Vault for centralized key management and cryptographic operations. Use when migrating Java applications that use javax.crypto.Cipher or java.security.Signature to Azure Key Vault, or centralizing cryptographic key management in Azure.
---

name: 'Migrate local crypto and signature to use Azure Key Vault Key'
description: ""
codeLocation:
  type: textsearch
  filePattern: "**/*.java"
  codePattern: >-
    Cipher|Signature

steps:
  - description: "Migrate local crypto and signature to use Azure Key Vault"
    type: "instruction"
    content: |
      Your task is to migrate a Java file from using the Cipher and Signature APIs to the Azure Key Vault API while maintaining the same functionality. Below is a reference to the relevant Azure Key Vault APIs for your convenience. You can tell whether it's a Cipher/Signature or Azure API from the package name.
      Try replacing all references to Cipher and Signature APIs with equivalent Azure Key Vault APIs, using the provided API descriptions as guidance.
      Please note:
        - Avoid using connectionString of the Azure Key Vault to initialize the CryptographyClient. Use AzureDefaultCredential instead.
        - Pay attention to the package name you import when initializing the clients. Packages are listed below along with the APIs.

      Below are the APIs provided for your reference. Don't forget to import the package whenever you are adding a new class reference in code edits:

      class: CryptographyClient
        Package: com.azure.security.keyvault.keys.cryptography
        Methods:
          - public SignResult sign(SignatureAlgorithm algorithm, byte[] digest)
            Description: Creates a signature from a digest using the configured key. The sign operation supports both asymmetric and symmetric keys. This operation requires the keys/sign permission for non-local operations. The SignatureAlgorithm indicates the type of algorithm to use to create the signature from the digest. Possible values include: ES256, ES384, ES512, ES256K, PS256, RS384, RS512, RS256, RS384, and RS512.
            Parameters:
            - algorithm - The algorithm to use for signing.
            - digest - The content from which signature is to be created.
            Returns: A SignResult whose getSignature() contains the created signature.
          - public SignResult sign(SignatureAlgorithm algorithm, byte[] digest, Context context)
            Description: Creates a signature from a digest using the configured key. The sign operation supports both asymmetric and symmetric keys. This operation requires the keys/sign permission for non-local operations. The SignatureAlgorithm indicates the type of algorithm to use to create the signature from the digest. Possible values include: ES256, ES384, ES512, ES256K, PS256, RS384, RS512, RS256, RS384, and RS512.
            Parameters:
            - algorithm - The algorithm to use for signing.
            - digest - The content from which signature is to be created.
            - context - Additional context that is passed through the HttpPipeline during the service call.
            Returns: A SignResult whose getSignature() contains the created signature.
          - public SignResult signData(SignatureAlgorithm algorithm, byte[] data)
            Description: Creates a signature from the raw data using the configured key. The sign data operation supports both asymmetric and symmetric keys. This operation requires the keys/sign permission for non-local operations. The SignatureAlgorithm indicates the type of algorithm to use to sign the digest. Possible values include: ES256, ES384, ES512, ES256K, PS256, RS384, RS512, RS256, RS384, and RS512.
            Parameters:
            - algorithm - The algorithm to use for signing.
            - data - The content from which signature is to be created.
            Returns: A SignResult whose getSignature() contains the created signature.
          - public SignResult signData(SignatureAlgorithm algorithm, byte[] data, Context context)
            Description: Creates a signature from the raw data using the configured key. The sign data operation supports both asymmetric and symmetric keys. This operation requires the keys/sign permission for non-local operations. The SignatureAlgorithm indicates the type of algorithm to use to sign the digest. Possible values include: ES256, ES384, ES512, ES256K, PS256, RS384, RS512, RS256, RS384, and RS512.
            Parameters:
            - algorithm - The algorithm to use for signing.
            - data - The content from which signature is to be created.
            - context - Additional context that is passed through the HttpPipeline during the service call.
            Returns: A SignResult whose getSignature() contains the created signature.
          - public VerifyResult verify(SignatureAlgorithm algorithm, byte[] digest, byte[] signature)
            Description: Verifies a signature using the configured key. The verify operation supports both symmetric keys and asymmetric keys. In case of asymmetric keys public portion of the key is used to verify the signature. This operation requires the keys/verify permission for non-local operations. The SignatureAlgorithm indicates the type of algorithm to use to verify the signature. Possible values include: ES256, ES384, ES512, ES256K, PS256, RS384, RS512, RS256, RS384, and RS512.
            Parameters:
            - algorithm - The algorithm to use for signing.
            - digest - The content from which signature was created.
            - signature - The signature to be verified.
            Returns: A VerifyResult isValid().
          - public VerifyResult verify(SignatureAlgorithm algorithm, byte[] digest, byte[] signature, Context context)
            Description: Verifies a signature using the configured key. The verify operation supports both symmetric keys and asymmetric keys. In case of asymmetric keys public portion of the key is used to verify the signature. This operation requires the keys/verify permission for non-local operations. The SignatureAlgorithm indicates the type of algorithm to use to verify the signature. Possible values include: ES256, ES384, ES512, ES256K, PS256, RS384, RS512, RS256, RS384, and RS512.
            Parameters:
            - algorithm - The algorithm to use for signing.
            - digest - The content from which signature was created.
            - signature - The signature to be verified.
            - context - Additional context that is passed through the HttpPipeline during the service call.
            Returns: A VerifyResult isValid().
          - public VerifyResult verifyData(SignatureAlgorithm algorithm, byte[] data, byte[] signature)
            Description: Verifies a signature against the raw data using the configured key. The verify operation supports both symmetric keys and asymmetric keys. In case of asymmetric keys public portion of the key is used to verify the signature. This operation requires the keys/verify permission for non-local operations. The SignatureAlgorithm indicates the type of algorithm to use to verify the signature. Possible values include: ES256, ES384, ES512, ES256K, PS256, RS384, RS512, RS256, RS384, and RS512.
            Parameters:
            - algorithm - The algorithm to use for signing.
            - data - The raw content against which signature is to be verified.
            - signature - The signature to be verified.
            Returns: A VerifyResult isValid().
          - public VerifyResult verifyData(SignatureAlgorithm algorithm, byte[] data, byte[] signature, Context context)
            Description: Verifies a signature against the raw data using the configured key. The verify operation supports both symmetric keys and asymmetric keys. In case of asymmetric keys public portion of the key is used to verify the signature. This operation requires the keys/verify permission for non-local operations. The SignatureAlgorithm indicates the type of algorithm to use to verify the signature. Possible values include: ES256, ES384, ES512, ES256K, PS256, RS384, RS512, RS256, RS384, and RS512.
            Parameters:
            - algorithm - The algorithm to use for signing.
            - data - The raw content against which signature is to be verified.
            - signature - The signature to be verified.
            - context - Additional context that is passed through the HttpPipeline during the service call.
            Returns: A VerifyResult isValid().
          - public EncryptResult encrypt(EncryptionAlgorithm algorithm, byte[] plaintext)
            Description: Encrypts an arbitrary sequence of bytes using the configured key. Note that the encrypt operation only supports a single block of data, the size of which is dependent on the target key and the encryption algorithm to be used. The encrypt operation is supported for both symmetric keys and asymmetric keys. In case of asymmetric keys, the public portion of the key is used for encryption. This operation requires the keys/encrypt permission for non-local operations. The EncryptionAlgorithm indicates the type of algorithm to use for encrypting the specified plaintext. Possible values for asymmetric keys include: RSA1_5, RSA_OAEP and RSA_OAEP_256. Possible values for symmetric keys include: A128CBC, A128CBCPAD, A128CBC_HS256, A128GCM, A192CBC, A192CBCPAD, A192CBC_HS384, A192GCM, A256CBC, A256CBCPAD, A256CBC_HS512 and A256GCM.
            Parameters:
            - algorithm - The algorithm to be used for encryption.
            - plaintext - The content to be encrypted.
            Returns: The EncryptResult whose getCipherText() contains the encrypted content.
          - public EncryptResult encrypt(EncryptionAlgorithm algorithm, byte[] plaintext, Context context)
            Description: Encrypts an arbitrary sequence of bytes using the configured key. Note that the encrypt operation only supports a single block of data, the size of which is dependent on the target key and the encryption algorithm to be used. The encrypt operation is supported for both symmetric keys and asymmetric keys. In case of asymmetric keys, the public portion of the key is used for encryption. This operation requires the keys/encrypt permission for non-local operations. The EncryptionAlgorithm indicates the type of algorithm to use for encrypting the specified plaintext. Possible values for asymmetric keys include: RSA1_5, RSA_OAEP and RSA_OAEP_256. Possible values for symmetric keys include: A128CBC, A128CBCPAD, A128CBC_HS256, A128GCM, A192CBC, A192CBCPAD, A192CBC_HS384, A192GCM, A256CBC, A256CBCPAD, A256CBC_HS512 and A256GCM.
            Parameters:
            - algorithm - The algorithm to be used for encryption.
            - plaintext - The content to be encrypted.
            - context - Additional context that is passed through the HttpPipeline during the service call.
            Returns: The EncryptResult whose getCipherText() contains the encrypted content.
          - public EncryptResult encrypt(EncryptParameters encryptParameters, Context context)
            Description: Encrypts an arbitrary sequence of bytes using the configured key. Note that the encrypt operation only supports a single block of data, the size of which is dependent on the target key and the encryption algorithm to be used. The encrypt operation is supported for both symmetric keys and asymmetric keys. In case of asymmetric keys, the public portion of the key is used for encryption. This operation requires the keys/encrypt permission for non-local operations. The EncryptionAlgorithm indicates the type of algorithm to use for encrypting the specified plaintext. Possible values for asymmetric keys include: RSA1_5, RSA_OAEP and RSA_OAEP_256. Possible values for symmetric keys include: A128CBC, A128CBCPAD, A128CBC_HS256, A128GCM, A192CBC, A192CBCPAD, A192CBC_HS384, A192GCM, A256CBC, A256CBCPAD, A256CBC_HS512 and A256GCM.
            Parameters:
            - encryptParameters - The parameters to use in the encryption operation.
            - context - Additional context that is passed through the HttpPipeline during the service call.
            Returns: The EncryptResult whose getCipherText() contains the encrypted content.
          - public DecryptResult decrypt(DecryptParameters decryptParameters, Context context)
            Description: Decrypts a single block of encrypted data using the configured key and specified algorithm. Note that only a single block of data may be decrypted, the size of this block is dependent on the target key and the algorithm to be used. The decrypt operation is supported for both asymmetric and symmetric keys. This operation requires the keys/decrypt permission for non-local operations. The EncryptionAlgorithm indicates the type of algorithm to use for decrypting the specified encrypted content. Possible values for asymmetric keys include: RSA1_5, RSA_OAEP and RSA_OAEP_256. Possible values for symmetric keys include: A128CBC, A128CBCPAD, A128CBC_HS256, A128GCM, A192CBC, A192CBCPAD, A192CBC_HS384, A192GCM, A256CBC, A256CBCPAD, A256CBC_HS512 and A256GCM.
            Parameters:
            - decryptParameters - The parameters to use in the decryption operation. Microsoft recommends you not use CBC without first ensuring the integrity of the ciphertext using an HMAC, for example. See Timing vulnerabilities with CBC-mode symmetric decryption using padding for more information.
            - context - Additional context that is passed through the HttpPipeline during the service call.
            Returns: The DecryptResult whose getPlainText() contains the decrypted content.
          - public DecryptResult decrypt(EncryptionAlgorithm algorithm, byte[] ciphertext)
            Description: Decrypts a single block of encrypted data using the configured key and specified algorithm. Note that only a single block of data may be decrypted, the size of this block is dependent on the target key and the algorithm to be used. The decrypt operation is supported for both asymmetric and symmetric keys. This operation requires the keys/decrypt permission for non-local operations. The EncryptionAlgorithm indicates the type of algorithm to use for decrypting the specified encrypted content. Possible values for asymmetric keys include: RSA1_5, RSA_OAEP and RSA_OAEP_256. Possible values for symmetric keys include: A128CBC, A128CBCPAD, A128CBC_HS256, A128GCM, A192CBC, A192CBCPAD, A192CBC_HS384, A192GCM, A256CBC, A256CBCPAD, A256CBC_HS512 and A256GCM.
            Parameters:
            - algorithm - The algorithm to be used for decryption.
            - ciphertext - The content to be decrypted. Microsoft recommends you not use CBC without first ensuring the integrity of the ciphertext using an HMAC, for example. See Timing vulnerabilities with CBC-mode symmetric decryption using padding for more information.
            Returns: The DecryptResult whose getPlainText() contains the decrypted content.
          - public DecryptResult decrypt(EncryptionAlgorithm algorithm, byte[] ciphertext, Context context)
            Description: Decrypts a single block of encrypted data using the configured key and specified algorithm. Note that only a single block of data may be decrypted, the size of this block is dependent on the target key and the algorithm to be used. The decrypt operation is supported for both asymmetric and symmetric keys. This operation requires the keys/decrypt permission for non-local operations. The EncryptionAlgorithm indicates the type of algorithm to use for decrypting the specified encrypted content. Possible values for asymmetric keys include: RSA1_5, RSA_OAEP and RSA_OAEP_256. Possible values for symmetric keys include: A128CBC, A128CBCPAD, A128CBC_HS256, A128GCM, A192CBC, A192CBCPAD, A192CBC_HS384, A192GCM, A256CBC, A256CBCPAD, A256CBC_HS512 and A256GCM.
            Parameters:
            - algorithm - The algorithm to be used for decryption.
            - ciphertext - The content to be decrypted. Microsoft recommends you not use CBC without first ensuring the integrity of the ciphertext using an HMAC, for example. See Timing vulnerabilities with CBC-mode symmetric decryption using padding for more information.
            - context - Additional context that is passed through the HttpPipeline during the service call.
            Returns: The DecryptResult whose getPlainText() contains the decrypted content.

      class: DecryptParameters
        Package: com.azure.security.keyvault.keys.cryptography.models

      class: DecryptResult
        Package: com.azure.security.keyvault.keys.cryptography.models

      class: EncryptParameters
        Package: com.azure.security.keyvault.keys.cryptography.models

      class: EncryptResult
        Package: com.azure.security.keyvault.keys.cryptography.models

      class: EncryptionAlgorithm
        Package: com.azure.security.keyvault.keys.cryptography.models

      class: KeyWrapAlgorithm
        Package: com.azure.security.keyvault.keys.cryptography.models

      class: SignResult
        Package: com.azure.security.keyvault.keys.cryptography.models

      class: SignatureAlgorithm
        Package: com.azure.security.keyvault.keys.cryptography.models

      class: UnwrapResult
        Package: com.azure.security.keyvault.keys.cryptography.models

      class: VerifyResult
        Package: com.azure.security.keyvault.keys.cryptography.models

      class: WrapResult
        Package: com.azure.security.keyvault.keys.cryptography.models

name: 'Add Azure Key Vault key dependency'
description: ""
codeLocation:
  type: textsearch
  filePattern: '**/{pom.xml,build.gradle,build.gradle.kts}'
  codePattern: ".*"

steps:
  - description: "Add Azure Key Vault key dependency"
    type: "instruction"
    content: |
      Your task is to add Azure Key Vault key dependency to a pom.xml, build.gradle, or build.gradle.kts file. Make sure you add the correct dependencies as below:

      Azure Key Vault keys related dependencies:
      - groupId: com.azure
        artifactId: azure-security-keyvault-keys
        version: 4.9.4
      - groupId: com.azure
        artifactId: azure-identity
        version: 1.15.4

