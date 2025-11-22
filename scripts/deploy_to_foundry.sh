#!/bin/bash
# Deploy an agent to Azure AI Foundry
# Usage: ./scripts/deploy_to_foundry.sh <agent-yaml-path> <project-name> <resource-group> <hub-name>
# Or set environment variables: AGENT_YAML_PATH, FOUNDRY_PROJECT_NAME, FOUNDRY_RESOURCE_GROUP, FOUNDRY_HUB_NAME

set -euo pipefail

# Set defaults from environment or arguments
AGENT_YAML_PATH="${1:=${AGENT_YAML_PATH:-agent.yaml}}"
FOUNDRY_PROJECT_NAME="${2:=${FOUNDRY_PROJECT_NAME:?'FOUNDRY_PROJECT_NAME not set'}}"
FOUNDRY_RESOURCE_GROUP="${3:=${FOUNDRY_RESOURCE_GROUP:?'FOUNDRY_RESOURCE_GROUP not set'}}"
FOUNDRY_HUB_NAME="${4:=${FOUNDRY_HUB_NAME:?'FOUNDRY_HUB_NAME not set'}}"

# Validate agent YAML exists
if [ ! -f "$AGENT_YAML_PATH" ]; then
    echo "ERROR: Agent YAML file not found at $AGENT_YAML_PATH"
    exit 1
fi

echo "=========================================="
echo "Deploying agent to Azure AI Foundry"
echo "=========================================="
echo "Agent YAML: $AGENT_YAML_PATH"
echo "Project: $FOUNDRY_PROJECT_NAME"
echo "Resource Group: $FOUNDRY_RESOURCE_GROUP"
echo "Hub: $FOUNDRY_HUB_NAME"
echo "=========================================="

# Extract agent name from YAML
AGENT_NAME=$(grep -A 1 '^name:' "$AGENT_YAML_PATH" | tail -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
echo "Agent name from YAML: $AGENT_NAME"

# Check if user is logged in
echo "Checking Azure login..."
if ! az account show > /dev/null 2>&1; then
    echo "Not logged into Azure. Running 'az login'..."
    az login
fi

# Install or update the Azure AI CLI extension
echo "Installing/updating Azure AI CLI extension..."
az extension add -n ai --upgrade -y 2>/dev/null || az extension update -n ai

# Create or update agent in Foundry
echo ""
echo "Publishing agent to Azure AI Foundry..."
az ai agent create-or-update \
    --resource-group "$FOUNDRY_RESOURCE_GROUP" \
    --hub-name "$FOUNDRY_HUB_NAME" \
    --definition "$AGENT_YAML_PATH" \
    --project "$FOUNDRY_PROJECT_NAME" \
    --verbose

echo ""
echo "=========================================="
echo "Agent deployed successfully!"
echo "=========================================="
echo ""
echo "To verify the agent:"
echo "  az ai agent show --resource-group $FOUNDRY_RESOURCE_GROUP --hub-name $FOUNDRY_HUB_NAME --project $FOUNDRY_PROJECT_NAME"
echo ""
