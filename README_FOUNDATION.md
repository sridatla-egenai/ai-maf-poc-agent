# Azure DevOps Pipeline → Azure AI Foundry Agent Deployment

This repository contains an Azure DevOps pipeline that publishes your agent definition directly to Azure AI Foundry. No Docker build or container registry required — just your `agent.yaml` and Azure credentials.

## What This Does

The pipeline (`azure-pipelines.yml`):
- Validates your `agent.yaml` file
- Authenticates to your Azure subscription
- Publishes/updates your agent to Azure AI Foundry using the **Python SDK** (`azure-ai-projects`)

**Note:** The pipeline uses the Python SDK, not `az ai agent` CLI (which doesn't exist as a standard extension).

## Prerequisites

1. **Azure Subscription** with Azure AI Foundry resources
   - A Foundry Hub (workspace)
   - A Foundry Project within that Hub

2. **Azure DevOps Project** where this repo is cloned

3. **Azure Service Connection** in Azure DevOps
   - Create an "Azure Resource Manager" service connection with credentials that have contributor or higher access to your Foundry resource group
   - Note the connection name (e.g., `Azure-Subscription`)

4. **Azure CLI** installed locally (optional, for manual testing)
   - `az extension add -n ai` (AI CLI extension)

## Setup Steps

### 1. Create Azure DevOps Service Connection

In your Azure DevOps project:

1. Go to **Project Settings** → **Service connections**
2. Click **New service connection** → **Azure Resource Manager** → **Service principal (automatic)**
3. Select your subscription and resource group
4. Name it (e.g., `Azure-Subscription`) — you'll reference this name in the pipeline
5. Click **Save**

### 2. Configure Pipeline Variables

In Azure DevOps, go to **Pipelines** → select your pipeline → **Edit** → **Variables**

Add or update these variables:

| Variable | Type | Value | Notes |
|----------|------|-------|-------|
| `AZURE_SERVICE_CONNECTION` | String | Name of service connection from step 1 | e.g., `Azure-Subscription` |
| `FOUNDRY_PROJECT_NAME` | String | Your Foundry project name | e.g., `my-ai-project` |
| `FOUNDRY_RESOURCE_GROUP` | String | Azure resource group name | e.g., `my-foundry-rg` |
| `FOUNDRY_HUB_NAME` | String | Your Foundry Hub (workspace) name | e.g., `my-foundry-hub` |
| `AGENT_YAML_PATH` | String | Path to agent definition | Default: `agent.yaml` |

**Example:**
```
AZURE_SERVICE_CONNECTION = Azure-Subscription
FOUNDRY_PROJECT_NAME = my-ai-project
FOUNDRY_RESOURCE_GROUP = rg-foundry-eastus
FOUNDRY_HUB_NAME = my-hub
AGENT_YAML_PATH = agent.yaml
```

### 3. Commit and Push

Update the pipeline variable placeholders in `azure-pipelines.yml` with your actual values, then:

```bash
git add azure-pipelines.yml
git commit -m "Configure Foundry deployment variables"
git push origin main
```

The pipeline will automatically trigger on push to `main` and deploy your agent.

## Local Testing / Manual Deployment

You can also deploy your agent locally using the helper script:

```bash
# Make the script executable
chmod +x scripts/deploy_to_foundry.sh

# Log in to Azure (if not already logged in)
az login

# Deploy the agent
./scripts/deploy_to_foundry.sh agent.yaml my-ai-project my-foundry-rg my-hub
```

Or use the Azure CLI directly:

```bash
# Install/update AI CLI extension
az extension add -n ai --upgrade -y

# Create or update agent
az ai agent create-or-update \
  --resource-group my-foundry-rg \
  --hub-name my-hub \
  --definition agent.yaml \
  --project my-ai-project
```

## Agent YAML Reference

Your `agent.yaml` must follow the Foundry agent schema. Key sections:

- **`name`**: Display name of your agent
- **`description`**: Brief description of what it does
- **`model`**: The model to use (e.g., GPT-4, Claude, local model ID from your Foundry hub)
- **`instructions`**: System prompt / agent behavior instructions
- **`tools`**: Optional list of tools (OpenAPI specs, custom functions, etc.)
- **`metadata`**: Tags and author info

Example structure:
```yaml
version: 1.0.0
name: My Weather Agent
description: Provides weather information
model:
  id: gpt-4  # or your Foundry model ID
instructions: >-
  You are a helpful weather assistant...
tools:
  - type: openapi
    id: GetWeather
    options:
      specification: https://api.weatherapi.com/v1/current.json
```

## Verify Deployment

After the pipeline runs (or after manual deployment), check that your agent was created:

```bash
az ai agent show \
  --resource-group my-foundry-rg \
  --hub-name my-hub \
  --project my-ai-project
```

You should see your agent listed in the Foundry UI under the project.

## Troubleshooting

### Pipeline fails with "AZURE_SERVICE_CONNECTION not found"
- Ensure the service connection name in variables matches exactly what you created in Azure DevOps
- Check that the service connection has access to your Foundry resource group

### "Resource not found" or "Hub not found" errors
- Verify the resource group, hub name, and project name are correct
- Ensure your service connection credentials have reader/contributor access to those resources
- Check spelling and case sensitivity

### "Azure AI CLI extension not found"
- The pipeline auto-installs it, but if it fails:
  ```bash
  az extension add -n ai --upgrade -y
  ```

### Agent YAML validation errors
- Validate your YAML syntax (use a YAML linter)
- Ensure the model ID exists in your Foundry hub
- Check that all required fields are present (name, model, instructions)

## Next Steps

1. Customize `agent.yaml` with your agent logic (instructions, tools, model)
2. Test the agent in the Foundry UI
3. Configure triggers (optional): modify the pipeline trigger to deploy on PR, schedule, or manual
4. Add more stages (optional): add testing, approval gates, or multi-environment deployments

## Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Agent Framework](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/agents)
- [Azure DevOps Pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/)

