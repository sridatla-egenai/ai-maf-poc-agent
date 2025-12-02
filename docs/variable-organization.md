# Variable Groups Organization Strategy

## Azure DevOps Variable Groups (Acts as "Folders")

### 1. Create Variable Groups in Azure DevOps

Navigate to: **Pipelines > Library > + Variable group**

#### Group: `ai-agent-config-nonprod`
**Purpose**: Non-sensitive configuration for non-production
```
FOUNDRY_ENDPOINT = https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent
PROJECT_NAME = adusa-poc-agent
RESOURCE_GROUP = rg-ai-agents-nonprod
LOCATION = eastus
CONNECTION_NAME = todo-api-connection
CONNECTION_TARGET_URL = https://product-api-main-98dd1cf.zuplo.site
AGENT_YAML_PATH = agents/simple-agent.yaml
```

#### Group: `ai-agent-secrets-nonprod` ⚠️ (Mark variables as secret)
**Purpose**: Sensitive credentials for non-production
```
TODO_API_KEY = zpka_8989f84eb04a4cf3bdeef393fd50f751_e9b42445  [Secret]
AZURE_SERVICE_CONNECTION = ado-service-connection
```

#### Group: `ai-agent-config-prod`
**Purpose**: Production configuration
```
FOUNDRY_ENDPOINT = https://prod-agent.services.ai.azure.com/api/projects/prod-agent
PROJECT_NAME = prod-agent
RESOURCE_GROUP = rg-ai-agents-prod
LOCATION = eastus
CONNECTION_NAME = todo-api-connection
CONNECTION_TARGET_URL = https://api.production.com
AGENT_YAML_PATH = agents/simple-agent.yaml
```

#### Group: `ai-agent-secrets-prod` ⚠️
**Purpose**: Production secrets
```
TODO_API_KEY = [Production API Key]  [Secret]
AZURE_SERVICE_CONNECTION = ado-service-connection-prod
```

---

## Updated Pipeline with Variable Groups

```yaml
trigger:
  branches:
    include:
      - main

# Reference variable groups based on environment
variables:
  - ${{ if eq(variables['Build.SourceBranchName'], 'main') }}:
    - group: ai-agent-config-nonprod
    - group: ai-agent-secrets-nonprod
  
  - ${{ if eq(variables['Build.SourceBranchName'], 'release') }}:
    - group: ai-agent-config-prod
    - group: ai-agent-secrets-prod

stages:
  - stage: DeployInfrastructure
    displayName: 'Deploy Infrastructure'
    jobs:
      - job: DeployConnection
        pool: 'egen-agent-pool'
        steps:
          - task: AzureResourceManagerTemplateDeployment@3
            displayName: 'Deploy Connection'
            inputs:
              azureResourceManagerConnection: '$(AZURE_SERVICE_CONNECTION)'
              resourceGroupName: '$(RESOURCE_GROUP)'
              location: '$(LOCATION)'
              csmFile: 'infrastructure/connection.bicep'
              overrideParameters: >
                -projectName $(PROJECT_NAME)
                -connectionName $(CONNECTION_NAME)
                -targetUrl $(CONNECTION_TARGET_URL)
                -apiKey $(TODO_API_KEY)
```

---

## Alternative: Environment-Specific Parameter Files

If you prefer file-based configuration:

### Directory Structure
```
infrastructure/
├── connection.bicep
└── parameters/
    ├── nonprod.parameters.json
    └── prod.parameters.json
```

### nonprod.parameters.json
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "projectName": {
      "value": "adusa-poc-agent"
    },
    "connectionName": {
      "value": "todo-api-connection"
    },
    "targetUrl": {
      "value": "https://product-api-main-98dd1cf.zuplo.site"
    }
  }
}
```

Then in pipeline:
```yaml
- task: AzureResourceManagerTemplateDeployment@3
  inputs:
    csmFile: 'infrastructure/connection.bicep'
    csmParametersFile: 'infrastructure/parameters/$(ENVIRONMENT).parameters.json'
    overrideParameters: '-apiKey $(TODO_API_KEY)'  # Only secret from variable
```

---

## Recommended Approach

**Use Variable Groups** because:
1. ✅ Centralized management in Azure DevOps UI
2. ✅ Easy to update without code changes
3. ✅ Built-in secret masking
4. ✅ Can link to Azure Key Vault
5. ✅ Environment-specific groups act as "folders"

**Avoid hardcoding** in parameter files for:
- API keys
- Connection strings
- Passwords
- Tokens
