# Azure AI Foundry Agent Deployment

Deploy AI agents with OpenAPI tools to Azure AI Foundry using infrastructure as code.

## 🏗️ Architecture Overview

This repository follows a **separation of concerns** architecture:

- **Infrastructure Layer** (`infrastructure/`) - Connections to external APIs managed as code
- **Application Layer** (`agents/`) - Agent definitions that reference connections
- **Deployment Layer** (`scripts/`) - Automation for deploying both layers

**Key Principle**: Deploy connections FIRST, then agents can reference them by ID.

## 🚀 Quick Start

```bash
# 1. Deploy the connection (weathertool)
python scripts/deploy_infrastructure.py foundry_connection \
  --bicepparam infrastructure/parameters/connections/connections.bicepparam

# 2. Deploy the agent
python -m scripts.deploy_agent \
  "https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent" \
  agents/weather-agent.yaml
```

## 📁 Repository Structure

```
ai-maf-poc-agent/
│
├── 🏗️  infrastructure/                 Infrastructure as Code (IaC)
│   │
│   ├── modules/                        Bicep Templates (HOW to deploy)
│   │   ├── connections/
│   │   │   ├── connection.bicep        → Template for creating connections
│   │   │   ├── api.json                → OpenAPI spec for weathertool
│   │   │   └── connection.json         → Connection metadata
│   │   └── guardrails/
│   │       └── content_filter.bicep    → Content filtering rules
│   │
│   └── parameters/                     Configuration (WHAT to deploy)
│       ├── connections/
│       │   ├── connections.bicepparam  → Connection settings (nonprod)
│       │   └── api.json                → OpenAPI spec reference
│       └── guardrails/
│           └── guardrails.bicepparam   → Guardrails settings (nonprod)
│
├── 🤖 agents/                          Agent Definitions
│   └── weather-agent.yaml              → Agent config (model, instructions, tools)
│
├── ⚙️  scripts/                         Deployment Automation
│   ├── deploy_infrastructure.py        → Deploy connections via Bicep
│   ├── deploy_agent.py                 → Deploy agents via SDK
│   ├── deploy_guardrails.py            → Deploy guardrails
│   ├── tool_factory.py                 → Convert YAML tools → SDK objects
│   └── local-deploy.sh                 → Interactive deployment menu
│
├── 🔄 pipelines/                        CI/CD Pipelines
│   ├── infrastructure-pipeline.yml     → Auto-deploy connections
│   ├── agent-pipeline.yml              → Auto-deploy agents
│   └── guardrails-pipeline.yml         → Auto-deploy guardrails
│
├── 📚 docs/                             Documentation
│   ├── DEPLOYMENT_FLOW.md              → Architecture diagrams & flow
│   ├── GUARDRAILS.md                   → Content filtering guide
│   ├── ORGANIZATION.md                 → Repository structure
│   └── PIPELINE_SETUP.md               → CI/CD setup guide
│
└── 📋 Configuration Files
    ├── requirements.txt                → Python dependencies
    ├── azure-pipelines.yml             → Unified deployment pipeline
    └── README.md                       → This file
```

## 🎯 Design Principles

### 1. Separation of Infrastructure and Application

```
infrastructure/     → Platform team manages connections (WHAT APIs are available)
agents/            → App team builds agents (WHAT agents do with APIs)
```

**Benefits:**
- ✅ One connection → Multiple agents can reuse it
- ✅ Update connection → Zero agent code changes
- ✅ Security centralized → App devs never see credentials
- ✅ Environment switching → Same agent, different connection config

### 2. Configuration Separate from Code

```
modules/           → Templates (HOW to deploy) - reusable across environments
parameters/        → Settings (WHAT to deploy) - per environment (dev/prod)
```

### 3. Critical Deployment Order

```
Phase 1: Deploy Connection  (infrastructure layer)
Phase 2: Deploy Agent       (application layer - references connection)
```

⚠️ **Important**: If agent is deployed before connection exists, deployment will FAIL with "Connection not found" error.

## ⚙️ Configuration

All configuration lives in: `infrastructure/parameters/`

### Connection Configuration

**File**: `infrastructure/parameters/connections/connections.bicepparam`

