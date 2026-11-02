#!/usr/bin/env python3
"""Test script to determine supported character sets for Star Micronics printer."""

from Printers.StarPrinter import StarPrinter
import sys

def print_test_page(title, chars):
    """Print a test page with the given characters."""
    printer = StarPrinter()
    printer.device.open()
    
    # Print header
    printer.device.textln(f"=== {title} ===")
    printer.device.textln("")
    
    # Print characters in a readable format
    for i, c in enumerate(chars):
        # Print 10 chars per line
        if i > 0 and i % 10 == 0:
            printer.device.textln("")
        printer.device.text(c)
    
    printer.device.textln("")
    printer.device.textln("")
    printer.cut()
    printer.device.close()
    print(f"Printed: {title}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_charset.py <test_name>")
        print("Available tests: ascii, extended, unicode")
        sys.exit(1)
    
    test_name = sys.argv[1].lower()
    
    if test_name == "ascii":
        # Basic ASCII characters (32-126 are printable)
        chars = [chr(i) for i in range(32, 127)]
        print_test_page("ASCII Characters (32-126)", chars)
    elif test_name == "extended":
        # Extended ASCII (127-255)
        chars = [chr(i) for i in range(127, 256)]
        print_test_page("Extended ASCII (127-255)", chars)
    elif test_name == "unicode":
        # Common Unicode characters
        chars = [
            'à', 'á', 'â', 'ã', 'ä', 'å', 'æ', 'ç', 'è', 'é',
            'ê', 'ë', 'ì', 'í', 'î', 'ï', 'ð', 'ñ', 'ò', 'ó',
            'ô', 'õ', 'ö', 'ø', 'ù', 'ú', 'û', 'ü', 'ý', 'þ',
            'ÿ', 'Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι',
            'Κ', 'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ',
            'Υ', 'Φ', 'Χ', 'Ψ', 'Ω', 'α', 'β', 'γ', 'δ', 'ε'
        ]
        print_test_page("Unicode Characters", chars)
    elif test_name == "symbols":
        # Common symbols
        chars = [
            '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
            '_', '+', '=', '{', '}', '[', ']', '|', '\\', ':', ';',
            '"', '\'', '<', '>', ',', '.', '?', '/', '~', '`',
            '€', '£', '¥', '¢', '©', '®', '™', '°', '±', 'µ'
        ]
        print_test_page("Special Symbols", chars)
    else:
        print(f"Unknown test: {test_name}")
        sys.exit(1)
