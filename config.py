import configparser
import os
from os import path

DEFAULT_CONFIG_PATH = path.join(
    path.expanduser("~"), ".config", "gremlin", "gremlin.ini"
)

DEFAULTS = {
    "printer": {
        "connection": "usb",
        "host": "",
        "port": "9100",
    }
}


def load_config(config_path=DEFAULT_CONFIG_PATH):
    """Load printer settings from env vars or config file."""
    connection = os.getenv("PRINTER_CONNECTION")
    host = os.getenv("PRINTER_HOST")
    port = os.getenv("PRINTER_PORT", "9100")

    if connection is not None or host is not None:
        return {
            "connection": connection or "usb",
            "host": host or "",
            "port": port
        }

    config = configparser.ConfigParser()
    config.read_dict(DEFAULTS)

    if os.path.exists(config_path):
        config.read(config_path)

    return config["printer"]


def save_config(config_path=DEFAULT_CONFIG_PATH, host="", port="9100"):
    """Write printer settings to the gremlin config file."""
    config = configparser.ConfigParser()
    config["printer"] = {"host": host, "port": port}

    config_dir = path.dirname(config_path)
    if config_dir and not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

    with open(config_path, "w") as config_file:
        config.write(config_file)
