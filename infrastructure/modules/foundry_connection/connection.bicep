// Bicep module for creating Azure AI Foundry OpenAPI Tool Connections
// This creates a connection that includes both authentication AND the OpenAPI specification

@description('Name of the AI Foundry project')
param projectName string

@description('Name of the connection to create')
param connectionName string

@description('Target URL for the API')
param targetUrl string

@description('OpenAPI specification URL or inline spec')
param openApiSpec string = ''

@description('API Key for authentication (optional for public APIs)')
@secure()
param apiKey string = ''

@description('Auth type')
@allowed([
  'None'
  'CustomKeys'
  'OAuth'
])
param authType string = 'CustomKeys'

@description('Connection category')
@allowed([
  'CustomKeys'
  'ApiKey'
  'OAuth'
  'RemoteTool'
])
param category string = 'CustomKeys'

@description('Additional metadata tags')
param tags object = {}

// Reference to existing AI Foundry account (hub)
resource aiAccount 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: projectName
}

// Reference to existing AI Foundry project
resource aiFoundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' existing = {
  parent: aiAccount
  name: projectName
}

// Create the OpenAPI tool connection
resource connection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = {
  parent: aiFoundryProject
  name: connectionName
  properties: {
    category: category
    target: targetUrl
    authType: 'CustomKeys'
    group: 'AzureAI'
    credentials: authType == 'ApiKey' || authType == 'CustomKeys' ? {
      keys:{
          name: 'apiKey'
          value: apiKey
        }
    } : null
    metadata: union({
      type: 'openapi'
      OpenApiSpec: openApiSpec
    }, tags)
  }
}
// Outputs
output connectionId string = connection.id
output connectionName string = connection.name
output connectionTarget string = targetUrl
