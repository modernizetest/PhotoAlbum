# Modernization Plan: PhotoAlbum Java — Migrate to Azure

**Project**: PhotoAlbum-Java

---

## Technical Framework

- **Language**: Java 8 (JDK 1.8)
- **Framework**: Spring Boot 2.7.18
- **Build Tool**: Maven 3.x
- **Database**: Oracle Database (Free 23ai), JDBC with plaintext credentials
- **Key Dependencies**: Spring Data JPA, Hibernate, Spring MVC (Thymeleaf), Commons IO
- **Containerization**: Dockerfile present

---

## Overview

This migration modernizes the PhotoAlbum Java application to run on Azure. The application currently stores photos as Oracle BLOBs and connects to Oracle Database using plaintext credentials configured via `application.properties`. The new architecture will:

- Replace Oracle Database with Azure Database for PostgreSQL, enabling a fully managed, cloud-native relational database service

The migration follows a phased approach: first modernizing the data tier and credentials.

---

## Migration Impact Summary

| Application       | Original Service       | New Azure Service                  | Authentication   | Comments                             |
|-------------------|------------------------|------------------------------------|------------------|--------------------------------------|
| PhotoAlbum-Java   | Oracle Database        | Azure Database for PostgreSQL      | Managed Identity | Migrate BLOB/data model to pg bytea  |
---

## Migration Tasks

### Task 1 — Migrate Oracle Database to Azure Database for PostgreSQL

Migrate the Oracle JDBC data source, JPA dialect, SQL syntax, and schema definitions to Azure Database for PostgreSQL. Replace the Oracle JDBC driver with the PostgreSQL driver. Update Spring datasource configuration and Hibernate dialect. Convert any Oracle-specific SQL in repositories to PostgreSQL-compatible equivalents, including BLOB storage (Oracle BLOB → PostgreSQL bytea).

**Skill**: `migration-oracle-to-postgresql`

---