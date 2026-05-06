---
name: migration-sybase-ase-to-azure-sql-database
description: Migrates Java application database layer from Sybase ASE (Adaptive Server Enterprise) to Azure SQL Database with passwordless managed identity authentication. Use when migrating Java applications from Sybase ASE to Azure SQL.
---

Your task is to migrate the database of a Java project from Sybase ASE to Azure SQL Database.

## Requirements

1. **Authentication**: Use passwordless authentication with a user-assigned managed identity. (Add comments for service principal alternatives.)
2. **Inspection**: Check and update all files related to Sybase ASE. For example, all files with the `.sql` suffix (such as `data.sql`) should be inspected and updated to use Azure SQL Database syntax if it's used for Sybase ASE.
3. **Follow best practices**: The new code should follow best practices for modern SQL Server. Here are some examples:
3.1. Error Handling
```diff
-UPDATE employees
-SET salary = salary * 1.1;
-IF @@error != 0
-    PRINT 'Error occurred!';
+BEGIN TRY
+    UPDATE employees
+    SET salary = salary * 1.1;
+END TRY
+BEGIN CATCH
+    PRINT 'Error occurred!';
+    PRINT ERROR_MESSAGE();
+END CATCH;
```
3.2. System Stored Procedures and Metadata Queries
```diff
-sp_help 'table_name';
+EXEC sp_help 'table_name';
```
3.3. Data Type Differences
```diff
-DECLARE @myDate DATETIME
+DECLARE @myDate DATETIME2
```
4. **Cleanup**: Remove Sybase-specific files (e.g., `jconn3.jar`, `jconn4.jar`) and dependencies from `pom.xml`/`build.gradle`
