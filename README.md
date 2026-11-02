# Ticket Gremlin (gremlin)

> Author: [Kyle Beasley](www.github.com/krbeasley)

A small service that prints "work tickets", notes and tasks on a Star Micronics
TSP650 over Ethernet. It runs as a container on your LAN and exposes an OpenAPI
(REST) server that anything on the network — including OpenWebUI tools — can
call to print labels remotely.

> Inspired by CodingWithLewis's YouTube video, *I Fixed My ADHD with a Receipt Printer*.

---

## Deploy (Docker)

```bash
docker compose up -d --build
```

The API is then reachable on the LAN at `http://<host-ip>:7143`
(interactive docs at `/docs`, OpenAPI spec at `/openapi.json`).

Printer connection is configured via environment variables in
`docker-compose.yml`:

```yaml
environment:
  - PRINTER_CONNECTION=network
  - PRINTER_HOST=192.168.2.118   # set a DHCP reservation for the printer's MAC
  - PRINTER_PORT=9100             # raw ESC/POS (JetDirect) port
```

## API

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/print_message` | `{title, message}` | Print a message ticket |
| POST | `/print_task` | `{title, message, due_date}` | Print a task (`MMDDYYYY` or `ASAP`) |
| POST | `/feed_cut` | none | Feed paper and cut |
| POST | `/print_config` | none | Print the config on the printer |
| GET | `/health` | — | `200` healthy, `503` printer unreachable (Uptime Kuma) |

Example:

```bash
curl -X POST http://<host-ip>:7143/print_task \
  -H 'Content-Type: application/json' \
  -d '{"title":"Water the plants","message":"They are thirsty","due_date":"ASAP"}'
```

## OpenWebUI

Add the server as an **OpenAPI tool server** in OpenWebUI
(Settings → Admin → Tools) with URL `http://<host-ip>:7143/openapi.json`.
Each POST endpoint becomes a callable tool (`print_message`, `print_task`,
`feed_cut`, `print_config`).

## Monitoring

Point Uptime Kuma (HTTP monitor) at `http://<host-ip>:7143/health`.
It returns `503` whenever the printer is unreachable, so printer outages
show up as downtime. The container's own healthcheck only checks that the
API process is up and will not restart the container over a printer outage.

---

## Hardware notes

> Your Star Micronics TSP650 does not fully understand the ESC/POS commands this
> application uses. To put your printer in ESC/POS mode, you must flip
> `Dip Switch 1-1` from `On` to `Off`. Turn off your printer first. Unplug it even.

The printer connects over Ethernet and listens on raw TCP port 9100
(JetDirect/AppSocket), which is what `python-escpos`'s `Network` printer uses.

## Character Set Support

| Character Set | Support | Notes |
|---------------|---------|-------|
| **Standard ASCII (32-126)** | ✅ Fully supported | All standard characters including $, !, @, #, %, ^, &, * work correctly |
| **Extended ASCII (127-255)** | ❌ Not supported | Shows as garbage or "?" characters |
| **Unicode Latin accented** | ⚠️ Partial support | Common accented vowels (à, é, ü, ï, etc.) work |
| **Unicode Greek letters** | ❌ Not supported | Shows as garbage or "?" characters |
| **Currency symbols** | ❌ Mostly not supported | €, £, ¥, etc. do not work; use text codes like "EUR", "USD", "kr" instead |
| **Text-based currency codes** | ✅ Supported | "kr", "USD", "EUR", etc. print correctly |

### Recommendations
- Use **standard ASCII characters** (0-127) for maximum compatibility
- For accented characters, test first - many Latin-1 Supplement characters work
- Avoid **extended ASCII** (127-255) - these will not print correctly
- Use **text currency codes** ("EUR", "USD", "kr") instead of symbols (€, $, £) for reliability
