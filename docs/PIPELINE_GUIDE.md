# Pipeline Guide

This document explains how to use the parameterized CI/CD pipelines for deploying infrastructure and agents.

## Overview

We have two separate pipelines:

1. **Infrastructure Pipeline** - Deploys Azure resources (Connections, etc.)
2. **Agent Pipeline** - Deploys AI Agents to Azure AI Foundry

Both pipelines support **runtime parameters** for selective deployment.

---

## Infrastructure Pipeline

**File**: `pipelines/infrastructure-pipeline.yml`

### Parameters

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `deployModule` | Which infrastructure module to deploy | `all` | `all`, `foundry_connection` |

### How to Use

#### Option 1: Manual Run (Recommended)
1. Go to **Azure DevOps > Pipelines**
2. Select **Infrastructure Pipeline**
3. Click **Run pipeline**
4. Select parameters:
   - **Branch**: `main` (for nonprod) or `release` (for prod)
   - **Deploy Module**: Choose which module to deploy
5. Click **Run**

#### Option 2: Automatic Trigger
- Pushes to `main` branch that modify `infrastructure/` will auto-trigger
- Deploys **all** modules by default

### Module Descriptions

- **`all`**: Deploys all infrastructure modules defined in `infrastructure/main.bicep`
- **`foundry_connection`**: Deploys only the AI Foundry Connection module

### Adding New Modules

1. Create module in `infrastructure/modules/your_module/`
2. Add to `pipelines/infrastructure-pipeline.yml` parameter values:
   ```yaml
   values:
     - all
     - foundry_connection
     - your_module  # Add this
   ```
3. Update `scripts/deploy_infrastructure.py` to handle the new module

---

## Agent Pipeline

**File**: `pipelines/agent-pipeline.yml`

### Parameters

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `agentFile` | Which agent YAML file to deploy | `simple-agent.yaml` | `simple-agent.yaml` |

### How to Use

#### Option 1: Manual Run (Recommended)
1. Go to **Azure DevOps > Pipelines**
2. Select **Agent Pipeline**
3. Click **Run pipeline**
4. Select parameters:
   - **Branch**: `main` (for nonprod) or `release` (for prod)
   - **Agent File**: Choose which agent to deploy
5. Click **Run**

#### Option 2: Automatic Trigger
- Pushes to `main` branch that modify `agents/`, `tools/`, or `scripts/` will auto-trigger
- Deploys `simple-agent.yaml` by default

### Adding New Agents

1. Create agent YAML in `agents/your-agent.yaml`
2. Add to `pipelines/agent-pipeline.yml` parameter values:
   ```yaml
   values:
     - simple-agent.yaml
     - your-agent.yaml  # Add this
   ```

---

## Environment Configuration

Both pipelines determine the environment based on the **branch**:

| Branch | Environment | Variable File |
|--------|-------------|---------------|
| `main` | `nonprod` | `infrastructure/variables/nonprod.yaml` |
| `release` | `prod` | `infrastructure/variables/prod.yaml` |

---

## Variable Groups

Ensure these Variable Groups exist in Azure DevOps:

### `ai-agent-secrets-nonprod`
- `TODO_API_KEY` (secret)
- `AZURE_SERVICE_CONNECTION`

### `ai-agent-secrets-prod`
- `TODO_API_KEY` (secret)
- `AZURE_SERVICE_CONNECTION`

---

## Example Workflows

### Scenario 1: Deploy New Connection to Nonprod
1. Update `infrastructure/variables/nonprod.yaml` with new connection details
2. Run **Infrastructure Pipeline**
3. Select:
   - Branch: `main`
   - Module: `foundry_connection`
4. Click **Run**

### Scenario 2: Deploy New Agent to Prod
1. Create `agents/sales-agent.yaml`
2. Add `sales-agent.yaml` to agent pipeline parameters
3. Merge to `release` branch
4. Run **Agent Pipeline**
5. Select:
   - Branch: `release`
   - Agent: `sales-agent.yaml`
6. Click **Run**

### Scenario 3: Full Deployment (Infrastructure + Agent)
1. Run **Infrastructure Pipeline** with `deployModule: all`
2. Wait for completion
3. Run **Agent Pipeline** with desired agent
4. Verify in Azure AI Foundry portal

---

## Troubleshooting

### Pipeline doesn't show parameters
- Ensure you're clicking **Run pipeline** (not just viewing the YAML)
- Parameters only appear in the manual run dialog

### Module not found error
- Check that the module exists in `infrastructure/modules/`
- Verify `scripts/deploy_infrastructure.py` handles the module

### Agent deployment fails
- Ensure infrastructure pipeline ran successfully first
- Check that the connection referenced in agent YAML exists
- Verify Variable Groups are linked to the pipeline

---

## Best Practices

1. **Test in Nonprod First**: Always deploy to `main` branch (nonprod) before `release` (prod)
2. **Use Manual Runs**: For production, manually trigger pipelines with explicit parameter selection
3. **Version Control**: Keep agent YAML files in version control
4. **Document Changes**: Update this guide when adding new modules or agents
