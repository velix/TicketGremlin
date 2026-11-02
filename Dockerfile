# TicketGremlin OpenAPI Server Dockerfile
# Multi-stage build for smaller final image

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies for USB printer access
RUN apt-get update && apt-get install -y --no-install-recommends \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create necessary directories.
# /app/data is OPTIONAL: nothing in the app requires it for text/task printing
# over the network. docker-compose.yml mounts the host ./data directory here
# (writable) only so POST /print_image can reach image files stored on the
# host, e.g. {"filepath": "/app/data/photo.jpg"}.
# The mount must stay writable: utils/image_utils.py writes the resized image
# next to the original, and a read-only mount makes /print_image fail with
# PermissionError. The endpoint deletes the resized copy after printing.
RUN mkdir -p /app/Printables /app/Printers /app/utils /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Ensure the user has proper permissions for USB devices
RUN usermod -aG lp www-data 2>/dev/null || true

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Run the OpenAPI server
CMD ["python3", "-m", "uvicorn", "openapi_server:app", "--host", "0.0.0.0", "--port", "8080"]
