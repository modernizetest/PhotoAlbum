---
name: migration-jax-rpc-to-jax-ws
description: Migrates Java web service implementations from deprecated JAX-RPC to JAX-WS. Updates web service configuration files and JAX-RPC specific code to use JAX-WS equivalents. Use when modernizing Java web services that use JAX-RPC or upgrading deprecated JAX-RPC APIs to the JAX-WS standard.
---

Migrate JAX-RPC to JAX-WS for current project. Requirements:
 - When modify files, double check whether it's necessary, don't do unnecessary change. For example
   - Don't add new business logic.
   - Don't delete existing business logic.
   - Don't upgrade dependency's version if original version can still work.
 - When adding new dependencies, double check the version is compatible with existing java version and tomcat version.
 - When updating web.xml, double check it's compatible with existing tomcat version.
 - Delete unused files. Example: JAX-RPC configuration files.
