import os


def load_config():
    """Load printer settings from environment variables (Docker deployment)."""
    return {
        "connection": os.getenv("PRINTER_CONNECTION", "network"),
        "host": os.getenv("PRINTER_HOST", ""),
        "port": os.getenv("PRINTER_PORT", "9100"),
    }
