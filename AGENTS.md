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


## Setup (Docker deployment)
Build & run: `docker compose up -d --build`
The container runs the FastAPI OpenAPI server on container port 8080, published on the host as 7143 (`"7143:8080"`). API base: `http://<host-ip>:7143` (Swagger docs at `/docs`, spec at `/openapi.json`).

For local hacking only: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, then `python3 -m uvicorn openapi_server:app --host 0.0.0.0 --port 8080`.

## API endpoints
- `POST /print_message` — body `{title, message}`
- `POST /print_task` — body `{title, message, due_date}` (MMDDYYYY or ASAP)
- `POST /feed_cut` — no body
- `POST /print_config` — no body (prints config on the printer)
- `GET /health` — 200 when printer reachable, 503 when degraded (Uptime Kuma target)

## Config
Environment variables only, set in `docker-compose.yml`: `PRINTER_CONNECTION=network`, `PRINTER_HOST`, `PRINTER_PORT=9100`.

## Hardware
Printer must be in ESC/POS mode: flip Dip Switch 1-1 to OFF.
Current connection: network (Ethernet, raw TCP 9100 at 192.168.2.118). Set a DHCP reservation for the printer's MAC on the router so the IP is stable.

## Code Structure
- `openapi_server.py`: FastAPI app — all endpoints + OpenAPI spec
- `Printers/StarPrinter.py`: network-only printer via python-escpos (raw TCP 9100)
- `Printables/Message.py`: base message class, wraps lines at 42 chars
- `Printables/Task.py`: Message + due date
- `config.py`: env-var config loading
- `tests/`: pytest suite (fake printer, no real I/O) — run `.venv/bin/pip install -r requirements-dev.txt && .venv/bin/pytest`

## Dependencies
python-escpos[network], pyusb (import-time requirement of python-escpos), fastapi, uvicorn, requests (container healthcheck)
