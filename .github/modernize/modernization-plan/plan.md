# Modernization Plan: Azure Migration for Photo Album Application

**Project**: Photo Album Java Application

---

## Technical Framework

- **Language**: Java 8 (Java 1.8)
- **Framework**: Spring Boot 2.7.18
- **Build Tool**: Maven 3.9.6
- **Database**: Oracle Database XE 21.3.0
- **Key Dependencies**: Spring Data JPA, Hibernate, Thymeleaf, ojdbc8, commons-io

---

## Overview

This migration will transform the Photo Album application from its current Oracle-based on-premises architecture to a cloud-native Azure deployment. The application currently runs on Oracle Database XE 21c with photos stored as BLOBs in the database. The new architecture will:

- Migrate from Oracle Database to Azure Database for PostgreSQL with managed identity authentication for secure, credential-free database access
- Deploy the containerized application to Azure Container Apps for serverless, auto-scaling container hosting
- Leverage Azure managed services for improved scalability, reliability, and operational efficiency
- Enable secure authentication using managed identities to eliminate credential management

The migration follows a phased approach starting with database migration, followed by application containerization and deployment to Azure Container Apps.

---

## Migration Impact Summary

| Application | Original Service | New Azure Service | Authentication | Comments |
|-------------|------------------|-------------------|----------------|----------|
| Photo Album | Oracle XE 21c | Azure PostgreSQL | Managed Identity | Database migration |
| Photo Album | Local Docker | Azure Container Apps | N/A | Container deployment |

---

## Clarifications

The following items were not explicitly requested but may be needed for a complete implementation:

1. **Infrastructure as Code (IaC) Generation**
   - **Why needed**: To provision Azure resources (PostgreSQL, Container Apps, etc.) in a repeatable, version-controlled manner
   - **Options**: 
     - Bicep (Azure-native IaC)
     - Terraform (Multi-cloud IaC)
   - **Recommendation**: Use Bicep for Azure-native deployments. If you don't explicitly request infrastructure generation, the plan will assume you'll manually provision resources.

2. **Azure Storage for Photo Data**
   - **Why needed**: Currently photos are stored as BLOBs in Oracle Database. Cloud-native approach would use Azure Blob Storage.
   - **Options**:
     - Keep photos in PostgreSQL as BLOBs (simpler migration, fewer changes)
     - Migrate to Azure Blob Storage (better scalability, cost-effective, cloud-native)
   - **Recommendation**: Keep photos in PostgreSQL database unless you specifically request Azure Blob Storage migration to minimize scope.

3. **Authentication and Authorization**
   - **Why needed**: Application currently has no authentication/security layer
   - **Options**:
     - Add Microsoft Entra ID (Azure AD) authentication
     - Implement custom authentication with Azure SQL
     - Keep application open (not recommended for production)
   - **Recommendation**: Application will remain open unless you explicitly request authentication implementation.

4. **Monitoring and Observability**
   - **Why needed**: Production applications need monitoring, logging, and alerting
   - **Options**:
     - Azure Application Insights for APM
     - Azure Monitor for infrastructure monitoring
     - Log Analytics workspace for centralized logging
   - **Recommendation**: These are not included unless explicitly requested.

5. **CI/CD Pipeline**
   - **Why needed**: Automated deployment pipeline for continuous delivery
   - **Options**:
     - GitHub Actions
     - Azure DevOps Pipelines
   - **Recommendation**: Not included in this plan unless explicitly requested.

