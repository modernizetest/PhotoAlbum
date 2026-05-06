---
name: migration-javax.email-send-to-azure-communication-service-email
description: Migrates Java applications from JavaMail (javax.mail) API to Azure Communication Service Email for sending emails. Replaces JavaMail email sending, message construction, and authentication with Azure Communication Service equivalents. Use when migrating Java applications from JavaMail or SMTP-based email sending to Azure Communication Service Email.
---

## Migration Scope

This guide focuses **exclusively** on migrating JavaMail to Azure Communication Service Email.

### What is Included:
- JavaMail API usage in application code
- Email sending, receiving, and message construction logic
- Authentication and connection setup for JavaMail
- Mapping of JavaMail concepts to Azure Communication Service Email equivalents

### What is NOT Included:
- **Other email providers**: Migration from providers other than JavaMail (e.g., Exchange, Gmail API, SMTP libraries) is not covered
- **Non-email features**: Integrations with calendar, contacts, or other non-email services are out of scope
- **Infrastructure and deployment**: Infrastructure-as-code, CI/CD pipelines, and deployment configurations are not included
- **Bulk data migration**: The physical transfer of historical email data is not covered
- **Advanced message processing**: Complex message parsing, filtering, or transformation strategies are not fully addressed

**Important**: This guide only covers the application's JavaMail email logic. If your application uses other services or features, migrate those separately using their dedicated guides.
