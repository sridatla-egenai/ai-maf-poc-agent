# Azure AI Foundry Agent POC

This repository contains the code and infrastructure for deploying an AI Agent to Azure AI Foundry.

## Repository Structure

```
ai-maf-poc-agent/
├── agents/                    # Agent Definitions (YAML)
│   └── simple-agent.yaml
│
├── infrastructure/            # Infrastructure as Code (Bicep)
│   ├── main.bicep
│   ├── modules/
│   └── variables/             # Environment configuration
│
├── pipelines/                 # Azure DevOps Pipelines
│   ├── infrastructure-pipeline.yml
│   └── agent-pipeline.yml
│
├── tools/                     # Tool Logic & Registry
│   ├── registry.py
│   └── openapi/
│
├── connections/               # Connection Definitions
│   └── todo-api.yaml
│
└── scripts/                   # Deployment Scripts
```

## Pipelines

We have separated the CI/CD process into two distinct pipelines with **runtime parameters** for selective deployment:

### 1. Infrastructure Pipeline (`pipelines/infrastructure-pipeline.yml`)
- **Triggers**: Changes to `infrastructure/` folder.
- **Action**: Deploys Bicep templates to provision Azure resources.
- **Parameter**: `deployModule` - Select which module to deploy (`all`, `foundry_connection`, etc.)

### 2. Agent Pipeline (`pipelines/agent-pipeline.yml`)
- **Triggers**: Changes to `agents/`, `tools/`, or `scripts/`.
- **Action**: Deploys the AI Agent to Azure AI Foundry.
- **Parameter**: `agentFile` - Select which agent YAML to deploy (`simple-agent.yaml`, etc.)

### Using Runtime Parameters

When you manually run a pipeline in Azure DevOps:
1. Click **Run pipeline**
2. Select the **branch** (determines environment: `main` = nonprod, `release` = prod)
3. Choose **parameters** (which module/agent to deploy)
4. Click **Run**

📖 **See [Pipeline Guide](docs/PIPELINE_GUIDE.md) for detailed usage instructions.**

## Getting Started

1. **Setup Variable Groups** in Azure DevOps:
   - `ai-agent-secrets-nonprod`
   - `ai-agent-secrets-prod`

2. **Create Pipelines**:
   - Point "Infrastructure Pipeline" to `pipelines/infrastructure-pipeline.yml`
   - Point "Agent Pipeline" to `pipelines/agent-pipeline.yml`

3. **Deploy**:
   - **Manual**: Run pipelines with desired parameters
   - **Automatic**: Push to `main` to deploy to nonprod (uses default parameters)
