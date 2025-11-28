#!/usr/bin/env python3
"""
Deploy an agent to Azure AI Foundry using the Python SDK.

Usage:
  python scripts/deploy_agent.py <endpoint> <agent_yaml_path>

Environment Variables (alternative to arguments):
  - FOUNDRY_ENDPOINT: Azure AI Foundry project endpoint
    Format: https://<account>.services.ai.azure.com/api/projects/<project-name>
  - AGENT_YAML_PATH (default: agent.yaml)

Example:
  python scripts/deploy_agent.py "https://myaccount.services.ai.azure.com/api/projects/my-project" agent.yaml
  
  FOUNDRY_ENDPOINT=https://myaccount.services.ai.azure.com/api/projects/my-project \
  python scripts/deploy_agent.py
"""

import sys
import os
import yaml
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
#from azure.ai.projects.models import ImageBasedHostedAgentDefinition, ProtocolVersionRecord, AgentProtocol
from azure.ai.projects.models import PromptAgentDefinition




def load_agent_yaml(yaml_path: str) -> dict:
    """Load and parse agent YAML file."""
    if not Path(yaml_path).exists():
        raise FileNotFoundError(f"Agent YAML not found at {yaml_path}")
    
    with open(yaml_path, 'r') as f:
        agent_def = yaml.safe_load(f)
    
    if not agent_def:
        raise ValueError(f"Agent YAML is empty: {yaml_path}")
    
    return agent_def


def validate_agent_definition(agent_def: dict) -> None:
    """Validate required fields in agent definition."""
    required_fields = ['name', 'model']
    for field in required_fields:
        if field not in agent_def:
            raise ValueError(f"Missing required field in agent.yaml: {field}")
    
    if isinstance(agent_def.get('model'), dict):
        if 'id' not in agent_def['model']:
            raise ValueError("Missing model.id in agent.yaml")
    else:
        raise ValueError("model must be a dict with 'id' field in agent.yaml")


def convert_tools_from_yaml(tools_yaml: list) -> list:
    """
    Convert tool definitions from YAML format to SDK-compatible dicts.
    
    Args:
        tools_yaml: List of tool definitions from agent.yaml
    
    Returns:
        List of tool dictionaries compatible with SDK
    """
    if not tools_yaml:
        return []
    
    sdk_tools = []
    for tool_yaml in tools_yaml:
        tool_type = tool_yaml.get('type')
        
        if tool_type == 'openapi':
            # Convert OpenAPI tool from YAML to SDK-compatible dict
            tool_id = tool_yaml.get('id', 'unknown_tool')
            description = tool_yaml.get('description', '')
            options = tool_yaml.get('options', {})
            
            # Get the OpenAPI spec URL
            spec = options.get('specification')
            if not spec:
                raise ValueError(f"Missing 'specification' in OpenAPI tool: {tool_id}")
            
            # Create tool dict in SDK format
            tool_dict = {
                'type': 'openapi',
                'openapi': {
                    'name': tool_id,
                    'description': description,
                    'spec': {
                        'url': spec
                    },
                    'auth': {
                        'type': 'anonymous'
                    }
                }
            }
            sdk_tools.append(tool_dict)
        else:
            print(f"⚠ Unsupported tool type: {tool_type}, skipping")
    
    return sdk_tools


def deploy_agent(
    endpoint: str,
    agent_yaml_path: str
) -> dict:
    """
    Deploy agent to Azure AI Foundry.
    
    Args:
        endpoint: Foundry project endpoint URL
                 Format: https://<account>.services.ai.azure.com/api/projects/<project-name>
        agent_yaml_path: Path to agent.yaml definition file
    
    Returns:
        dict: Deployed agent info (id, name, etc.)
    
    Raises:
        Exception: If deployment fails
    """
    # Load and validate agent definition
    print(f"Loading agent from: {agent_yaml_path}")
    agent_def = load_agent_yaml(agent_yaml_path)
    validate_agent_definition(agent_def)
    
    agent_name = agent_def.get('name', 'Agent')
    print(f"Agent name: {agent_name}")
    print(f"Model: {agent_def['model']['id']}")
    print(f"\nConnecting to Azure AI Foundry:")
    print(f"  Endpoint: {endpoint}")
    
    # Initialize Azure AI Projects client
    try:
        credential = DefaultAzureCredential()
        client = AIProjectClient(
            endpoint=endpoint,
            credential=credential
        )
        print("✓ Connected to Azure AI Foundry\n")
    except Exception as e:
        print(f"✗ Failed to connect to Foundry: {e}")
        raise
    
    # Prepare agent creation parameters
    try:
        model_id = agent_def['model']['id']
        
        agent_create_params = {
            'agent_name': agent_name,
            'definition': PromptAgentDefinition(
                    model=model_id,
                    instructions=agent_def.get('instructions', 'You are a helpful assistant that answers general questions'),
            ),
        }
        
        # Convert and add tools if present
        if 'tools' in agent_def and agent_def['tools']:
            sdk_tools = convert_tools_from_yaml(agent_def['tools'])
            if sdk_tools:
                print(f"Tools: {len(sdk_tools)} tool(s) configured")
                agent_create_params['tools'] = sdk_tools
        
        if 'metadata' in agent_def:
            agent_create_params['metadata'] = agent_def['metadata']
            print(f"Metadata: {agent_def['metadata']}")
        
        # Create or update agent
        print("Deploying agent to Foundry...")
        agent = client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model_id,
                instructions=agent_def.get('instructions', 'You are a helpful assistant that answers general questions'),
            ),
        )

        
#     agent_name=os.environ["AZURE_AI_FOUNDRY_AGENT_NAME"],
#     definition=PromptAgentDefinition(
#         model=os.environ["AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT_NAME"],
#         instructions="You are a helpful assistant that answers general questions",
#     ),
# )
        
        result = {
            'id': agent.id,
            'name': agent.name,
            'model': model_id,
            'endpoint': endpoint,
        }
        
        print(f"\n✓ Agent deployed successfully!")
        print(f"  Agent ID: {agent.id}")
        print(f"  Agent Name: {agent.name}")
        
        return result
        
    except Exception as e:
        print(f"✗ Failed to deploy agent: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Main entry point."""
    # Get arguments from CLI, environment variables, or prompt user
    if len(sys.argv) > 1:
        endpoint = sys.argv[1]
        agent_yaml_path = sys.argv[2] if len(sys.argv) > 2 else 'agent.yaml'
    else:
        endpoint = os.getenv('FOUNDRY_ENDPOINT')
        agent_yaml_path = os.getenv('AGENT_YAML_PATH', 'agent.yaml')
        
        # If endpoint not set, prompt the user
        if not endpoint:
            print("\n" + "="*70)
            print("Azure AI Foundry Agent Deployment")
            print("="*70 + "\n")
            
            print("You need the Foundry Project endpoint URL.")
            print("Format: https://<account>.services.ai.azure.com/api/projects/<project-name>")
            print()
            
            endpoint = input("Enter Foundry project endpoint URL: ").strip()
            
            user_path = input(f"Enter agent YAML path (default: agent.yaml): ").strip()
            if user_path:
                agent_yaml_path = user_path
            
            print()
    
    try:
        result = deploy_agent(endpoint, agent_yaml_path)
        print(f"\nDeployment Info:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        sys.exit(0)
    except Exception as e:
        print(f"\nDEPLOYMENT FAILED: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
