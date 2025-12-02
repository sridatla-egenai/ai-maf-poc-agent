// Main Bicep orchestration file
// This file calls the foundry_connection module

targetScope = 'resourceGroup'

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
param connectionType string = 'CustomKeys'

@description('Azure region')
param location string = resourceGroup().location

@description('Resource tags')
param tags object = {}

// Deploy the connection module
module foundryConnection 'modules/foundry_connection/connection.bicep' = {
  name: 'deploy-${connectionName}'
  params: {
    projectName: projectName
    connectionName: connectionName
    targetUrl: targetUrl
    apiKey: apiKey
    connectionType: connectionType
    location: location
    tags: tags
  }
}

// Outputs
output connectionId string = foundryConnection.outputs.connectionId
output connectionName string = foundryConnection.outputs.connectionName
output connectionTarget string = foundryConnection.outputs.connectionTarget
