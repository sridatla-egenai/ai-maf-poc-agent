import asyncio
import httpx
import uvicorn
import anyio
import os
from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route
from mcp.server import Server, InitializationOptions
from mcp.types import Tool, TextContent, JSONRPCMessage
import mcp.types as types
from mcp.shared.message import SessionMessage

# --- 1. Custom SSE Transport Logic ---
# This ensures we handle the message queues correctly between GET and POST
class StarletteSSEServerTransport:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        # Streams for incoming messages (Client -> Server)
        self._in_send, self._in_recv = anyio.create_memory_object_stream(100)
        # Streams for outgoing messages (Server -> Client)
        self._out_send, self._out_recv = anyio.create_memory_object_stream(100)

    async def handle_post_message(self, message_dict):
        """Feed a JSON-RPC message from a POST request into the server"""
        # Parse the dict into the correct MCP JSONRPCMessage type
        try:
            # We use the parsing logic from the SDK to ensure safety
            parsed_msg = types.JSONRPCMessage.model_validate(message_dict)
            # Wrap in SessionMessage as expected by MCP Session
            await self._in_send.send(SessionMessage(message=parsed_msg))
        except Exception as e:
            print(f"Error parsing message: {e}")

    async def sse_generator(self):
        """Yields SSE formatted events for the GET request"""
        yield f"event: endpoint\ndata: {self.endpoint}\n\n"
        
        async with self._out_recv:
            async for message in self._out_recv:
                try:
                    # message is a SessionMessage, we need the inner JSONRPCMessage
                    if isinstance(message, SessionMessage):
                        json_msg = message.message
                    else:
                        json_msg = message

                    # Serialize to JSON and format as SSE
                    json_str = json_msg.model_dump_json()
                    yield f"event: message\ndata: {json_str}\n\n"
                except Exception as e:
                    print(f"Error in SSE generator: {e}")

# --- 2. Initialize MCP Server ---
mcp_server = Server("Product-API-Proxy")

@mcp_server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_products",
            description="Fetch products from backend. Optional category filter.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string"}
                }
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_products":
        category = arguments.get("category")
        base_url = os.getenv("PRODUCT_API_URL", "http://localhost:8000")
        url = f"{base_url}/get-all-products"
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url)
                data = resp.json()
                
                if category:
                    # Filter by productGroup if category is provided
                    data = [p for p in data if p.get("productGroup", "").lower() == category.lower()]
                
                return [TextContent(type="text", text=str(data))]
            except Exception as e:
                return [TextContent(type="text", text=f"Backend Error: {e}")]
    
    raise ValueError(f"Unknown tool: {name}")

# --- 3. Starlette Routes ---
# We store the active transport here. 
# Note: For production, use a dict mapped by SessionID.
active_transport = None

async def handle_sse(request):
    global active_transport
    
    # 1. Create a new Transport
    transport = StarletteSSEServerTransport("/mcp")
    active_transport = transport

    # 2. Run the MCP Server connection in the background
    # This connects the Server logic (tools) to our Transport queues
    init_options = InitializationOptions(
        server_name="product-mcp-server",
        server_version="0.1.0",
        capabilities=types.ServerCapabilities(
            tools=types.ToolsCapability()
        )
    )

    asyncio.create_task(mcp_server.run(
        read_stream=transport._in_recv,
        write_stream=transport._out_send,
        initialization_options=init_options
    ))

    # 3. Return the SSE Stream
    return StreamingResponse(transport.sse_generator(), media_type="text/event-stream")

async def handle_messages(request):
    global active_transport
    if not active_transport:
        return JSONResponse({"error": "No active connection"}, status_code=400)

    try:
        body = await request.json()
        await active_transport.handle_post_message(body)
        return JSONResponse({"status": "accepted"}, status_code=202)
    except Exception as e:
        print(f"Error handling POST: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

# --- 4. App Definition ---
routes = [
    Route("/mcp", handle_sse, methods=["GET"]),
    Route("/mcp", handle_messages, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    # Ensure port matches mcp.json (8001)
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")