import os
import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Route
from starlette.responses import JSONResponse as StarletteJSONResponse
from mcp.server import MCPServer

from Printers.StarPrinter import StarPrinter
from Printables.Message import Message
from Printables.Task import Task
from Printables.ImgMessage import ImgMessage
from config import load_config
from utils.image_utils import resize_image_for_printer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

printer_config = load_config()
PRINTER_CONNECTION = printer_config.get("connection", "usb")
PRINTER_HOST = printer_config.get("host", "")
PRINTER_PORT = int(printer_config.get("port", "9100"))

printer = StarPrinter(
    host=PRINTER_HOST if PRINTER_CONNECTION == "network" else None,
    port=PRINTER_PORT
)

# Create MCP server
mcp = MCPServer("ticketgremlin-mcp", version="1.0.0")


@mcp.tool(description="Print a basic message ticket")
async def print_message(title: str, message: str) -> str:
    msg = Message(subject=title, body=message)
    _print_message_internal(msg)
    return f"Printed message: {title}"


@mcp.tool(description="Print a task with a due date")
async def print_task(title: str, message: str, due_date: str) -> str:
    task = Task(body=message, due_date=due_date, subject=title)
    _print_message_internal(task)
    return f"Printed task: {title} (Due: {due_date})"


@mcp.tool(description="Print an image with optional title. Image will be auto-resized.")
async def print_image(filepath: str, title: Optional[str] = None) -> str:
    resized_path = resize_image_for_printer(filepath)
    msg = ImgMessage(filepath=resized_path, subject=title)
    _print_message_internal(msg)
    if os.path.exists(resized_path) and resized_path != filepath:
        os.remove(resized_path)
    return f"Printed image: {title or filepath}"


@mcp.tool(description="Feed paper and cut")
async def feed_cut() -> str:
    printer.device.open()
    printer.device.ln()
    printer.cut()
    printer.device.close()
    return "Paper fed and cut"


@mcp.tool(description="Print the current configuration")
async def print_config() -> str:
    printer.device.open()
    printer.device.textln(f"Printer Connection: {PRINTER_CONNECTION}")
    printer.device.textln(f"Printer Host: {PRINTER_HOST or 'USB'}")
    printer.device.textln(f"Printer Port: {PRINTER_PORT}")
    printer.cut()
    printer.device.close()
    return "Configuration printed"


def _print_message_internal(message):
    printer.device.open()
    printer.printMessage(message)
    printer.cut()
    printer.device.close()


# OpenAPI schema
from fastapi.openapi.utils import get_openapi

fastapi_app = FastAPI(
    title="TicketGremlin MCP",
    version="1.0.0",
    description="MCP server for printing tickets to Star Micronics printers"
)

# Generate OpenAPI schema
def get_openapi_schema():
    return get_openapi(
        title="TicketGremlin MCP",
        version="1.0.0",
        description="MCP server for printing tickets to Star Micronics printers",
        routes=fastapi_app.routes,
    )

# OpenAPI endpoint
async def openapi_json(request):
    return StarletteJSONResponse(content=get_openapi_schema())

async def openapi_options(request):
    return Response(status_code=200)

# Health check endpoint
async def health_check(request):
    try:
        test_device = StarPrinter(
            host=PRINTER_HOST if PRINTER_CONNECTION == "network" else None,
            port=PRINTER_PORT
        )
        test_device.device.open()
        test_device.device.ln(0)
        test_device.device.close()

        return StarletteJSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "printer": "connected",
                "connection_type": PRINTER_CONNECTION,
                "host": PRINTER_HOST if PRINTER_CONNECTION == "network" else "USB",
                "port": PRINTER_PORT
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return StarletteJSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": "printer_not_connected",
                "details": str(e)
            }
        )


# OPTIONS handler for health
async def health_options(request):
    return Response(status_code=200)


# Get MCP ASGI app configured for root path / with allowed hosts
from mcp.server.transport_security import TransportSecuritySettings

mcp_app = mcp.streamable_http_app(
    streamable_http_path="/",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
        allowed_hosts=["*"],  # Allow all hosts
        allowed_origins=["*"],  # Allow all origins
    )
)

# Add health check route to MCP app BEFORE its catch-all route
# We need to insert it at the beginning
health_route = Route("/health", endpoint=health_check, methods=["GET"])
health_options_route = Route("/health", endpoint=health_options, methods=["OPTIONS"])

# Insert OpenAPI and health routes at the beginning
openapi_route = Route("/openapi.json", endpoint=openapi_json, methods=["GET", "HEAD"])
openapi_options_route = Route("/openapi.json", endpoint=openapi_options, methods=["OPTIONS"])
mcp_app.routes.insert(0, health_options_route)
mcp_app.routes.insert(0, health_route)
mcp_app.routes.insert(0, openapi_options_route)
mcp_app.routes.insert(0, openapi_route)

# Add CORS middleware
from starlette.middleware.cors import CORSMiddleware
mcp_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = mcp_app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
