#!/usr/bin/env python3
"""
Deploy a Connection to Azure AI Foundry.

A Connection stores credentials and endpoint information for external services.
Once created, it can be referenced by multiple tools/agents.

Usage:
    python scripts/deploy_connection.py <endpoint> <connection_yaml_path>
"""

import os
import sys
import yaml
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


def deploy_connection(endpoint: str, connection_yaml_path: str):
    """
    Deploy a connection to Azure AI Foundry.
    
    Args:
        endpoint: Foundry project endpoint
        connection_yaml_path: Path to connection YAML definition
    """
    # Load connection definition
    print(f"Loading connection from: {connection_yaml_path}")
    with open(connection_yaml_path, 'r') as f:
        conn_def = yaml.safe_load(f)
    
    # Validate required fields
    required = ['name', 'type', 'target']
    for field in required:
        if field not in conn_def:
            raise ValueError(f"Connection definition missing '{field}'")
    
    # Initialize client
    print(f"Connecting to Azure AI Foundry: {endpoint}")
    credential = DefaultAzureCredential()
    client = AIProjectClient(endpoint=endpoint, credential=credential)
    
    # Prepare connection parameters
    conn_name = conn_def['name']
    conn_type = conn_def['type']  # e.g., 'CustomKeys', 'ApiKey'
    target = conn_def['target']  # The API endpoint
    
    # Get credentials from environment (never hardcode!)
    credentials = {}
    if 'credentials' in conn_def:
        for key, value in conn_def['credentials'].items():
            # If value starts with ${, it's an env var reference
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                env_value = os.getenv(env_var)
                if not env_value:
                    raise ValueError(f"Environment variable {env_var} not set")
                credentials[key] = env_value
            else:
                credentials[key] = value
    
    print(f"Creating connection: {conn_name}")
    print(f"  Type: {conn_type}")
    print(f"  Target: {target}")
    
    # Create the connection using the SDK
    try:
        # Note: The exact API may vary based on SDK version
        # This is a conceptual implementation
        connection = client.connections.create_or_update(
            name=conn_name,
            properties={
                'category': conn_type,
                'target': target,
                'authType': conn_def.get('auth_type', 'CustomKeys'),
                'credentials': credentials
            }
        )
        
        print(f"✅ Connection '{conn_name}' created successfully!")
        print(f"   Connection ID: {connection.id}")
        return connection
        
    except AttributeError:
        # If connections API is not available in current SDK
        print("⚠️  Connection creation via SDK not available in current version.")
        print("   Please create the connection via:")
        print("   1. Azure Portal (AI Foundry)")
        print("   2. Azure CLI")
        print("   3. Bicep/ARM template")
        print(f"\n   Connection details:")
        print(f"   - Name: {conn_name}")
        print(f"   - Type: {conn_type}")
        print(f"   - Target: {target}")
        return None
    except Exception as e:
        print(f"❌ Failed to create connection: {e}")
        raise


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/deploy_connection.py <endpoint> <connection_yaml_path>")
        print("\nExample:")
        print("  python scripts/deploy_connection.py \\")
        print("    'https://my-project.services.ai.azure.com/api/projects/my-project' \\")
        print("    'connections/todo-api.yaml'")
        sys.exit(1)
    
    endpoint = sys.argv[1]
    connection_yaml_path = sys.argv[2]
    
    try:
        deploy_connection(endpoint, connection_yaml_path)
    except Exception as e:
        print(f"\nDeployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
