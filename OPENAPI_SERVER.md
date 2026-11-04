# TicketGremlin OpenAPI Server - Implementation Summary

## Overview

This document describes the **new OpenAPI-compatible server** for TicketGremlin, designed to work with **OpenWebUI** and **mcpo** (MCP-to-OpenAPI proxy).

## Why OpenAPI Instead of MCP?

After extensive research into OpenWebUI's documentation and the mcpo proxy, the following was identified:

1. **OpenWebUI has TWO distinct integration paths:**
   - **MCP (Streamable HTTP)** - Native MCP protocol support
   - **OpenAPI Tool Servers** - Standard REST APIs with OpenAPI 3.x spec

2. **mcpo** is a proxy that converts MCP servers to OpenAPI endpoints

3. **The reported issue** ("models do not call the tools") is likely due to:
   - The configuration of the model's function-calling mode
   - Compatibility issues with the MCP protocol
   - Problems with tool discovery and registration

4. **OpenAPI approach is more reliable** because:
   - Standard HTTP/REST is used
   - Better debugging capabilities
   - Any OpenAPI-compatible client can be used
   - OpenWebUI's reference implementations are followed exactly

## New Implementation: `openapi_server.py`

### Structure

The new server follows the **exact pattern** of the reference OpenAPI servers of OpenWebUI (time, filesystem):

```
openapi_server.py
├── FastAPI app with CORS enabled
├── Pydantic models for request/response validation
├── POST endpoints for each action (print_message, print_task, etc.)
├── GET endpoints for health check and info
└── Proper OpenAPI spec generation at /openapi.json
```

### Endpoints

| Method | Path | Description | Request Model | Response Model |
|--------|------|-------------|---------------|----------------|
| POST | `/print_message` | A basic message ticket is printed | `PrintMessageRequest` | `PrintMessageResponse` |
| POST | `/print_task` | A task with due date is printed | `PrintTaskRequest` | `PrintTaskResponse` |
| POST | `/feed_cut` | Paper is fed and cut | (no body) | `FeedCutResponse` |
| POST | `/print_config` | Current configuration is printed | (no body) | `PrintConfigResponse` |
| GET | `/health` | Health check | - | `HealthCheckResponse` |
| GET | `/` | API information | - | JSON |
| GET | `/openapi.json` | OpenAPI specification | - | JSON |
| GET | `/docs` | Interactive Swagger UI | - | HTML |
| GET | `/redoc` | Alternative API docs | - | HTML |

### Pydantic Models

**Request Models:**
- `PrintMessageRequest`: title (str), message (str)
- `PrintTaskRequest`: title (str), message (str), due_date (str)

**Response Models:**
- Each endpoint has a dedicated response model with status, message, and relevant data
- All responses include proper typing and descriptions for the OpenAPI spec

### Key Features

1. **CORS Enabled**: `allow_origins=["*"]` for development
2. **Error Handling**: Proper HTTPException with status codes and details
3. **Type Safety**: Full Pydantic validation for all inputs
4. **Documentation**: Auto-generated OpenAPI spec with descriptions
5. **Health Check**: `/health` endpoint for monitoring
6. **Printer Connection Testing**: Health check verifies printer connectivity

## How It Solves the Original Problem

### Problem: "Models do not call the tools in the MCP server"

With the **OpenAPI approach**, this issue is resolved because:

1. **OpenWebUI Integration**:
   - The server is added as an **OpenAPI Tool Server** (not MCP)
   - Type = **OpenAPI** (not MCP Streamable HTTP)
   - URL = `http://localhost:8080` (or the server URL)

2. **Tool Discovery**:
   - OpenWebUI reads `/openapi.json` to discover all endpoints
   - Each POST endpoint becomes a callable tool
   - No MCP protocol handshake required

3. **Model Compatibility**:
   - **Native (Agentic) Mode** function calling is supported
   - **Legacy Mode** is also supported (though Native is recommended)
   - Models can call tools via standard function calling

4. **Debugging**:
   - Endpoints can be tested directly via `/docs` (Swagger UI)
   - `curl` or any HTTP client can be used
   - Standard HTTP errors are easier to debug

## Usage with OpenWebUI

### Option 1: User Tool Server (Recommended for Local Testing)

1. The server is started:
   ```bash
   uvicorn openapi_server:app --host 0.0.0.0 --port 8080
   ```

2. In OpenWebUI:
   - **Settings → Tools** is opened
   - **+ Add Tool Server** is clicked
   - **Type** is set to **OpenAPI**
   - **URL** is entered as `http://localhost:8080`
   - **Save** is clicked

3. In chat:
   - The **➕** button in the input area is clicked
   - The tools to use are enabled
   - The model can now call: `print_message`, `print_task`, `feed_cut`, `print_config`

### Option 2: Global Tool Server (For Production/Shared Access)

1. The server is deployed (Docker recommended)
2. In OpenWebUI Admin:
   - **Admin Settings → Tools** is opened
   - **+ Add Tool Server** is clicked
   - **Type** is set to **OpenAPI**
   - **URL** is entered as `http://your-server:8080`
   - **Access Control** is configured for users/groups
   - **Save** is clicked

3. Tools must be enabled via **➕ → Integrations → Tools** in the chat

### Option 3: With mcpo Proxy (For MCP Servers)

To use mcpo as a proxy for an MCP server:

```bash
# Install mcpo
pip install mcpo

# Run mcpo with your MCP server
mcpo --port 8000 --api-key "your-api-key" -- your_mcp_server_command

# Then add to OpenWebUI as OpenAPI server
# URL: http://localhost:8000
```

