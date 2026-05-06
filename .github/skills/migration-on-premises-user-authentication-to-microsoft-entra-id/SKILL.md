---
name: migration-on-premises-user-authentication-to-microsoft-entra-id
description: Migrates Java Spring Boot application user authentication from on-premises login to Microsoft Entra ID using spring-cloud-azure-starter-active-directory and spring-boot-starter-oauth2-client. Use when migrating Java web application authentication to Microsoft Entra ID, modernizing on-premises login to cloud identity, or adding Azure Active Directory authentication.
---

Your task is to migrate authentication to Microsoft Entra ID.

## Steps
1. Update dependencies.
  1.1. Use spring-cloud-azure-dependencies (bom) to manage the Spring Cloud Azure dependency version. Choose a version of spring-cloud-azure-dependencies that is compatible with your Spring Boot version:
    - For projects using spring-boot:2.x, spring-cloud-azure-dependencies' version should >=`4.20.0` and < `5.0.0`.
    - For projects using spring-boot:3.x, spring-cloud-azure-dependencies' version should >= `5.22.0` and < `7.0.0`.
    - For projects using spring-boot:4.x, spring-cloud-azure-dependencies' version should >=`7.1.0`.
  1.2. Add 2 new dependencies. CAUTION: WHEN ADDING DEPENDENCIES, DO NOT DELETE ANY EXISTING DEPENDENCIES. DELETING EXISTING DEPENDENCIES MAY CAUSE COMPILE ERROR.
    - com.azure.spring:spring-cloud-azure-starter-active-directory
    - org.springframework.boot:spring-boot-starter-oauth2-client
  1.3. After new dependencies added, double check that no original dependencies deleted. Including the original dependencies related to original login method.
2. Update properties.
  2.1. These properties should be added:
    - spring.cloud.azure.active-directory.enabled: true
    - spring.cloud.azure.active-directory.profile.tenant-id: ${AZURE_TENANT_ID}
    - spring.cloud.azure.active-directory.credential.client-id: ${AZURE_CLIENT_ID}
    - spring.cloud.azure.active-directory.credential.client-secret: ${AZURE_CLIENT_SECRET}
  2.2. Add a new comment for the newly added properties:
    - Refer to this link to get more information about these properties: https://learn.microsoft.com/en-us/azure/developer/java/spring-framework/spring-security-support
  2.3. Delete all properties that will not take effect due to using the new authentication method.
3. Update Java code.
  3.1. Add "login with Microsoft Entra ID" related code by choosing one of the two options.
    3.1.1. If the current configuration class extends WebSecurityConfigurerAdapter, then do the following things:
        - Change WebSecurityConfigurerAdapter to AadWebSecurityConfigurerAdapter
        - Add "http.authorizeRequests().antMatchers("/login").permitAll().anyRequest().authenticated();" in the "configure" method.
        Example:
        ```java
        import com.azure.spring.cloud.autoconfigure.aad.AadWebSecurityConfigurerAdapter;
        public static class ExampleWebSecurityConfigurerAdapter extends AadWebSecurityConfigurerAdapter {
            @Override
            protected void configure(HttpSecurity http) throws Exception {
                super.configure(http);
                http.authorizeRequests()
                        .antMatchers("/login").permitAll()
                        .anyRequest().authenticated();
                // Continue with the action step described below: Merge newly added code and original code.
            }
        }
        ```
    3.1.2. If the current configuration defines a SecurityFilterChain bean, then add "login with Microsoft Entra ID" related code in the bean definition method.
        - Apply AadWebApplicationHttpSecurityConfigurer by "http.with(AadWebApplicationHttpSecurityConfigurer.aadWebApplication(), Customizer.withDefaults())".
        - Add ".authorizeHttpRequests(requests -> requests.requestMatchers("/login").permitAll().anyRequest().authenticated());".
        Example:
        ```java
        import com.azure.spring.cloud.autoconfigure.implementation.aad.security.AadWebApplicationHttpSecurityConfigurer;
        public class ExampleSecurityConfig {
            @Bean
            public SecurityFilterChain htmlWebFilterChain(HttpSecurity http) throws Exception {
                http.with(AadWebApplicationHttpSecurityConfigurer.aadWebApplication(), Customizer.withDefaults())
                    .authorizeHttpRequests(requests -> requests
                        .requestMatchers("/login").permitAll()
                        .anyRequest().authenticated());
                return http.build();
                // Continue with the action step described below: Merge newly added code and original code.
            }
        }
        ```
  3.2. Merge newly added code and original code.
    - When keeping original code, make as few modifications as possible.
        - Don't change code format like indentation.
        - Don't add or delete line breaks or empty lines.
        - Don't delete code comments.
        - Don't refactor code.
    - If there is http.authorizeRequests() (or http.authorizeHttpRequests()) in original code, merge original code and newly added code. Follow these rules:
        - When using AadWebSecurityConfigurerAdapter, use http.authorizeRequests().
        - When defining a SecurityFilterChain bean, use http.authorizeHttpRequests().
        - The original http.authorizeRequests() (or http.authorizeHttpRequests()) may be inside other methods that are called by the "configure" method instead of in the "configure" method directly. Move the newly added code to the place beside original related code.
        - Merge sub methods after authorizeRequests() (or http.authorizeHttpRequests()) of original code and newly added code instead of calling authorizeRequests() (or http.authorizeHttpRequests()) twice.
        - Don't delete original business logic like "requestMatchers(...)", "antMatchers(...)" and "antMatcher(...)". CAUTION: KEEP ORIGINAL "and()" METHOD BEFORE "antMatcher(...)", LACKING THE "and()" METHOD BEFORE "antMatcher(...)" MAY CAUSE COMPILE ERRORS.
    - Keep other original HttpSecurity configuring code. Examples:
        - http.logout()
        - http.csrf()
        - http.requiresChannel()
    - Delete other HttpSecurity configuring code that conflicts with login method (login with Microsoft Entra ID). Examples:
        - Delete original authentication-related code, example: http.authenticationManager()
        - Delete original form login-related code, example: http.formLogin()
  3.3. Delete other code that conflicts with "login with Microsoft Entra ID". Examples:
    - AuthenticationManagerBuilder configuration related code.
  3.4. Make sure no B2C related content is added. The newly added dependency is spring-cloud-azure-starter-active-directory, not spring-cloud-azure-starter-active-directory-b2c. Don't import any B2C-related classes in Java code.
  3.5. Refine imports.
    - Delete unused imports. Double check that they are not used anymore before deleting them. Note that "org.springframework.security.config.annotation.web.builders.HttpSecurity;" should not be deleted when it is still being used.
    - Add missing imports. Sort the newly added imports according to the existing order rule of the current file.
