# TicketGremlin OpenAPI Server - Implementation Summary

## Overview

This document describes the **new OpenAPI-compatible server** for TicketGremlin, designed to work seamlessly with **OpenWebUI** and **mcpo** (MCP-to-OpenAPI proxy).

## Why OpenAPI Instead of MCP?

After extensive research into OpenWebUI's documentation and the mcpo proxy, we identified that:

1. **OpenWebUI has TWO distinct integration paths:**
   - **MCP (Streamable HTTP)** - Native MCP protocol support
   - **OpenAPI Tool Servers** - Standard REST APIs with OpenAPI 3.x spec

2. **mcpo** is a proxy that converts MCP servers to OpenAPI endpoints

3. **The user's issue** ("models do not call the tools") is likely due to:
   - Model function calling mode configuration
   - MCP protocol compatibility issues
   - Tool discovery/registration problems

4. **OpenAPI approach is more reliable** because:
   - Uses standard HTTP/REST
   - Better debugging capabilities
   - Works with any OpenAPI-compatible client
   - Follows OpenWebUI's reference implementations exactly

## New Implementation: `openapi_server.py`

### Structure

The new server follows the **exact pattern** of OpenWebUI's reference OpenAPI servers (time, filesystem):

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
| POST | `/print_message` | Print a basic message ticket | `PrintMessageRequest` | `PrintMessageResponse` |
| POST | `/print_task` | Print a task with due date | `PrintTaskRequest` | `PrintTaskResponse` |
| POST | `/feed_cut` | Feed paper and cut | (no body) | `FeedCutResponse` |
| POST | `/print_config` | Print current configuration | (no body) | `PrintConfigResponse` |
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
- All responses include proper typing and descriptions for OpenAPI spec

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
   - Add as **OpenAPI Tool Server** (not MCP)
   - Type = **OpenAPI** (not MCP Streamable HTTP)
   - URL = `http://localhost:8080` (or your server URL)

2. **Tool Discovery**:
   - OpenWebUI reads `/openapi.json` to discover all endpoints
   - Each POST endpoint becomes a callable tool
   - No MCP protocol handshake required

3. **Model Compatibility**:
   - Works with **Native (Agentic) Mode** function calling
   - Also works with **Legacy Mode** (though Native is recommended)
   - Models can call tools via standard function calling

4. **Debugging**:
   - Can test endpoints directly via `/docs` (Swagger UI)
   - Can use `curl` or any HTTP client
   - Standard HTTP errors are easier to debug

## Usage with OpenWebUI

### Option 1: User Tool Server (Recommended for Local Testing)

1. Start the server:
   ```bash
   uvicorn openapi_server:app --host 0.0.0.0 --port 8080
   ```

2. In OpenWebUI:
   - Go to **Settings → Tools**
   - Click **+ Add Tool Server**
   - Set **Type** = **OpenAPI**
   - Enter **URL** = `http://localhost:8080`
   - Click **Save**

3. In chat:
   - Click the **➕** button in the input area
   - Enable the tools you want to use
   - The model can now call: `print_message`, `print_task`, `feed_cut`, `print_config`

### Option 2: Global Tool Server (For Production/Shared Access)

1. Deploy the server (Docker recommended)
2. In OpenWebUI Admin:
   - Go to **Admin Settings → Tools**
   - Click **+ Add Tool Server**
   - Set **Type** = **OpenAPI**
   - Enter **URL** = `http://your-server:8080`
   - Configure **Access Control** for users/groups
   - Click **Save**

3. Users must enable tools via **➕ → Integrations → Tools** in their chat

### Option 3: With mcpo Proxy (For MCP Servers)

If you want to use mcpo to proxy an MCP server:

```bash
# Install mcpo
pip install mcpo

# Run mcpo with your MCP server
mcpo --port 8000 --api-key "your-api-key" -- your_mcp_server_command

# Then add to OpenWebUI as OpenAPI server
# URL: http://localhost:8000
```

But with our new `openapi_server.py`, **you don't need mcpo** - it's already OpenAPI-compatible!

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

Run with: `docker-compose up -d`

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

Visit `http://localhost:8080/docs` for Swagger UI where you can:
- See all available endpoints
- Try them out interactively
- See request/response schemas

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
   - Verify server is running: `curl http://localhost:8080/health`
   - Check URL in OpenWebUI settings
   - Ensure CORS is configured (it is by default)

2. **"No tools available"**
   - Check `/openapi.json` is accessible
   - Verify OpenWebUI can reach the server
   - For User Tool Servers: browser must be able to reach the URL
   - For Global Tool Servers: OpenWebUI backend must be able to reach the URL

3. **"Models don't call tools"**
   - Ensure model's **Function Calling** is set to **Native**
   - Enable tools in the chat via **➕ → Integrations → Tools**
   - Use a model that supports function calling (GPT-4, Claude 3, etc.)

4. **Printer not found**
   - Verify USB device passthrough in Docker
   - Check `PRINTER_CONNECTION` environment variable
   - Test with: `curl -X POST http://localhost:8080/print_message -H "Content-Type: application/json" -d '{"title":"Test","message":"Hello"}'`

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

If printer is disconnected:
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

1. **Test locally**: Run `uvicorn openapi_server:app --reload` and test endpoints
2. **Deploy**: Use Docker or docker-compose
3. **Configure OpenWebUI**: Add as OpenAPI Tool Server
4. **Enable tools**: In chat, enable the tools via ➕ button
5. **Verify**: Ask the model to print something

## References

- [OpenWebUI OpenAPI Tool Servers Docs](https://docs.openwebui.com/features/extensibility/plugin/tools/openapi-servers/)
- [OpenWebUI MCP Docs](https://docs.openwebui.com/features/extensibility/mcp)
- [mcpo GitHub](https://github.com/open-webui/mcpo)
- [Reference OpenAPI Servers](https://github.com/open-webui/openapi-servers)