```bicep
using '../../modules/connections/connection.bicep'

param projectName = 'adusa-poc-agent'
param connectionName = 'weathertool'
param targetUrl = 'https://wttr.in'
param openApiSpec = loadTextContent('./api.json')
param authType = 'CustomKeys'
param category = 'CustomKeys'
param apiKey = 'test'  // In production, use Key Vault reference
```

**Key Properties:**
- `projectName` - Azure AI Foundry project name
- `connectionName` - Connection identifier (referenced by agents)
- `targetUrl` - API endpoint
- `openApiSpec` - Path to OpenAPI 3.1 specification
- `authType` - Authentication method (CustomKeys, AAD, ManagedIdentity, etc.)

### Agent Configuration

**File**: `agents/weather-agent.yaml`

```yaml
version: 1.0.0
name: weather-agent
model:
  id: "gpt-4o-mini"
instructions: |
  You are a weather assistant that helps users get weather information.
tools:
  - type: openapi
    id: weathertool
    connection_id: weathertool  # References the connection deployed via Bicep
```

**Key Properties:**
- `name` - Agent identifier
- `model.id` - Azure OpenAI model deployment name
- `instructions` - System prompt for agent behavior
- `tools.connection_id` - Must match deployed connection name

### Guardrails Configuration

**File**: `infrastructure/parameters/guardrails/guardrails.bicepparam`

```bicep
param contentFilterConfig = {
  hate: { enabled: true, severity: 'medium', blocking: true }
  sexual: { enabled: true, severity: 'medium', blocking: true }
  violence: { enabled: true, severity: 'medium', blocking: true }
  selfHarm: { enabled: true, severity: 'high', blocking: true }
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

## 🏗️ Deployment Guide

### Prerequisites
- Azure CLI installed and authenticated (`az login`)
- Python 3.10+ with virtual environment activated
- Access to Azure AI Foundry project
- Resource Group: `ad-usa-poc` (or set via `RESOURCE_GROUP` env var)

### Deployment Sequence (Critical!)

**Phase 1: Deploy Infrastructure (Connection)**

Connections must be deployed FIRST before agents can reference them.

```bash
python scripts/deploy_infrastructure.py foundry_connection \
  --bicepparam infrastructure/parameters/connections/connections.bicepparam
```

This deploys:
- Connection resource named `weathertool`
- Target API: `https://wttr.in`
- OpenAPI specification embedded
- Authentication configured

**Phase 2: Deploy Agent**

After connection exists, deploy the agent that uses it.

```bash
python -m scripts.deploy_agent \
  "https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent" \
  agents/weather-agent.yaml
```

This creates/updates `weather-agent` with:
- Model: `gpt-4o-mini`
- Tools: `weathertool` (references connection by ID)
- Instructions: Weather assistant prompts

**Phase 3 (Optional): Deploy Guardrails**

```bash
python scripts/deploy_guardrails.py nonprod
```

This applies content filtering rules for responsible AI.

### Interactive Deployment

Use the interactive menu for guided deployment:

```bash
./scripts/local-deploy.sh
```

Menu options:
1. Deploy connection
2. Deploy agent
3. Deploy guardrails
4. Exit

## 🔄 CI/CD Pipelines

The repository includes multiple pipeline options for automated deployment:

### Option 1: Unified Pipeline (Recommended for First Deploy)

**File**: `azure-pipelines.yml`

Deploys both infrastructure and agents in sequence (ensures correct order).

```yaml
stages:
  - DeployInfrastructure  # Phase 1: Deploy connection
  - DeployAgent           # Phase 2: Deploy agent (depends on Phase 1)
```

**Trigger**: Manual or changes to both `infrastructure/**` and `agents/**`

### Option 2: Separate Pipelines (For Independent Updates)

**Infrastructure Pipeline**: `pipelines/infrastructure-pipeline.yml`
- **Trigger**: Changes to `infrastructure/**`
- **Deploys**: Connections via Bicep
- **Command**: `python scripts/deploy_infrastructure.py foundry_connection --bicepparam ...`

**Agent Pipeline**: `pipelines/agent-pipeline.yml`
- **Trigger**: Changes to `agents/**` or `scripts/**`
- **Deploys**: Agents via SDK
- **Command**: `python -m scripts.deploy_agent ...`
- **Prerequisite**: ⚠️ Connection must already exist!

