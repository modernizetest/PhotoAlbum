---
name: migration-cache-related-code-to-redis
description: Migrate cache related code to use Redis, and potentially to Azure Managed Redis / Azure Cache for Redis (retiring) while following best practices. Use this skill when users want to migrate their cache related code to use Redis, such as Apache Commons JCS, DynaCache, Embedded cache, JCache, OSCache, ShiftOne, Oracle Coherence, etc., or local Redis to Azure Managed Redis / Azure Cache for Redis (retiring) with secure authentication changes.
---

# Migrate Cache Related Code to Redis

A skill to provide knowledge about migrating cache related code to use Redis.

At a high level, the process of migrating cache related code to Redis involves:

1. Update the library dependencies: remove the old caching library dependencies and add the appropriate Redis client library dependencies.
2. Update the code logic to use Redis API instead of the old caching library API
3. Handle authentication and connection management for Redis, especially if migrating to Azure Managed Redis which may involve passwordless authentication using Azure Entra ID.
4. Update the related configuration entries.

When migrating to Azure Managed Redis, it's recommended to use passwordless authentication with Azure Entra ID for better security. For migrations targeting Azure Managed Redis, the specific code changes should be based on the framework and libraries the project is currently using, as written below.

Note: Azure Cache for Redis is retiring and there are limitations on new provisioning. For existing instances, the passwordless authentication experience is similar to Azure Managed Redis, as shown in the code examples below. The default port for Azure Cache for Redis is 6380, while for Azure Managed Redis it's 10000.

## Spring Boot applications

1. Add the `com.azure.spring:spring-cloud-azure-dependencies` to your dependency management to manage Spring Cloud Azure dependencies.
    * For Spring Boot 4.0.x, be sure to set the spring-cloud-azure-dependencies version to 7.0.0 or later.
    * For Spring Boot 3.5.x, be sure to set the spring-cloud-azure-dependencies version to 6.1.0 or later.
    * For Spring Boot 3.1.x-3.4.x, be sure to set the spring-cloud-azure-dependencies version to 5.25.0 or later.
    * For Spring Boot 2.x, be sure to set the spring-cloud-azure-dependencies version to 4.20.0 or later.
2. Add Redis related starter from Spring Cloud Azure
    * For Spring Cloud Azure 4.x: `com.azure.spring:spring-cloud-azure-starter-redis`
    * For other versions: `com.azure.spring:spring-cloud-azure-starter-data-redis-lettuce`
3. Update the configuration to enable passwordless authentication:
    * For Spring Cloud Azure 4.x. The configuration properties start with `spring.redis`:
        ```yaml
        spring:
          redis:
            host: ${AZURE_MANAGED_REDIS_HOST}
            #username: ${AZURE_MANAGED_REDIS_USERNAME}
            port: 10000
            ssl: true
            azure:
              passwordless-enabled: true
        ```
    * For other versions, the configuration properties start with `spring.data.redis`:
        ```yaml
        spring:
          data:
            redis:
              host: ${AZURE_MANAGED_REDIS_HOST}
              #username: ${AZURE_MANAGED_REDIS_USERNAME}
              port: 10000
              ssl:
                enabled: true
              azure:
                passwordless-enabled: true
        ```
4. Spring Cloud Azure will automatically configure the `RedisConnectionFactory` and `RedisTemplate` beans to use passwordless authentication with Azure Entra ID. Update your code to inject and use these beans instead of creating Redis connections manually, just like you would with any other Spring Data Redis setup.

## Non-Spring Boot Java applications with Jedis

1. Add the following dependencies to your project:
    * `redis.clients:jedis` with version `7.2.0` or later for Jedis support.
    * `com.azure:azure-identity` to handle Azure Entra ID authentication.
    * `redis.clients.authentication:redis-authx-entraid:0.1.1-beta2` for utility classes that help with Azure Entra ID authentication.
2. Create a `DefaultAzureCredential` instance to obtain authentication tokens, and use it together with the Azure Redis scope to build a `redis.clients.authentication.core.TokenAuthConfig` via `redis.clients.authentication.entraid.AzureTokenAuthConfigBuilder`. This auth config will be used with Jedis.
3. Use the resulting `TokenAuthConfig` to create a `redis.clients.jedis.RedisClient` instance (for example, via `redis.clients.jedis.authentication.AuthXManager`), which handles token refresh with the corresponding auth config. It has APIs similar to the `Jedis` class and can be used as a singleton that automatically handles thread-safety and connection pooling.
    * `redis.clients.jedis.RedisClient` is `AutoCloseable` and should be closed when the application shuts down to release resources.
