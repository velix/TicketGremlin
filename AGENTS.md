# TicketGremlin

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, judgment is used.

## 1. Think Before Coding

**Nothing is assumed. Confusion is not hidden. Tradeoffs are surfaced.**

Before implementing:
- Assumptions are stated explicitly. When uncertain, a question is asked.
- Multiple interpretations are presented. None is picked silently.
- A simpler approach is named when one exists. Pushback is given when warranted.
- Work stops when something is unclear. The confusion is named. A question is asked.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If 200 lines are written where 50 could suffice, the code is rewritten.

The question: "Would a senior engineer say this is overcomplicated?" If yes, the code is simplified.

## 3. Surgical Changes

**Only what must be touched is touched. Only one's own mess is cleaned up.**

When editing existing code:
- Adjacent code, comments, and formatting are not "improved".
- Code that is not broken is not refactored.
- Existing style is matched, even when another style would be chosen.
- Unrelated dead code is mentioned when noticed. It is not deleted.

When changes create orphans:
- Imports, variables, and functions made unused by the changes are removed.
- Pre-existing dead code is not removed unless requested.

The test: Every changed line is traced directly to the request.

## 4. Goal-Driven Execution

**Success criteria are defined. The loop runs until verification.**

Tasks are transformed into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, a brief plan is stated:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria allow independent loops. Weak criteria ("make it work") require constant clarification.

## Setup (Docker deployment)

The container is built and started with: `docker compose up -d --build`

The container runs the FastAPI OpenAPI server on container port 8080, published on the host as 7143 (`"7143:8080"`).
API base: `http://<host-ip>:7143` (Swagger docs at `/docs`, spec at `/openapi.json`).

For local hacking only, the virtual environment is created with `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
The server is then started with `python3 -m uvicorn openapi_server:app --host 0.0.0.0 --port 8080`.

## API endpoints
- `POST /print_message` — body `{title, message}`
- `POST /print_task` — body `{title, message, due_date}` (MMDDYYYY or ASAP)
- `POST /feed_cut` — no body
- `POST /print_config` — no body (prints config on the printer)
- `GET /health` — 200 when printer reachable, 503 when degraded (Uptime Kuma target)

## Config
Environment variables only, set in `docker-compose.yml`: `PRINTER_CONNECTION=network`, `PRINTER_HOST`, `PRINTER_PORT=9100`.

## Hardware
The printer must be in ESC/POS mode. Dip Switch 1-1 is flipped to OFF.
Current connection: network (Ethernet, raw TCP 9100 at printer.local).
A DHCP reservation for the printer's MAC is set on the router so the IP is stable.

## Code Structure
- `openapi_server.py`: FastAPI app — all endpoints + OpenAPI spec
- `Printers/StarPrinter.py`: network-only printer via python-escpos (raw TCP 9100)
- `Printables/Message.py`: base message class, wraps lines at 42 chars
- `Printables/Task.py`: Message + due date
- `config.py`: env-var config loading
- `tests/`: pytest suite (fake printer, no real I/O) — the suite is run with `.venv/bin/pip install -r requirements-dev.txt && .venv/bin/pytest`

## Dependencies
python-escpos[network], pyusb (import-time requirement of python-escpos), fastapi, uvicorn, requests (container healthcheck)
