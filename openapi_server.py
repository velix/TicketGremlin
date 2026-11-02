from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field
import logging
import threading

from Printers.StarPrinter import StarPrinter
from Printables.Message import Message
from Printables.Task import Task
from config import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load printer configuration
printer_config = load_config()
PRINTER_CONNECTION = printer_config.get("connection", "usb")
PRINTER_HOST = printer_config.get("host", "")
PRINTER_PORT = int(printer_config.get("port", "9100"))

# Initialize printer (network connection; PRINTER_HOST/PRINTER_PORT from env)
printer = StarPrinter(host=PRINTER_HOST, port=PRINTER_PORT)

# The printer accepts one TCP 9100 connection at a time; serialize print jobs
print_lock = threading.Lock()

# Create FastAPI app
app = FastAPI(
    title="TicketGremlin API",
    version="1.0.0",
    description="OpenAPI server for printing tickets to Star Micronics printers",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------------------
# Pydantic Request Models
# ------------------------------------------------------------------------------

class PrintMessageRequest(BaseModel):
    """Request model for printing a basic message ticket."""
    title: str = Field(..., description="Title/subject of the message")
    message: str = Field(..., description="Body content of the message")


class PrintMessageResponse(BaseModel):
    """Response model for print_message."""
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Confirmation message")
    title: str = Field(..., description="Title that was printed")


class PrintTaskRequest(BaseModel):
    """Request model for printing a task with due date."""
    title: str = Field(..., description="Title/subject of the task")
    message: str = Field(..., description="Body content of the task")
    due_date: str = Field(..., description="Due date for the task (format: MMDDYYYY or 'ASAP')")


class PrintTaskResponse(BaseModel):
    """Response model for print_task."""
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Confirmation message")
    title: str = Field(..., description="Title that was printed")
    due_date: str = Field(..., description="Due date that was printed")


class FeedCutResponse(BaseModel):
    """Response model for feed_cut."""
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Confirmation message")


class PrintConfigResponse(BaseModel):
    """Response model for print_config."""
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Confirmation message")
    connection_type: str = Field(..., description="Printer connection type")
    host: str = Field(..., description="Printer host (or 'USB')")
    port: int = Field(..., description="Printer port")


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Health status")
    printer: str = Field(..., description="Printer connection status")
    connection_type: str = Field(..., description="Printer connection type")
    host: str = Field(..., description="Printer host")
    port: int = Field(..., description="Printer port")


# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------

def _print_message_internal(printable):
    """Internal helper to print any printable object."""
    try:
        with print_lock:
            printer.device.open()
            printer.printMessage(printable)
            printer.cut()
            printer.device.close()
    except Exception as e:
        logger.error(f"Printing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Printer error: {str(e)}"
        )


def _test_printer_connection():
    """Test if printer is connected and accessible."""
    try:
        test_device = StarPrinter(host=PRINTER_HOST, port=PRINTER_PORT)
        test_device.device.open()
        test_device.device.ln(0)
        test_device.device.close()
        return True
    except Exception as e:
        logger.error(f"Printer connection test failed: {str(e)}")
        return False


# ------------------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------------------

@app.post(
    "/print_message",
    operation_id="print_message",
    response_model=PrintMessageResponse,
    summary="Print a basic message ticket",
    description="Prints a message with a title to the connected Star Micronics printer. The printer will automatically cut the paper after printing."
)
async def print_message(
    request: PrintMessageRequest = Body(..., description="Message print request")
) -> PrintMessageResponse:
    """
    Print a basic message ticket.
    
    The message will be printed with the specified title, and the paper will be 
    automatically cut after printing.
    """
    try:
        msg = Message(subject=request.title, body=request.message)
        _print_message_internal(msg)
        return PrintMessageResponse(
            status="success",
            message=f"Printed message: {request.title}",
            title=request.title
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in print_message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to print message: {str(e)}"
        )


@app.post(
    "/print_task",
    operation_id="print_task",
    response_model=PrintTaskResponse,
    summary="Print a task with due date",
    description="Prints a task with a title, message body, and due date to the connected Star Micronics printer. The printer will automatically cut the paper after printing."
)
async def print_task(
    request: PrintTaskRequest = Body(..., description="Task print request")
) -> PrintTaskResponse:
    """
    Print a task with a due date.
    
    The task will be printed with title, message body, and due date. The paper will be 
    automatically cut after printing.
    
    Due date format: MMDDYYYY (e.g., 12312024 for December 31, 2024) or 'ASAP'
    """
    try:
        task = Task(
            body=request.message,
            due_date=request.due_date,
            subject=request.title
        )
        _print_message_internal(task)
        return PrintTaskResponse(
            status="success",
            message=f"Printed task: {request.title}",
            title=request.title,
            due_date=request.due_date
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in print_task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to print task: {str(e)}"
        )


@app.post(
    "/feed_cut",
    operation_id="feed_cut",
    response_model=FeedCutResponse,
    summary="Feed paper and cut",
    description="Feeds a line of paper and cuts it. Useful for advancing paper between prints or creating a clean cut."
)
async def feed_cut() -> FeedCutResponse:
    """
    Feed paper and cut.
    
    Advances the paper by one line and performs a cut. This is useful for:
    - Advancing paper between print jobs
    - Creating a clean cut when the printer hasn't cut properly
    - Separating printouts
    """
    try:
        with print_lock:
            printer.device.open()
            printer.device.ln()
            printer.cut()
            printer.device.close()
        return FeedCutResponse(
            status="success",
            message="Paper fed and cut"
        )
    except Exception as e:
        logger.error(f"Error in feed_cut: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to feed and cut: {str(e)}"
        )


@app.post(
    "/print_config",
    operation_id="print_config",
    response_model=PrintConfigResponse,
    summary="Print current configuration",
    description="Prints the current printer configuration to the printer itself. Useful for debugging and verifying settings."
)
async def print_config() -> PrintConfigResponse:
    """
    Print current configuration.
    
    Prints the printer connection settings (type, host, port) to the printer.
    Useful for verifying that the printer is configured correctly.
    """
    try:
        with print_lock:
            printer.device.open()
            printer.device.textln(f"Printer Connection: {PRINTER_CONNECTION}")
            printer.device.textln(f"Printer Host: {PRINTER_HOST or 'USB'}")
            printer.device.textln(f"Printer Port: {PRINTER_PORT}")
            printer.cut()
            printer.device.close()

        return PrintConfigResponse(
            status="success",
            message="Configuration printed",
            connection_type=PRINTER_CONNECTION,
            host=PRINTER_HOST or "USB",
            port=PRINTER_PORT
        )
    except Exception as e:
        logger.error(f"Error in print_config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to print configuration: {str(e)}"
        )


@app.get(
    "/health",
    operation_id="health",
    response_model=HealthCheckResponse,
    summary="Health check endpoint",
    description="Check if the TicketGremlin API server is running and if the printer is connected. Returns HTTP 200 when healthy, 503 when the printer is unreachable (for Uptime Kuma and other monitors)."
)
async def health_check():
    """
    Health check endpoint.

    Returns the health status of the API server and the printer connection.
    HTTP 200 = service up and printer reachable; HTTP 503 = printer degraded,
    so external monitors (e.g. Uptime Kuma) flag the service as down.
    """
    with print_lock:
        printer_connected = _test_printer_connection()

    body = HealthCheckResponse(
        status="healthy" if printer_connected else "degraded",
        printer="connected" if printer_connected else "disconnected",
        connection_type=PRINTER_CONNECTION,
        host=PRINTER_HOST or "USB",
        port=PRINTER_PORT
    )
    return JSONResponse(
        status_code=200 if printer_connected else 503,
        content=body.model_dump()
    )


# ------------------------------------------------------------------------------
# Root endpoint
# ------------------------------------------------------------------------------

@app.get(
    "/",
    operation_id="info",
    summary="API Information",
    description="Returns basic information about the TicketGremlin API server."
)
async def root():
    """API information endpoint."""
    return {
        "name": "TicketGremlin API",
        "version": "1.0.0",
        "description": "OpenAPI server for printing tickets to Star Micronics printers",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "health": "/health"
    }
