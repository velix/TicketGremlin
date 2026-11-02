# TicketGremlin

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.


## Setup
Virtual env + deps: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
Make executable: `chmod +x main.py`
Run: `./main.py` or `.venv/bin/python3 main.py`

User must be in `lp` group: `sudo usermod -aG lp $USER` (requires relogin)

## Commands
Print: `./main.py -t "title" -m "message"`
Due date: `-d MMDDYYYY` or `-d ASAP`
Feed & cut only: `--feed-cut`
Print config: `--print-config`

## Config
Printer connection is configured via env vars (PRINTER_CONNECTION=usb|network, PRINTER_HOST, PRINTER_PORT=9100) or `~/.config/gremlin/gremlin.ini`; env vars win. See `.env.example` for the Docker setup.

## Hardware
Printer must be in ESC/POS mode: flip Dip Switch 1-1 to OFF.
Current connection: network (Ethernet, 192.168.2.118:9100). USB still supported via PRINTER_CONNECTION=usb.

## Code Structure
- `main.py`: CLI entrypoint (argparse)
- `Printers/StarPrinter.py`: Printer abstraction (Usb/Network via python-escpos)
- `Printables/Message.py`: Base message class, handles line wrapping at 42 chars
- `Printables/Task.py`: Message + due date
- `Printables/ImgMessage.py`: Message + image support
- `config.py`: Config file loading/saving
- `detect_script.py`: USB printer endpoint detection

Image syntax in messages: `[[image]]/path/to/image.jpg`

## Dependencies
python-escpos[usb,network], pyusb, Pillow, qrcode, python-barcode
