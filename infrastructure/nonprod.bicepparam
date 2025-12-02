// Non-production environment parameters
// This is the single source of truth for all nonprod deployments

using './modules/foundry_connection/connection.bicep'

// AI Foundry Project Configuration
param projectName = 'adusa-poc-agent'

// Weather Tool Connection Configuration
param connectionName = 'weathertool'
param targetUrl = 'https://wttr.in'
param openApiSpec = loadTextContent('./modules/foundry_connection/api.json')
param authType = 'CustomKeys'
param category = 'CustomKeys'
param apiKey = 'test'

// Common Tags
param tags = {
  environment: 'nonprod'
  managedBy: 'devops'
  project: 'ai-agents'
  toolType: 'weather'
}
