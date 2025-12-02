#!/usr/bin/env python3
"""
Deploy infrastructure using Bicep with YAML variables.

This script:
1. Loads environment variables from YAML
2. Converts them to Bicep parameters
3. Deploys using Azure CLI

Usage:
    python scripts/deploy_infrastructure.py <environment>
    
Example:
    python scripts/deploy_infrastructure.py nonprod
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path

def load_variables(env: str) -> dict:
    """Load variables from YAML file."""
    var_file = Path(f"infrastructure/variables/{env}.yaml")
    
    if not var_file.exists():
        raise FileNotFoundError(f"Variables file not found: {var_file}")
    
    with open(var_file, 'r') as f:
        return yaml.safe_load(f)

def deploy_infrastructure(env: str, module: str = 'all'):
    """Deploy infrastructure for the given environment and module."""
    print(f"🚀 Deploying infrastructure for environment: {env}")
    print(f"📦 Module: {module}")
    
    # Load variables
    vars = load_variables(env)
    print(f"✓ Loaded variables from infrastructure/variables/{env}.yaml")
    
    # Get API key from environment variable
    api_key = os.getenv('TODO_API_KEY')
    if not api_key:
        raise ValueError("TODO_API_KEY environment variable not set")
    
    # Extract configuration
    resource_group = vars['azure']['resourceGroup']
    location = vars['azure']['location']
    project_name = vars['foundry']['projectName']
    connection_name = vars['connection']['name']
    target_url = vars['connection']['targetUrl']
    connection_type = vars['connection']['type']
    tags = vars.get('tags', {})
    
    # Convert tags to Bicep format
    tags_param = ' '.join([f"{k}={v}" for k, v in tags.items()])
    
    # Determine template to deploy
    if module == 'all':
        template_file = 'infrastructure/main.bicep'
        print("Deploying ALL infrastructure via main.bicep")
    elif module == 'foundry_connection':
        template_file = 'infrastructure/modules/foundry_connection/connection.bicep'
        print(f"Deploying ONLY {module} module")
    else:
        raise ValueError(f"Unknown module: {module}")
        
    print(f"\n📋 Deployment Configuration:")
    print(f"  Resource Group: {resource_group}")
    print(f"  Template: {template_file}")
    
    # Build Azure CLI command
    cmd = [
        'az', 'deployment', 'group', 'create',
        '--resource-group', resource_group,
        '--template-file', template_file,
        '--parameters',
        f'location={location}',
        f'tags={{{tags_param}}}'
    ]
    
    # Add module-specific parameters
    if module == 'all' or module == 'foundry_connection':
        cmd.extend([
            '--parameters',
            f'projectName={project_name}',
            f'connectionName={connection_name}',
            f'targetUrl={target_url}',
            f'connectionType={connection_type}',
            f'apiKey={api_key}'
        ])
    
    print(f"\n🔧 Running deployment...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"\n✅ Infrastructure deployed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deployment failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Deploy infrastructure')
    parser.add_argument('environment', help='Environment (nonprod/prod)')
    parser.add_argument('--module', default='all', help='Module to deploy (all, foundry_connection)')
    
    args = parser.parse_args()
    
    try:
        success = deploy_infrastructure(args.environment, args.module)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