**Guardrails Pipeline**: `pipelines/guardrails-pipeline.yml`
- **Trigger**: Changes to `infrastructure/parameters/guardrails/**`
- **Deploys**: Content filtering rules

### Azure DevOps Setup

1. **Create service connection**: `ado-service-connection`
2. **Grant IAM permissions**:
   - `Microsoft.CognitiveServices/accounts/*/connections/write`
   - `Microsoft.CognitiveServices/accounts/*/agents/write`
3. **Configure agent pool**: `egen-agent-pool` (or use Microsoft-hosted agents)
4. **Set variables**:
   - `RESOURCE_GROUP`: `ad-usa-poc`
   - `FOUNDRY_ENDPOINT`: Your project endpoint
   - `AGENT_YAML_PATH`: `agents/weather-agent.yaml`

See `docs/PIPELINE_SETUP.md` for detailed setup instructions.

## 📝 Creating New Agents

### Step 1: Create Agent YAML

Create a new file in `agents/` directory (e.g., `agents/my-agent.yaml`):

```yaml
version: 1.0.0
name: my-agent
model:
  id: "gpt-4o-mini"
instructions: |
  You are a helpful assistant that...
  Your goal is to...
tools:
  - type: openapi
    id: weathertool
    connection_id: weathertool  # References existing connection
```

**Agent YAML Structure:**
- `name` - Unique identifier for the agent
- `model.id` - Azure OpenAI model deployment name
- `instructions` - System prompt defining agent behavior
- `tools[].connection_id` - Must match a deployed connection name

### Step 2: Deploy the Agent

```bash
python -m scripts.deploy_agent \
  "https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent" \
  agents/my-agent.yaml
```

### Step 3: Verify

Check Azure AI Foundry Studio → Agents section to see your deployed agent.

## 🔌 Adding New Connections

### Step 1: Prepare OpenAPI Specification

Add your API's OpenAPI 3.1 spec to `infrastructure/parameters/connections/`:

```
infrastructure/parameters/connections/
├── api.json              # Existing weathertool spec
└── my-api-spec.json      # Your new API spec
```

### Step 2: Update Configuration

Edit `infrastructure/parameters/connections/connections.bicepparam`:

```bicep
using '../../modules/connections/connection.bicep'

param projectName = 'adusa-poc-agent'
param connectionName = 'my-new-connection'        // Update
param targetUrl = 'https://api.example.com'       // Update
param openApiSpec = loadTextContent('./my-api-spec.json')  // Update
param authType = 'ApiKey'                         // Update as needed
param category = 'ApiKey'                         // Update as needed
```

**Or** create a new `.bicepparam` file for multiple connections:
- `connections.bicepparam` → weathertool
- `database-connection.bicepparam` → database API
- `payment-connection.bicepparam` → payment gateway

### Step 3: Deploy Connection

```bash
python scripts/deploy_infrastructure.py foundry_connection \
  --bicepparam infrastructure/parameters/connections/connections.bicepparam
```

### Step 4: Reference in Agent

Update your agent YAML to use the new connection:

