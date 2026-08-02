FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libusb-1.0-0 \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt mcp_requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r mcp_requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser
USER appuser

RUN chmod a+rw /dev/bus/usb/* 2>/dev/null || true

EXPOSE 8080

HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8080"]
