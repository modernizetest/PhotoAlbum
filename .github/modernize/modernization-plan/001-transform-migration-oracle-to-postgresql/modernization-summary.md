# Modernization Summary: Oracle to PostgreSQL Migration

**Task ID:** 001-transform-migration-oracle-to-postgresql  
**Description:** Migrate from Oracle Database XE 21c to Azure Database for PostgreSQL with managed identity authentication

## Changes Made

### 1. `pom.xml` — Build Configuration
- **Removed:** Oracle JDBC driver (`com.oracle.database.jdbc:ojdbc8`)
- **Added:** PostgreSQL JDBC driver (`org.postgresql:postgresql:42.7.7`)
- **Added:** Azure Identity Extensions (`com.azure:azure-identity-extensions:1.2.2`) for managed identity authentication

### 2. `src/main/resources/application.properties` — Main Configuration
- Changed JDBC URL from `jdbc:oracle:thin:@localhost:1521:XE` to PostgreSQL URL with managed identity authentication plugin (`AzurePostgresqlAuthenticationPlugin`)
- Changed driver class from `oracle.jdbc.OracleDriver` to `org.postgresql.Driver`
- Changed Hibernate dialect from `OracleDialect` to `PostgreSQLDialect`
- Commented out `spring.datasource.username` and `spring.datasource.password` (replaced by managed identity)
- Added example Service Principal authentication URL

### 3. `src/main/resources/application-docker.properties` — Docker Configuration
- Changed JDBC URL from Oracle to PostgreSQL using environment variable placeholders (`${PGHOST}`, `${PGPORT}`, `${PGDATABASE}`)
- Changed driver class and Hibernate dialect to PostgreSQL equivalents
- Retained username/password for local Docker development via env vars

### 4. `src/test/resources/application-test.properties` — Test Configuration
- Updated H2 URL to use `MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DEFAULT_NULL_ORDERING=HIGH` for PostgreSQL compatibility in tests

### 5. `src/main/java/com/photoalbum/model/Photo.java` — Entity
- Removed Oracle-specific `columnDefinition = "NUMBER(19,0)"` from `fileSize` field
- Removed Oracle-specific `columnDefinition = "TIMESTAMP DEFAULT SYSTIMESTAMP"` from `uploadedAt` field
- Hibernate now uses dialect-appropriate types for both PostgreSQL and H2

### 6. `src/main/java/com/photoalbum/repository/PhotoRepository.java` — SQL Queries
All native SQL queries migrated from Oracle to PostgreSQL syntax:

| Method | Oracle Feature | PostgreSQL Equivalent |
|--------|---------------|----------------------|
| `findAllOrderByUploadedAtDesc` | Uppercase identifiers | Lowercase identifiers |
| `findPhotosUploadedBefore` | `ROWNUM <= 10` subquery | `LIMIT 10` |
| `findPhotosUploadedAfter` | `NVL(field, default)` | `COALESCE(field, default)` |
| `findPhotosByUploadMonth` | `TO_CHAR(date, 'YYYY'/'MM')` | `EXTRACT(YEAR/MONTH FROM date)::text` with `LPAD` for zero-padding |
| `findPhotosWithPagination` | `ROWNUM`-based nested query | `ROW_NUMBER() OVER (...)` window function |
| `findPhotosWithStatistics` | Uppercase identifiers | Lowercase identifiers (RANK/SUM OVER natively supported) |

### 7. `src/main/java/com/photoalbum/service/impl/PhotoServiceImpl.java` — Service
- Updated log messages to reference "PostgreSQL database" instead of "Oracle database"

### 8. `docker-compose.yml` — Container Setup
- Replaced Oracle Express 21c service with PostgreSQL 15 service
- Changed healthcheck from `sqlplus` to `pg_isready`
- Updated application environment variables for PostgreSQL connection
- Reduced startup time (Oracle required 180s; PostgreSQL uses 30s)

## Authentication

- **Production (Azure):** Managed Identity via `AzurePostgresqlAuthenticationPlugin` — credential-free, secure
- **Local Docker:** Standard username/password via environment variables
- **Tests:** H2 in-memory database with PostgreSQL compatibility mode

## Build & Test Results

- ✅ **Build:** `mvn clean package` — SUCCESS
- ✅ **Tests:** 1 test run, 0 failures, 0 errors (`PhotoAlbumApplicationTests.contextLoads`)

## Old Technology References Removed

- ❌ `ojdbc8` Oracle JDBC driver
- ❌ `oracle.jdbc.OracleDriver` driver class
- ❌ `OracleDialect` Hibernate dialect
- ❌ `jdbc:oracle:thin:` connection URLs
- ❌ Oracle-specific SQL: `ROWNUM`, `NVL`, `TO_CHAR(date, format)` (non-portable usage)
- ❌ Oracle-specific DDL: `NUMBER(19,0)`, `TIMESTAMP DEFAULT SYSTIMESTAMP`
- ❌ Oracle XE Docker container
- ❌ Oracle-specific log messages
