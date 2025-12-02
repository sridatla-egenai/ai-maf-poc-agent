// Bicep module for creating Azure AI Foundry Connections
// This module creates a Microsoft.CognitiveServices/accounts/projects/connections resource

@description('Name of the AI Foundry project')
param projectName string

@description('Name of the connection to create')
param connectionName string

@description('Target URL for the API')
param targetUrl string

@description('API Key for authentication')
@secure()
param apiKey string

@description('Connection type')
@allowed([
  'CustomKeys'
  'ApiKey'
  'OAuth'
])
param connectionType string = 'CustomKeys'

@description('Azure region')
param location string = resourceGroup().location

@description('Additional metadata tags')
param tags object = {}

// Reference to existing AI Foundry workspace/project
resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-01-01-preview' existing = {
  name: projectName
}

// Create the connection
resource connection 'Microsoft.MachineLearningServices/workspaces/connections@2024-01-01-preview' = {
  parent: aiProject
  name: connectionName
  properties: {
    category: connectionType
    target: targetUrl
    authType: 'ApiKey'
    credentials: {
      key: apiKey
    }
    metadata: union({
      deployedBy: 'bicep'
    }, tags)
  }
}

// Outputs
output connectionId string = connection.id
output connectionName string = connection.name
output connectionTarget string = targetUrl
