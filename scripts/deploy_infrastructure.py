#!/usr/bin/env python3
"""
Deploy infrastructure using Bicep parameter files (.bicepparam).

This script deploys infrastructure modules using native Bicep parameter files.
All configuration is stored in .bicepparam files.

Usage:
    python scripts/deploy_infrastructure.py <module> --bicepparam <file>
    
Example:
    python scripts/deploy_infrastructure.py foundry_connection --bicepparam infrastructure/nonprod.bicepparam
"""

import os
import sys
import subprocess
from pathlib import Path

def deploy_infrastructure(module: str, bicepparam_file: str):
    """Deploy infrastructure for the given module using Bicep parameter file."""
    print(f"🚀 Deploying infrastructure module: {module}")
    print(f"📦 Deploying {module} module")
    print(f"📄 Using Bicep parameters file: {bicepparam_file}")
    
    # Validate bicepparam file exists
    if not Path(bicepparam_file).exists():
        raise FileNotFoundError(f"Bicep parameters file not found: {bicepparam_file}")
    
    # Get resource group from environment or use default
    resource_group = os.getenv('RESOURCE_GROUP', 'ad-usa-poc')
    
    # Determine template to deploy
    if module == 'foundry_connection':
        template_file = 'infrastructure/modules/foundry_connection/connection.bicep'
    else:
        raise ValueError(f"Unknown module: {module}. Available: foundry_connection")
    
    if not Path(template_file).exists():
        raise FileNotFoundError(f"Template not found: {template_file}")
    
    print(f"\n📋 Deployment Configuration:")
    print(f"  Resource Group: {resource_group}")
    print(f"  Template: {template_file}")
    print(f"  Parameters: {bicepparam_file}")
    
    # Build Azure CLI command with bicepparam file
    cmd = [
        'az', 'deployment', 'group', 'create',
        '--resource-group', resource_group,
        '--template-file', template_file,
        '--parameters', bicepparam_file
    ]
    
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
    parser = argparse.ArgumentParser(
        description='Deploy infrastructure modules using Bicep parameter files',
        epilog='Examples:\n'
               '  python scripts/deploy_infrastructure.py foundry_connection --bicepparam infrastructure/nonprod.bicepparam',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('module', 
                        choices=['foundry_connection'],
                        help='Module to deploy')
    parser.add_argument('--bicepparam',
                        required=True,
                        help='Path to Bicep parameter file (.bicepparam)')
    
    args = parser.parse_args()
    
    try:
        success = deploy_infrastructure(args.module, args.bicepparam)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
