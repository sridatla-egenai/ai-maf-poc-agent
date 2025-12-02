# Azure AI Foundry Agent Deployment

Deploy AI agents with OpenAPI tools to Azure AI Foundry using infrastructure as code.

## 🚀 Quick Start

```bash
# 1. Deploy the connection (weathertool)
python scripts/deploy_infrastructure.py foundry_connection --bicepparam infrastructure/nonprod.bicepparam

# 2. Deploy the agent
python -m scripts.deploy_agent \
  "https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent" \
  agents/weather-agent.yaml
```

## 📁 Repository Structure

```
ai-maf-poc-agent/
├── agents/
│   └── weather-agent.yaml           # Agent definition with tools
├── infrastructure/
│   ├── nonprod.bicepparam           # Single config file for nonprod
│   └── modules/
│       └── foundry_connection/
│           ├── connection.bicep     # Connection template
│           └── api.json             # OpenAPI spec
├── scripts/
│   ├── deploy_infrastructure.py     # Deploy connections
│   ├── deploy_agent.py             # Deploy agents
│   └── tool_factory.py             # Tool conversion logic
└── azure-pipelines.yml             # CI/CD pipeline
```

## ⚙️ Configuration

All configuration is in **one file**: `infrastructure/nonprod.bicepparam`

```bicep
// AI Foundry Project
param projectName = 'adusa-poc-agent'

// Weather Tool Connection
param connectionName = 'weathertool'
param targetUrl = 'https://wttr.in'
param openApiSpec = loadTextContent('./modules/foundry_connection/api.json')
param authType = 'CustomKeys'
param category = 'CustomKeys'

// Tags
param tags = {
  environment: 'nonprod'
  managedBy: 'devops'
  project: 'ai-agents'
}
```

## 🔧 Local Development

**Prerequisites:**
- Python 3.10+
- Azure CLI (`az login`)
- Access to Azure AI Foundry project

**Setup:**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Login to Azure
az login
```

## 🏗️ Deployment

### 1. Deploy Infrastructure (Connection)

```bash
python scripts/deploy_infrastructure.py foundry_connection \
  --bicepparam infrastructure/nonprod.bicepparam
```

This creates the `weathertool` connection in Azure AI Foundry that:
- Points to `https://wttr.in`
- Contains the OpenAPI specification
- Appears in the Foundry Studio UI

### 2. Deploy Agent

```bash
python -m scripts.deploy_agent \
  "https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent" \
  agents/weather-agent.yaml
```

This creates/updates the `weather-agent` that:
- Uses GPT-4o-mini model
- Has access to the `weathertool` connection
- Can fetch weather data for any location

## 🔄 CI/CD Pipeline

The pipeline (`azure-pipelines.yml`) automatically deploys agents when you push changes:

```yaml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - agents/**
      - scripts/**
```

**Pipeline runs:**
1. Sets up Python environment
2. Installs dependencies
3. Authenticates with Azure CLI
4. Deploys the agent to Foundry

**Azure DevOps Setup:**
1. Create service connection: `ado-service-connection`
2. Grant permissions: `Microsoft.CognitiveServices/accounts/*/agents/write`
3. Use self-hosted pool: `egen-agent-pool` (or change to Microsoft-hosted)

## 📝 Creating New Agents

1. **Create agent YAML** in `agents/`:
```yaml
version: 1.0.0
name: my-agent
model:
  id: "gpt-4o-mini"
instructions: "You are a helpful assistant..."
tools:
  - type: openapi
    id: weathertool
    options:
      specification: file://infrastructure/modules/foundry_connection/api.json
      connection_id: weathertool
```

2. **Deploy**:
```bash
python -m scripts.deploy_agent \
  "https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent" \
  agents/my-agent.yaml
```

## 🔌 Adding New Connections

1. **Update `nonprod.bicepparam`** with new connection details
2. **Add OpenAPI spec** to `infrastructure/modules/foundry_connection/`
3. **Deploy**:
```bash
python scripts/deploy_infrastructure.py foundry_connection \
  --bicepparam infrastructure/nonprod.bicepparam
```

## 🧪 Verification

**Check deployed connections:**
```bash
az rest --method get \
  --url "https://management.azure.com/subscriptions/{sub}/resourceGroups/ad-usa-poc/providers/Microsoft.CognitiveServices/accounts/adusa-poc-agent/projects/adusa-poc-agent/connections?api-version=2025-04-01-preview" \
  --query "value[].{name:name,category:properties.category,target:properties.target}" -o table
```

**View in Azure AI Foundry Studio:**
- Go to https://ai.azure.com
- Project: `adusa-poc-agent`
- Navigate to: Settings → Connections
- Navigate to: Agents section

## 🛠️ Troubleshooting

**Connection not showing in UI?**
- Verify `group: 'AzureAI'` is set in Bicep
- Check `metadata.type = 'openapi'` (lowercase)

**Agent deployment fails?**
- Ensure connection exists first
- Check `connection_id` matches deployed connection name
- Verify OpenAPI spec path is correct

**Import errors?**
- Use `python -m scripts.deploy_agent` (not `python scripts/deploy_agent.py`)
- Ensure `scripts/__init__.py` exists

## 📦 Dependencies

Key packages (see `requirements.txt`):
- `azure-ai-projects==2.0.0b1` - Azure AI Foundry SDK
- `azure-ai-agents==1.1.0` - Agent deployment
- `azure-identity==1.25.1` - Authentication
- `pyyaml==6.0.3` - YAML parsing

## 🔐 Security Notes

- Never commit API keys to git
- Use Azure Key Vault or pipeline secrets for sensitive values
- Connection credentials are stored securely in Azure
- Use managed identities when possible
