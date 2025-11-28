# Azure DevOps Pipeline → Azure AI Foundry Agent Deployment

This guide explains how to deploy your agent to Azure AI Foundry using the Azure DevOps pipeline.

## Quick Start

The pipeline automatically deploys your agent whenever you push to the `main` branch.

### Prerequisites

1. **Azure DevOps Project** with this repository
2. **Azure Subscription** with Azure AI Foundry resources
3. **Service Connection** in Azure DevOps (for authentication)
4. **Local testing** (optional but recommended)

## Setup

### Step 1: Get Your Foundry Endpoint

You need your Foundry project endpoint in this format:
```
https://<account>.services.ai.azure.com/api/projects/<project-name>
```

Example: `https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent`

### Step 2: Create Azure DevOps Service Connection

1. Go to your Azure DevOps project
2. Navigate to **Project Settings** → **Service connections**
3. Click **New service connection** → **Azure Resource Manager**
4. Choose **Service principal (automatic)**
5. Select your subscription and resource group
6. Name it `Azure-Subscription` (or note the name you choose)
7. Click **Save**

### Step 3: Update Pipeline Variables

The pipeline has these variables in `azure-pipelines.yml`:

```yaml
variables:
  - name: AGENT_YAML_PATH
    value: 'agent.yaml'
  - name: FOUNDRY_ENDPOINT
    value: 'https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent'
  - name: AZURE_SERVICE_CONNECTION
    value: 'Azure-Subscription'
```

**Update the values:**

- **`FOUNDRY_ENDPOINT`**: Replace with your actual endpoint
- **`AGENT_YAML_PATH`**: Keep as `agent.yaml` (or change if your config file is elsewhere)
- **`AZURE_SERVICE_CONNECTION`**: Must match the service connection name from Step 2

### Step 4: Commit and Push

```bash
git add azure-pipelines.yml
git commit -m "Configure Foundry endpoint for pipeline"
git push origin main
```

The pipeline will trigger automatically!

## Local Testing (Recommended)

Test the deployment locally before pushing to the pipeline:

```bash
# Install dependencies
pip install -r requirements.txt

# Authenticate to Azure
az login

# Deploy
python scripts/deploy_agent.py https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent agent.yaml
```

## Pipeline Steps

The `azure-pipelines.yml` executes these steps:

1. **Checkout** - Pulls your repository code
2. **Python Setup** - Installs Python 3.10
3. **Install Dependencies** - Runs `pip install -r requirements.txt`
4. **Deploy Agent** - Runs `python scripts/deploy_agent.py` with the endpoint and YAML file

## Customizing Your Agent

Edit `agent.yaml` to customize your agent:

```yaml
version: 1.0.0
name: weather-agent
description: Description of the agent

metadata:
  author: "platform_team"
  tag: "env:nonprd"

model:
  id: gpt-5-mini

instructions: |
  You are a helpful weather assistant.
  Provide accurate weather information.

tools: []
```

## Troubleshooting

### Pipeline fails with authentication error

**Problem**: `Failed to authenticate`

**Solution**:
- Verify the service connection has access to your Foundry resource group
- Check that the service connection credentials are valid
- Ensure the resource group name is correct

### Agent deployment fails with "create_agent not found"

**Problem**: `'AgentsOperations' object has no attribute 'create_agent'`

**Solution**: This is already fixed in the current `deploy_agent.py`. Make sure you're using version 2.0.0b2 or later of `azure-ai-projects`.

### "Agent YAML not found" error

**Problem**: Script can't find `agent.yaml`

**Solution**:
- Verify the file exists in your repository root
- Check that `AGENT_YAML_PATH` in the pipeline matches the actual file path
- Ensure the file is committed to git (not in `.gitignore`)

### Connection timeout or network errors

**Problem**: Pipeline can't reach the Foundry endpoint

**Solution**:
- Verify the `FOUNDRY_ENDPOINT` URL is correct
- Test connectivity: `curl -I <your-endpoint>`
- Check that your Azure subscription hasn't expired

## Debugging

To see more details during pipeline execution:

1. Go to **Pipelines** → select your pipeline run
2. Click **Logs** to view full output
3. Look for the "Deploy agent to Foundry" step for deployment details

## Pipeline File Location

- **Pipeline Definition**: `azure-pipelines.yml`
- **Deployment Script**: `scripts/deploy_agent.py`
- **Dependencies**: `requirements.txt`
- **Agent Config**: `agent.yaml`

## Environment Variables

The pipeline uses:

- `FOUNDRY_ENDPOINT` - Your Foundry project endpoint URL
- `AGENT_YAML_PATH` - Path to agent configuration file
- `AZURE_SUBSCRIPTION_ID` - Azure subscription token (provided by pipeline)

## Next Steps

1. ✅ Set up the service connection
2. ✅ Update `azure-pipelines.yml` with your endpoint
3. ✅ Test locally with the deployment script
4. ✅ Commit and push to trigger the pipeline
5. ✅ Monitor the pipeline run in Azure DevOps
6. ✅ Verify your agent appears in Foundry UI

## Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Agent Framework](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/agents)
- [Azure DevOps Pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/)
