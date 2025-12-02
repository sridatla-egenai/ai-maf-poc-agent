#!/usr/bin/env python3
"""
Convert YAML parameter file to Bicep-compatible JSON format.
This allows you to write parameters in YAML but deploy with Bicep.
"""

import sys
import json
import yaml
from pathlib import Path

def convert_yaml_to_bicep_params(yaml_path: str, output_path: str = None):
    """
    Convert YAML parameters to Bicep JSON parameter format.
    
    Args:
        yaml_path: Path to YAML parameter file
        output_path: Optional output path for JSON file
    """
    with open(yaml_path, 'r') as f:
        params = yaml.safe_load(f)
    
    # Convert to Bicep parameter format
    bicep_params = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {}
    }
    
    for key, value in params.items():
        bicep_params["parameters"][key] = {"value": value}
    
    # Determine output path
    if not output_path:
        output_path = yaml_path.replace('.yaml', '.json').replace('.yml', '.json')
    
    # Write JSON file
    with open(output_path, 'w') as f:
        json.dump(bicep_params, f, indent=2)
    
    print(f"✅ Converted {yaml_path} -> {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/yaml_to_bicep_params.py <yaml_file> [output_json]")
        sys.exit(1)
    
    yaml_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_yaml_to_bicep_params(yaml_path, output_path)
