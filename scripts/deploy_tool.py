#!/usr/bin/env python3
import os
import sys
import yaml
import jsonref
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import OpenApiAgentTool, OpenApiAnonymousAuthDetails, OpenApiFunctionDefinition

def deploy_tool(tool_path: str, endpoint: str = None):
    """
    Deploy (prepare and validate) a tool from a directory.
    
    Args:
        tool_path: Path to the tool directory (containing tool.yaml)
        endpoint: Azure AI Foundry endpoint (optional, for connection creation)
    """
    tool_dir = Path(tool_path)
    yaml_path = tool_dir / "tool.yaml"
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"tool.yaml not found in {tool_dir}")
        
    print(f"Loading tool definition from {yaml_path}...")
    with open(yaml_path, "r") as f:
        tool_def = yaml.safe_load(f)
        
    # Validate required fields
    if "name" not in tool_def:
        raise ValueError("Tool definition missing 'name'")
    if "type" not in tool_def:
        raise ValueError("Tool definition missing 'type'")
        
    # Handle OpenAPI tools
    if tool_def["type"] == "openapi":
        spec_file = tool_def.get("spec_path")
        if not spec_file:
            raise ValueError("OpenAPI tool missing 'spec_path'")
            
        spec_path = tool_dir / spec_file
        if not spec_path.exists():
            raise ValueError(f"OpenAPI spec not found at {spec_path}")
            
        print(f"Loading OpenAPI spec from {spec_path}...")
        with open(spec_path, "r") as f:
            # Use jsonref to resolve references
            openapi_spec = jsonref.loads(f.read())
            
        # Handle Auth
        auth_config = tool_def.get("auth", {})
        auth_type = auth_config.get("type", "anonymous")
        
        if auth_type == "anonymous":
            auth = OpenApiAnonymousAuthDetails()
            print("Auth Type: Anonymous")
        else:
            # TODO: Implement other auth types (connection, managed_identity)
            print(f"Auth Type: {auth_type} (Note: Only anonymous fully implemented in this script)")
            auth = OpenApiAnonymousAuthDetails()
            
        # Create the Tool Object
        # First create the OpenAPI function definition
        try:
            openapi_def = OpenApiFunctionDefinition(
                name=tool_def["name"],
                spec=openapi_spec,
                description=tool_def.get("description", ""),
                auth=auth
            )
            
            # Then wrap it in OpenApiAgentTool
            tool = OpenApiAgentTool(
                openapi=openapi_def
            )
            
            print(f"✅ Tool '{tool_def['name']}' successfully validated and created in memory.")
            
            # In the current SDK, tools are attached to agents. 
            # There isn't a standalone "upload tool" API call for OpenAPI tools 
            # other than creating a Connection (if auth is needed).
            # So "deploying" here means validating it's ready for use.
            
            return tool
            
        except Exception as e:
            print(f"❌ Failed to create tool object: {e}")
            raise
            
    else:
        print(f"⚠ Tool type '{tool_def['type']}' not yet supported by this script.")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/deploy_tool.py <path_to_tool_directory> [endpoint]")
        sys.exit(1)
        
    tool_path = sys.argv[1]
    endpoint = sys.argv[2] if len(sys.argv) > 2 else os.getenv("FOUNDRY_ENDPOINT")
    
    try:
        deploy_tool(tool_path, endpoint)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