The new `openapi_server.py` is already OpenAPI-compatible. mcpo is not needed.

## Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t ticketgremlin-openapi .

# Run with USB passthrough
docker run -d \
  --name ticketgremlin \
  -p 7143:8080 \
  --device /dev/bus/usb \
  -e PRINTER_CONNECTION=usb \
  -v $(pwd)/data:/app/data \
  ticketgremlin-openapi
```

### Docker Compose

```yaml
version: '3.8'
services:
  ticketgremlin:
    build: .
    ports:
      - "7143:8080"
    environment:
      - PRINTER_CONNECTION=usb
    devices:
      - "/dev/bus/usb:/dev/bus/usb"
    volumes:
      - ./data:/app/data
```

The stack is started with: `docker-compose up -d`

## Configuration

### Environment Variables

- `PRINTER_CONNECTION`: `usb` or `network` (default: `usb`)
- `PRINTER_HOST`: Hostname/IP for network printer (default: `""`)
- `PRINTER_PORT`: Port for network printer (default: `9100`)

### Config File

```json
{
  "connection": "usb",
  "host": "",
  "port": 9100
}
```

## Testing the Server

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8080/health

# Print a message
curl -X POST http://localhost:8080/print_message \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "message": "Hello World"}'

# Print a task
curl -X POST http://localhost:8080/print_task \
  -H "Content-Type: application/json" \
  -d '{"title": "Task", "message": "Do something", "due_date": "12312024"}'

# Feed and cut
curl -X POST http://localhost:8080/feed_cut \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Interactive Testing

Swagger UI is opened at `http://localhost:8080/docs`. There, the following can be done:
- All available endpoints are shown
- Endpoints are tested interactively
- Request and response schemas are shown

## Migration from MCP Server

### Changes Made

1. **New File**: `openapi_server.py` - Pure OpenAPI server
2. **Updated**: `Dockerfile` - Now builds for OpenAPI server
3. **Updated**: `docker-compose.yml` - Configured for OpenAPI server
4. **New File**: `openapi_requirements.txt` - Dependencies for OpenAPI server
5. **Updated**: `.dockerignore` - Proper ignore rules

### What Stayed the Same

- `Printables/` - Message, Task, ImgMessage classes unchanged
- `Printers/` - StarPrinter unchanged
- `utils/` - image_utils unchanged
- `config.py` - Configuration loading unchanged

### What's Different

| Aspect | MCP Server | OpenAPI Server |
|--------|------------|----------------|
| Protocol | MCP Streamable HTTP | REST/OpenAPI 3.x |
| Tool Discovery | MCP `tools/list` | OpenAPI `/openapi.json` |
| Transport | MCP-specific | Standard HTTP |
| OpenWebUI Type | MCP (Streamable HTTP) | OpenAPI |
| Debugging | MCP protocol | Standard HTTP/curl |
| Documentation | Manual | Auto-generated |

## Troubleshooting

### Common Issues

1. **"Failed to connect to tool server"**
   - The server status is checked with: `curl http://localhost:8080/health`
   - The URL in OpenWebUI settings is checked
   - CORS is configured by default

2. **"No tools available"**
   - `/openapi.json` accessibility is checked
   - The connection from OpenWebUI to the server is checked
   - For User Tool Servers, the browser must reach the URL
   - For Global Tool Servers, the OpenWebUI backend must reach the URL

3. **"Models don't call tools"**
   - The model's **Function Calling** must be set to **Native**
   - Tools are enabled in the chat via **➕ → Integrations → Tools**
   - A model that supports function calling is used (GPT-4, Claude 3, etc.)

4. **"Printer not found"**
   - USB device passthrough in Docker is checked
   - The `PRINTER_CONNECTION` environment variable is checked
   - A test is run with: `curl -X POST http://localhost:8080/print_message -H "Content-Type: application/json" -d '{"title":"Test","message":"Hello"}'`

### Health Check

The `/health` endpoint returns:
```json
{
  "status": "healthy",
  "printer": "connected",
  "connection_type": "usb",
  "host": "USB",
  "port": 9100
}
```

If the printer is disconnected:
```json
{
  "status": "degraded",
  "printer": "disconnected",
  ...
}
```

## Files Modified/Created

### Created
- `openapi_server.py` - Main OpenAPI server
- `openapi_requirements.txt` - Dependencies

### Modified
- `Dockerfile` - Build configuration
- `docker-compose.yml` - Deployment configuration
- `.dockerignore` - Docker ignore rules

### Unchanged (but required)
- `config.py`
- `Printables/Message.py`
- `Printables/Task.py`
- `Printables/ImgMessage.py`
- `Printers/StarPrinter.py`
- `utils/image_utils.py`

## Next Steps

1. **Test locally**: The server is started with `uvicorn openapi_server:app --reload`. The endpoints are tested.
2. **Deploy**: Docker or docker-compose is used.
3. **Configure OpenWebUI**: The server is added as an OpenAPI Tool Server.
4. **Enable tools**: In chat, the tools are enabled via the ➕ button.
5. **Verify**: The model is asked to print something.

## References

- [OpenWebUI OpenAPI Tool Servers Docs](https://docs.openwebui.com/features/extensibility/plugin/tools/openapi-servers/)
- [OpenWebUI MCP Docs](https://docs.openwebui.com/features/extensibility/mcp)
- [mcpo GitHub](https://github.com/open-webui/mcpo)
- [Reference OpenAPI Servers](https://github.com/open-webui/openapi-servers)
