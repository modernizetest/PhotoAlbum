@description('Azure region for the Container App')
param location string

@description('Prefix used for naming resources')
param prefix string

@description('Container image to deploy')
param containerImage string

@description('Azure Container Registry login server')
param acrLoginServer string

@description('Azure Container Registry admin username')
param acrAdminUsername string

@secure()
@description('Azure Container Registry admin password')
param acrAdminPassword string

@description('Container Apps managed environment resource ID')
param containerAppsEnvironmentId string

@description('PostgreSQL server hostname')
param postgresHost string

@description('PostgreSQL username')
param postgresUser string

@secure()
@description('PostgreSQL password')
param postgresPassword string

@description('PostgreSQL database name')
param postgresDatabaseName string

// ── Container App ──────────────────────────────────────────────────────────
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${prefix}-app'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        transport: 'http'
      }
      registries: [
        {
          server: acrLoginServer
          username: acrAdminUsername
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acrAdminPassword
        }
        {
          name: 'db-password'
          value: postgresPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'photo-album'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'SPRING_PROFILES_ACTIVE'
              value: 'azure'
            }
            {
              name: 'SPRING_DATASOURCE_URL'
              value: 'jdbc:postgresql://${postgresHost}:5432/${postgresDatabaseName}?sslmode=require'
            }
            {
              name: 'SPRING_DATASOURCE_USERNAME'
              value: postgresUser
            }
            {
              name: 'SPRING_DATASOURCE_PASSWORD'
              secretRef: 'db-password'
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/actuator/health'
                port: 8080
              }
              initialDelaySeconds: 30
              periodSeconds: 15
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/actuator/health'
                port: 8080
              }
              initialDelaySeconds: 30
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

// ── Outputs ────────────────────────────────────────────────────────────────
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
