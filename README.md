# Photo Album Application - Java Spring Boot with PostgreSQL on Azure

A simple photo storage and gallery application built with Spring Boot and PostgreSQL, featuring drag-and-drop upload, responsive gallery view, and full-size photo details with navigation. Deployable locally with Docker Compose or to Azure using Container Apps and Azure Database for PostgreSQL.

## Features

- 📤 **Photo Upload**: Drag-and-drop or click to upload multiple photos
- 🖼️ **Gallery View**: Responsive grid layout for browsing uploaded photos  
- 🔍 **Photo Detail View**: Click any photo to view full-size with metadata and navigation
- 📊 **Metadata Display**: View file size, dimensions, aspect ratio, and upload timestamp
- ⬅️➡️ **Photo Navigation**: Previous/Next buttons to browse through photos
- ✅ **Validation**: File type and size validation (JPEG, PNG, GIF, WebP; max 10MB)
- 🗄️ **Database Storage**: Photo data stored as BLOBs in PostgreSQL
- 🗑️ **Delete Photos**: Remove photos from both gallery and detail views
- 🎨 **Modern UI**: Clean, responsive design with Bootstrap 5
- ☁️ **Azure Ready**: One-command infrastructure provisioning and deployment

## Technology Stack

- **Framework**: Spring Boot 2.7.18 (Java 8)
- **Database**: PostgreSQL 15 (local) / Azure Database for PostgreSQL Flexible Server (cloud)
- **Templating**: Thymeleaf
- **Build Tool**: Maven
- **Frontend**: Bootstrap 5.3.0, Vanilla JavaScript
- **Containerization**: Docker & Docker Compose
- **Cloud**: Azure Container Apps, Azure Container Registry

## Prerequisites

### Local Development
- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

### Azure Deployment
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed and logged in (`az login`)
- Docker Desktop running (for building and pushing the image)
- An active Azure subscription

## Quick Start (Local)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd PhotoAlbum
   ```

2. **Start the application**:
   ```bash
   docker-compose up --build
   ```

   This will:
   - Start a PostgreSQL 15 container
   - Build the Java Spring Boot application
   - Start the Photo Album application container
   - Automatically create the database schema using JPA/Hibernate

3. **Access the application**:
   - Open your browser and navigate to: **http://localhost:8080**

## Azure Deployment

### 1. Provision Azure infrastructure

```bash
# Interactive – prompts for the PostgreSQL password
./azure-setup.sh

# Or pass all values explicitly
POSTGRES_ADMIN_PASSWORD='YourStr0ngP@ssword' \
  ./azure-setup.sh \
    --location eastus \
    --prefix photoalbum \
    --resource-group photoalbum-rg
```

This creates in Azure:
- **Resource Group** `photoalbum-rg`
- **Azure Container Registry** (ACR) – stores the Docker image
- **Log Analytics workspace** – Container Apps logging
- **Container Apps managed environment**
- **Azure Database for PostgreSQL Flexible Server** (Burstable B1ms, PostgreSQL 15)
- **Azure Container App** – runs the Spring Boot application

### 2. Build & deploy the application image

```bash
POSTGRES_ADMIN_PASSWORD='YourStr0ngP@ssword' \
  ./deploy-to-azure.sh \
    --resource-group photoalbum-rg \
    --prefix photoalbum
```

Or with an explicit ACR and image tag:

```bash
./deploy-to-azure.sh \
  --resource-group photoalbum-rg \
  --acr photoalbumacr.azurecr.io \
  --tag v1.0.0
