import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("PRINTER_CONNECTION", "network")
os.environ.setdefault("PRINTER_HOST", "192.168.2.118")
os.environ.setdefault("PRINTER_PORT", "9100")

import openapi_server  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


class FakeDevice:
    """Records calls; can be told to fail during printMessage."""

    def __init__(self, fail_on_print=False):
        self.calls = []
        self.fail_on_print = fail_on_print

    def open(self):
        self.calls.append("open")

    def close(self):
        self.calls.append("close")

    def ln(self, n=1):
        self.calls.append("ln")

    def cut(self):
        self.calls.append("cut")

    def textln(self, t=""):
        self.calls.append("textln")

    def set(self, **kw):
        pass


class FakePrinter:
    def __init__(self, fail_on_print=False):
        self.device = FakeDevice(fail_on_print)

    def printMessage(self, m):
        self.device.calls.append("printMessage")
        if self.device.fail_on_print:
            raise OSError("simulated printer failure")

    def cut(self):
        self.device.cut()


@pytest.fixture
def fake_printer(monkeypatch):
    fp = FakePrinter()
    monkeypatch.setattr(openapi_server, "printer", fp)
    return fp


@pytest.fixture
def failing_printer(monkeypatch):
    fp = FakePrinter(fail_on_print=True)
    monkeypatch.setattr(openapi_server, "printer", fp)
    return fp


@pytest.fixture
def client(fake_printer, monkeypatch):
    monkeypatch.setattr(openapi_server, "_test_printer_connection", lambda: True)
    return TestClient(openapi_server.app)
