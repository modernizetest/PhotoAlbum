---
name: migration-on-premises-user-authentication-to-microsoft-entra-id
description: Migrate the user authentication to Microsoft Entra ID authentication
---

# on-premises-user-authentication-to-microsoft-entra-id

## Overview

Migrate on-premises user authentication (e.g., form login, LDAP) to Microsoft Entra ID using Spring Cloud Azure Active Directory starter.

## Instructions

1. Add dependency `com.azure.spring:spring-cloud-azure-starter-active-directory` (not the B2C variant `spring-cloud-azure-starter-active-directory-b2c`).

2. Update the Spring Security configuration to enable "login with Microsoft Entra ID":
   - If the class extends `WebSecurityConfigurerAdapter`, change it to extend `com.azure.spring.cloud.autoconfigure.aad.AadWebSecurityConfigurerAdapter`.
   - If the class defines a `SecurityFilterChain` bean, apply `com.azure.spring.cloud.autoconfigure.implementation.aad.security.AadWebApplicationHttpSecurityConfigurer.aadWebApplication()` via `http.with(...)`.

3. Merge the new Entra ID login code with existing security rules. Remove conflicting authentication code (`http.formLogin()`, `AuthenticationManagerBuilder` config). Keep all other existing security configuration.