```

The script:
1. Builds the Docker image locally
2. Logs in to ACR and pushes the image
3. Updates the running Container App with the new image
4. Prints the application URL

### Re-deploying after code changes

```bash
./deploy-to-azure.sh --resource-group photoalbum-rg --prefix photoalbum --tag $(date +%Y%m%d%H%M%S)
```

## Services

### PostgreSQL Database (local)
- **Image**: `postgres:15`
- **Port**: `5432`
- **Database / User / Password**: `photoalbum / photoalbum / photoalbum`

### Azure Database for PostgreSQL Flexible Server (cloud)
- **SKU**: Standard_B1ms (Burstable)
- **Version**: PostgreSQL 15
- **Storage**: 32 GB
- **Backup retention**: 7 days

### Photo Album Java Application
- **Port**: `8080`
- **Framework**: Spring Boot 2.7.18
- **Java Version**: 8
- **Photo Storage**: All photos stored as BLOBs in the database

## Database Schema

The application uses Spring Data JPA with Hibernate for automatic schema management.

### PHOTOS Table
- `id` (VARCHAR(36), Primary Key, UUID)
- `original_file_name` (VARCHAR(255), Not Null)
- `stored_file_name` (VARCHAR(255), Not Null)
- `file_path` (VARCHAR(500), Nullable)
- `file_size` (BIGINT, Not Null)
- `mime_type` (VARCHAR(50), Not Null)
- `uploaded_at` (TIMESTAMP, Not Null)
- `width` (INTEGER, Nullable)
- `height` (INTEGER, Nullable)
- `photo_data` (BYTEA / BLOB, Not Null)

### Indexes
- `idx_photos_uploaded_at` on `uploaded_at`

## Development

### Running Locally (without Docker)

1. **Start a local PostgreSQL instance** (e.g. via `brew services start postgresql@15`)
2. **Create the database and user**:
   ```sql
   CREATE USER photoalbum WITH PASSWORD 'photoalbum';
   CREATE DATABASE photoalbum OWNER photoalbum;
   ```
3. **Run the application**:
   ```bash
   mvn spring-boot:run
   ```

### Building from Source

```bash
mvn clean package -DskipTests
java -jar target/photo-album-1.0.0.jar
```

### Running Tests

```bash
mvn test
```

Tests use an in-memory H2 database – no external services required.

## Project Structure

```
PhotoAlbum/
├── src/main/java/com/photoalbum/    # Java source code
│   ├── controller/                  # Spring MVC controllers
│   ├── model/                       # JPA entities
│   ├── repository/                  # Data access layer
│   ├── service/                     # Business logic
│   └── config/                      # Configuration classes
├── src/main/resources/              # Application resources
│   ├── templates/                   # Thymeleaf templates
│   ├── static/                      # Static web assets (CSS, JS)
│   ├── application.properties       # Local configuration (PostgreSQL)
│   ├── application-docker.properties # Docker Compose profile
│   └── application-azure.properties  # Azure profile
├── infra/                           # Azure infrastructure (Bicep)
│   ├── main.bicep                   # Main template
│   ├── container-app.bicep          # Container Apps configuration
│   └── database.bicep               # PostgreSQL configuration
├── docker-compose.yml               # Local development services
├── Dockerfile                       # Application container build
├── azure-setup.sh                   # Azure infrastructure provisioning
├── deploy-to-azure.sh               # Application deployment to Azure
├── pom.xml                          # Maven dependencies
└── README.md                        # This file
```

## Troubleshooting

### Database connection errors (local)
```bash
# Verify PostgreSQL container is healthy
docker-compose ps
docker-compose logs postgres-db
```

### Application logs (local)
```bash
docker-compose logs photoalbum-java-app
```

### Rebuild (local)
```bash
docker-compose up --build
```

### Reset database (local)
```bash
docker-compose down -v
docker-compose up --build
```

### Azure Container App logs
```bash
az containerapp logs show \
  --name photoalbum-app \
  --resource-group photoalbum-rg \
  --follow
```

## Stopping the Application

```bash
# Local – stop services
docker-compose down

# Local – stop and remove all data
docker-compose down -v

# Azure – scale to zero (keeps infrastructure)
az containerapp update \
  --name photoalbum-app \
  --resource-group photoalbum-rg \
  --min-replicas 0 --max-replicas 0
```

## Performance Notes

- Azure Database for PostgreSQL Flexible Server B1ms is suitable for development and low-traffic workloads. Scale up the SKU for production use.
- BLOB storage in the database impacts performance at scale; consider migrating photo files to Azure Blob Storage for large deployments.

## Contributing

When contributing to this project:

- Follow Spring Boot best practices
- Maintain database compatibility
- Ensure UI/UX consistency
- Test both local Docker and Azure deployment scenarios
- Update documentation for any architectural changes
- Preserve UUID system integrity
- Add appropriate tests for new features

## License

This project is provided as-is for educational and demonstration purposes.