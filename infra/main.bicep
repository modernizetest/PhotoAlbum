@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Prefix used for naming all resources')
param prefix string = 'photoalbum'

@description('PostgreSQL administrator username')
param postgresAdminUser string = 'photoalbum'

@secure()
@description('PostgreSQL administrator password')
param postgresAdminPassword string

@description('Container image to deploy (e.g. myacr.azurecr.io/photo-album:latest)')
param appContainerImage string = ''

// ── Azure Container Registry ───────────────────────────────────────────────
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: '${replace(prefix, '-', '')}acr'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// ── Log Analytics workspace (required by Container Apps environment) ────────
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${prefix}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ── Container Apps managed environment ─────────────────────────────────────
resource containerAppsEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${prefix}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// ── PostgreSQL Flexible Server ─────────────────────────────────────────────
module database 'database.bicep' = {
  name: 'database'
  params: {
    location: location
    prefix: prefix
    adminUser: postgresAdminUser
    adminPassword: postgresAdminPassword
  }
}

// ── Container App ──────────────────────────────────────────────────────────
module app 'container-app.bicep' = {
  name: 'container-app'
  params: {
    location: location
    prefix: prefix
    containerImage: empty(appContainerImage) ? '${acr.properties.loginServer}/photo-album:latest' : appContainerImage
    acrLoginServer: acr.properties.loginServer
    acrAdminUsername: acr.listCredentials().username
    acrAdminPassword: acr.listCredentials().passwords[0].value
    containerAppsEnvironmentId: containerAppsEnv.id
    postgresHost: database.outputs.postgresHost
    postgresUser: postgresAdminUser
    postgresPassword: postgresAdminPassword
    postgresDatabaseName: database.outputs.postgresDatabaseName
  }
}

// ── Outputs ────────────────────────────────────────────────────────────────
output acrLoginServer string = acr.properties.loginServer
output containerAppFqdn string = app.outputs.containerAppFqdn
output postgresHost string = database.outputs.postgresHost
