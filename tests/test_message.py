"""Unit tests for Printables.Message text wrapping.

Fixtures use standard ASCII (32-126) only, per the verified Character Set
Support table in README.md.
"""
import pytest

from Printables.Message import Message


def test_newlines_split_into_separate_lines():
    m = Message(body="line1\nline2")
    assert "line1" in m.body
    assert "line2" in m.body
    assert all("\n" not in line for line in m.body)


def test_crlf_handled():
    m = Message(body="a\r\nb")
    assert "a" in m.body and "b" in m.body


def test_long_line_wraps_at_42_chars():
    text = "word " * 30  # 150 chars of ASCII
    m = Message(body=text)
    assert len(m.body) > 1
    assert all(len(line) <= 42 for line in m.body)


def test_set_body_error_raises_value_error(monkeypatch):
    orig = Message.createTextArray

    def boom(self, text):
        if text is None:  # subject path uses the real implementation
            return orig(self, text)
        raise IndexError("no lines")

    monkeypatch.setattr(Message, "createTextArray", boom)
    with pytest.raises(ValueError, match="could not be formatted"):
        Message(body="x")