4. Example code.
    ```java
    import com.azure.identity.DefaultAzureCredential;
    import com.azure.identity.DefaultAzureCredentialBuilder;
    import java.util.Optional;
    import java.util.Collections;
    import redis.clients.authentication.core.TokenAuthConfig;
    import redis.clients.authentication.entraid.AzureTokenAuthConfigBuilder;
    import redis.clients.jedis.ConnectionPoolConfig;
    import redis.clients.jedis.DefaultJedisClientConfig;
    import redis.clients.jedis.RedisClient;
    import redis.clients.jedis.authentication.AuthXManager;

    final String SCOPE = "https://redis.azure.com/.default";
    // For Mooncake, use `https://*.cacheinfra.windows.net.china:10225/appid/.default`
    // For US Government, use `https://*.cacheinfra.windows.us.government.net:10225/appid/.default`
    final DefaultAzureCredential CREDENTIAL = new DefaultAzureCredentialBuilder().build();

    TokenAuthConfig authConfig = AzureTokenAuthConfigBuilder.builder()
        .defaultAzureCredential(CREDENTIAL)
        .scopes(Collections.singleton(SCOPE))
        .tokenRequestExecTimeoutInMs(5000)
        .build();

    RedisClient client = RedisClient.builder()
        .hostAndPort(System.getenv("REDIS_HOST"), Optional.ofNullable(System.getenv("REDIS_PORT")).map(Integer::parseInt).orElse(10000))
        .clientConfig(DefaultJedisClientConfig.builder()
            .authXManager(new AuthXManager(authConfig))
            .ssl(true)
            .build())
        .poolConfig(new ConnectionPoolConfig())
        .build();

    // use client elsewhere
    client.set("name", "jedis");
    ```

## Non-Spring Boot Java applications with Lettuce

1. Add the following dependencies to your project:
    * `io.lettuce:lettuce-core` for Lettuce support.
    * `com.azure:azure-identity` to handle Azure Entra ID authentication.
    * Add `redis.clients.authentication:redis-authx-entraid:0.1.1-beta2` to your project for utility classes that help with Azure Entra ID authentication.
2. Create a `DefaultAzureCredential` instance to obtain authentication tokens. And use it to create the `redis.clients.authentication.core.IdentityProvider` implementation that can be used with Lettuce.
3. Create a `TokenBasedRedisCredentialsProvider` with the auth config, which can be used in Lettuce client configuration to handle passwordless authentication and token refresh.
4. Create a Lettuce `io.lettuce.core.RedisClient` that handles the credential refresh with the auth config. It should be used as a singleton.
5. Create a `io.lettuce.core.api.StatefulRedisConnection<String, String>` instance from the Lettuce `RedisClient`, which can be shared and used in a thread-safe manner.
6. Note:
    * `io.lettuce.core.RedisClient`, `io.lettuce.core.api.StatefulRedisConnection<String, String>` and `TokenBasedRedisCredentialsProvider` are `AutoCloseable` and should be closed when the application shuts down to release resources.
    * Given that the client and connection are designed to be shared and thread-safe, wrap them in a utility class where appropriate.
7. Example code.
    ```java
    import com.azure.identity.DefaultAzureCredential;
    import com.azure.identity.DefaultAzureCredentialBuilder;
    import io.lettuce.authx.TokenBasedRedisCredentialsProvider;
    import io.lettuce.core.ClientOptions;
    import io.lettuce.core.RedisClient;
    import io.lettuce.core.RedisURI;
    import io.lettuce.core.api.StatefulRedisConnection;
    import redis.clients.authentication.core.TokenAuthConfig;
    import redis.clients.authentication.entraid.AzureTokenAuthConfigBuilder;
    import java.util.Optional;
    import java.util.Collections;

    final String SCOPE = "https://redis.azure.com/.default";
    // For Mooncake, use `https://*.cacheinfra.windows.net.china:10225/appid/.default`
    // For US Government, use `https://*.cacheinfra.windows.us.government.net:10225/appid/.default`
    final DefaultAzureCredential CREDENTIAL = new DefaultAzureCredentialBuilder().build();

    TokenAuthConfig authConfig = AzureTokenAuthConfigBuilder.builder()
        .defaultAzureCredential(CREDENTIAL)
        .scopes(Collections.singleton(SCOPE))
        .tokenRequestExecTimeoutInMs(5000)
        .build();

    TokenBasedRedisCredentialsProvider credentialsProvider = TokenBasedRedisCredentialsProvider.create(authConfig);

    RedisURI redisUri = RedisURI.builder()
        .withHost(System.getenv("REDIS_HOST"))
        .withPort(Optional.ofNullable(System.getenv("REDIS_PORT")).map(Integer::parseInt).orElse(10000))
        .withSsl(true)
        .withAuthentication(credentialsProvider)
        .build();

    RedisClient redisClient = RedisClient.create(redisUri);
    redisClient.setOptions(ClientOptions.builder().reauthenticateBehavior(ClientOptions.ReauthenticateBehavior.ON_NEW_CREDENTIALS).build());

    StatefulRedisConnection<String, String> connection = redisClient.connect();

    // use the connection elsewhere
    connection.sync().set("name", "lettuce");
    ```