```yaml
tools:
  - type: openapi
    id: my-new-connection
    connection_id: my-new-connection
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

### Connection Issues

**❌ Connection not showing in Azure AI Foundry UI?**

Check these Bicep template properties in `infrastructure/modules/connections/connection.bicep`:
```bicep
properties: {
  group: 'AzureAI'          // Required for UI visibility
  metadata: {
    type: 'openapi'         // Must be lowercase
  }
}
```

**❌ Deployment fails with "authType validation error"?**

Ensure `authType` parameter is one of the allowed values:
- `AAD`, `AccessKey`, `AccountKey`, `ApiKey`, `CustomKeys`
- `ManagedIdentity`, `None`, `OAuth2`, `PAT`, `SAS`
- `ServicePrincipal`, `UsernamePassword`

**❌ Credentials structure error?**

For `CustomKeys` auth, use:
```bicep
credentials: {
  key: apiKey
}
```

### Agent Deployment Issues

**❌ "Connection 'weathertool' not found"**

This means the agent is trying to reference a connection that doesn't exist.

**Solution**: Deploy connection FIRST:
```bash
python scripts/deploy_infrastructure.py foundry_connection --bicepparam ...
```

**❌ "ModuleNotFoundError: No module named 'tool_factory'"**

Use module-style execution:
```bash
python -m scripts.deploy_agent ...  # ✅ Correct
python scripts/deploy_agent.py ... # ❌ Wrong
```

**❌ Agent deployment succeeds but doesn't work**

Check:
1. `connection_id` in agent YAML matches deployed connection name exactly
2. OpenAPI spec is valid OpenAPI 3.1 format
3. Target API is accessible from Azure
4. Authentication credentials are correct

### Pipeline Issues

**❌ Pipeline fails with authentication error**

Verify:
1. Service connection `ado-service-connection` exists
2. Service principal has required IAM roles
3. `AzureCLI@2` task is using correct service connection

**❌ Agent pipeline runs before connection deployed**

Use the **unified pipeline** (`azure-pipelines.yml`) which ensures correct order with stage dependencies.

### General Issues

**❌ "Template not found" error**

Verify file paths:
- Template: `infrastructure/modules/connections/connection.bicep`
- Parameters: `infrastructure/parameters/connections/connections.bicepparam`

**❌ Python import errors**

Ensure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 📦 Dependencies

Key packages (see `requirements.txt`):
- `azure-ai-projects==2.0.0b1` - Azure AI Foundry SDK
- `azure-ai-agents==1.1.0` - Agent deployment
- `azure-identity==1.25.1` - Authentication
- `pyyaml==6.0.3` - YAML parsing

## 🛡️ Guardrails (Content Filtering)

Deploy responsible AI guardrails to filter harmful content:

```bash
python scripts/deploy_guardrails.py nonprod
```

**Features**:
- Content filtering for hate, sexual, violence, and self-harm
- Configurable severity levels (low, medium, high)
- Blocking or monitoring modes
- Per-environment configuration
- Automatic deployment via CI/CD

**Configuration**: `infrastructure/parameters/guardrails/guardrails.bicepparam`

**Documentation**: See `docs/GUARDRAILS.md` for full details

## 🔐 Security Best Practices

### Credential Management

✅ **DO:**
- Use Azure Key Vault references in production
- Store secrets in Azure DevOps pipeline variables (marked as secret)
- Use Managed Identity authentication when possible
- Rotate credentials regularly

❌ **DON'T:**
- Commit API keys, tokens, or passwords to git
- Use test credentials in production
- Hardcode sensitive values in YAML/Bicep files

### Example: Key Vault Reference

```bicep
param apiKey = {
  '@keyvault': {
    vaultId: '/subscriptions/.../Microsoft.KeyVault/vaults/my-vault'
    secretName: 'weather-api-key'
  }
}
```

### Authentication Methods (Recommended Priority)

1. **Managed Identity** - Best for Azure-to-Azure communication
2. **Service Principal** - Good for automated deployments
3. **API Key** - When required by third-party APIs (use Key Vault)
4. **CustomKeys** - For testing only (not for production)

### Network Security

- Restrict API access with VNet integration
- Use private endpoints for sensitive connections
- Enable Azure AI Foundry managed network rules

## 📚 Additional Documentation

- **[DEPLOYMENT_FLOW.md](docs/DEPLOYMENT_FLOW.md)** - Architecture diagrams and deployment sequence
- **[ORGANIZATION.md](docs/ORGANIZATION.md)** - Repository structure and design decisions
- **[PIPELINE_SETUP.md](docs/PIPELINE_SETUP.md)** - Detailed CI/CD setup guide
- **[GUARDRAILS.md](docs/GUARDRAILS.md)** - Content filtering implementation
- **[VERIFICATION.md](docs/VERIFICATION.md)** - Testing and validation procedures

## 🤝 Contributing

When adding new features:

1. **Connections** → Update `infrastructure/parameters/connections/`
2. **Agents** → Add YAML to `agents/`
3. **Templates** → Modify `infrastructure/modules/`
4. **Scripts** → Update Python scripts in `scripts/`
5. **Documentation** → Keep docs in sync with changes

## 📄 License

[Add your license here]

## 🆘 Support

For issues or questions:
- Check troubleshooting section above
- Review documentation in `docs/` folder
- Open an issue in the repository
