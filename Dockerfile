# TicketGremlin OpenAPI server image (network printer deployment)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Container-internal port. The host-side port is set in docker-compose.yml
# (currently "7143:8080"); anything inside the container always uses 8080.
EXPOSE 8080

# Service-level health check: must NOT fail when only the printer is down
# (that is reported by GET /health with a 503 for external monitors).
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

CMD ["python3", "-m", "uvicorn", "openapi_server:app", "--host", "0.0.0.0", "--port", "8080"]
