# Infrastructure

This directory contains all infrastructure-as-code for the AI Agent project.

## Directory Structure

```
infrastructure/
├── main.bicep                          # Main orchestration file
├── modules/                            # Bicep modules
│   └── foundry_connection/
│       └── connection.bicep            # Connection module
└── variables/                          # Environment variables (YAML)
    ├── nonprod.yaml                    # Non-production config
    └── prod.yaml                       # Production config
```

## Usage

### Local Deployment

```bash
# Set the API key (never commit this!)
export TODO_API_KEY="your-api-key-here"

# Deploy to nonprod
python scripts/deploy_infrastructure.py nonprod

# Deploy to prod
python scripts/deploy_infrastructure.py prod
```

### CI/CD Deployment

The pipeline automatically:
1. Loads variables from `infrastructure/variables/{environment}.yaml`
2. Gets secrets from Azure DevOps Variable Groups
3. Deploys using `scripts/deploy_infrastructure.py`

## Adding New Modules

To add a new infrastructure module:

1. Create a new directory under `modules/`:
   ```
   infrastructure/modules/my_module/
   └── my_resource.bicep
   ```

2. Add parameters to `main.bicep`:
   ```bicep
   module myModule 'modules/my_module/my_resource.bicep' = {
     name: 'deploy-my-resource'
     params: {
       // parameters here
     }
   }
   ```

3. Add configuration to `variables/{env}.yaml`:
   ```yaml
   myModule:
     param1: value1
     param2: value2
   ```

4. Update `scripts/deploy_infrastructure.py` to pass the new parameters.

## Environment Variables

All environment-specific configuration is stored in YAML files under `variables/`.

### Structure

```yaml
environment: nonprod

azure:
  resourceGroup: rg-name
  location: eastus
  serviceConnection: connection-name

foundry:
  projectName: project-name
  endpoint: https://...

connection:
  name: connection-name
  targetUrl: https://...
  type: CustomKeys

tags:
  environment: nonprod
  managedBy: devops
```

### Secrets

**Never** store secrets in YAML files. Always use:
- Azure DevOps Variable Groups (marked as secret)
- Azure Key Vault
- Environment variables in the pipeline

## Bicep Modules

### foundry_connection

Creates an Azure AI Foundry Connection resource.

**Parameters:**
- `projectName`: Name of the AI Foundry project
- `connectionName`: Name of the connection
- `targetUrl`: API endpoint URL
- `apiKey`: API key (secure parameter)
- `connectionType`: Type of connection (CustomKeys, ApiKey, OAuth)
- `location`: Azure region
- `tags`: Resource tags

**Outputs:**
- `connectionId`: Full resource ID
- `connectionName`: Connection name
- `connectionTarget`: Target URL
