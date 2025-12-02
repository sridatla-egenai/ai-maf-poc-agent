from typing import List, Dict
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAISearchAgentTool,
    FileSearchTool,
    OpenApiAgentTool,
    OpenApiFunctionDefinition,
    OpenApiAnonymousAuthDetails,
    OpenApiProjectConnectionAuthDetails,
    OpenApiProjectConnectionSecurityScheme,
    AzureAISearchToolResource,
    AISearchIndexResource,
    CodeInterpreterTool,
    MCPTool
)


def build_tools_from_yaml(project_client: AIProjectClient, tools_cfg: List[Dict]):
    """
    Convert logical YAML tool entries into concrete Tool objects
    for Azure AI Foundry Agent Service.

    - YAML defines: type, id, options
    """
    tools = []

    for t in tools_cfg or []:
        tool_type = t.get("type")
        tool_id = t.get("id") # This is often the name
        options = t.get("options", {})
        
        # Fallback for older schema if 'kind'/'name' are used
        if not tool_type and "kind" in t:
             tool_type = t.get("kind")
        if not tool_id and "name" in t:
             tool_id = t.get("name")

        if not tool_type:
            print(f"⚠ Tool entry missing 'type': {t}, skipping")
            continue

        # 1) Generic Azure AI Search tool
        if tool_type == "azure_ai_search":
            connection_id = options.get("connection_id", "CONN_PRIMARY_SEARCH")
            index_name = options.get("index_name", "primary-search-index")
            
            tools.append(
                AzureAISearchAgentTool(
                    azure_ai_search=AzureAISearchToolResource(
                        indexes=[
                            AISearchIndexResource(
                                project_connection_id=connection_id,
                                index_name=index_name
                            )
                        ]
                    )
                )
            )

        # 2) File Search / vector store
        elif tool_type == "file_search":
            vector_store_id = options.get("vector_store_id")
            if not vector_store_id:
                 # Try to find a default or raise warning
                 print(f"⚠ file_search tool '{tool_id}' missing 'vector_store_id' in options")
            
            tools.append(
                FileSearchTool(
                    vector_store_ids=[vector_store_id] if vector_store_id else []
                )
            )

        # 3) OpenAPI-based tool
        elif tool_type == "openapi":
            spec_url = options.get("specification")
            if not spec_url:
                 # Fallback to 'spec_url' if used in other schemas
                 spec_url = options.get("spec_url")
            
            if not spec_url:
                raise ValueError(f"OpenAPI tool '{tool_id}' missing 'specification' URL")

            # Determine Auth
            auth = OpenApiAnonymousAuthDetails()
            connection_id = options.get("connection_id")
            
            if connection_id:
                auth = OpenApiProjectConnectionAuthDetails(
                    security_scheme=OpenApiProjectConnectionSecurityScheme(
                        project_connection_id=connection_id
                    )
                )

            # Handle local file paths
            spec_content = spec_url
            if spec_url.startswith("file://"):
                try:
                    import json
                    from pathlib import Path
                    file_path = spec_url.replace("file://", "")
                    # Resolve relative to current working directory if needed
                    if not Path(file_path).is_absolute():
                        file_path = Path.cwd() / file_path
                    
                    with open(file_path, 'r') as f:
                        # Load as JSON/dict if possible, or string
                        if file_path.suffix == '.json':
                            spec_content = json.load(f)
                        else:
                            spec_content = f.read()
                    print(f"Loaded OpenAPI spec from {file_path}")
                except Exception as e:
                    raise ValueError(f"Failed to read OpenAPI spec file {spec_url}: {e}")

            # Create OpenAPI Definition
            openapi_def = OpenApiFunctionDefinition(
                name=tool_id,
                spec=spec_content,
                description=t.get("description", ""),
                auth=auth
            )

            # Wrap in Agent Tool
            tools.append(
                OpenApiAgentTool(
                    openapi=openapi_def
                )
            )

        # 4) MCP Tool
        elif tool_type == "mcp":
            server_url = options.get("server_url")
            allowed_tools = options.get("allowed_tools", [])
            if not server_url:
                 raise ValueError(f"MCP tool '{tool_id}' missing 'server_url'")
            
            tools.append(
                MCPTool(
                    server_label=tool_id,
                    server_url=server_url,
                    allowed_tools=allowed_tools,
                )
            )

        # 5) Code interpreter
        elif tool_type == "code_interpreter":
            tools.append(
                CodeInterpreterTool()
            )
            
        # 6) Bing Connection (if treated as a tool type or connection)
        elif tool_type == "bing_connection":
             # This might be a specific implementation or just a connection reference
             # For now, we can skip or implement if we have a class for it.
             # Assuming it might be an OpenAPI tool wrapping Bing or similar.
             pass

        else:
            print(f"⚠ Unsupported tool type '{tool_type}' in YAML")

    return tools
