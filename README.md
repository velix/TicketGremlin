# Ticket Gremlin (gremlin)

> Author: [Kyle Beasley](www.github.com/krbeasley)

A small service that prints "work tickets", notes and tasks on a Star Micronics
TSP650 over Ethernet. It runs as a container on the LAN. It exposes an OpenAPI
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
  - PRINTER_HOST=printer.local   # set a DHCP reservation for the printer's MAC
  - PRINTER_PORT=9100             # raw ESC/POS (JetDirect) port
```

## API

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/print_message` | `{title, message}` | A message ticket is printed |
| POST | `/print_task` | `{title, message, due_date}` | A task is printed (`MMDDYYYY` or `ASAP`) |
| POST | `/feed_cut` | none | Paper is fed and cut |
| POST | `/print_config` | none | The config is printed on the printer |
| GET | `/health` | — | `200` healthy, `503` printer unreachable (Uptime Kuma) |

Example:

```bash
curl -X POST http://<host-ip>:7143/print_task \
  -H 'Content-Type: application/json' \
  -d '{"title":"Water the plants","message":"They are thirsty","due_date":"ASAP"}'
```

## OpenWebUI

The server is added as an **OpenAPI tool server** in OpenWebUI
(Settings → Admin → Tools) with URL `http://<host-ip>:7143/openapi.json`.
Each POST endpoint becomes a callable tool (`print_message`, `print_task`,
`feed_cut`, `print_config`).

## Monitoring

Uptime Kuma (HTTP monitor) is pointed at `http://<host-ip>:7143/health`.
The endpoint returns `503` whenever the printer is unreachable. Printer
outages appear as downtime. The container's own healthcheck only checks
that the API process is up. The container is not restarted over a printer
outage.

---

## Hardware notes

> The Star Micronics TSP650 does not fully understand the ESC/POS commands this
> application uses. ESC/POS mode must be enabled on the printer by flipping
> `Dip Switch 1-1` from `On` to `Off`. The printer is switched off first. It is
> unplugged too.

The printer connects over Ethernet and listens on raw TCP port 9100
(JetDirect/AppSocket), which is what `python-escpos`'s `Network` printer uses.

## Character Set Support

| Character Set | Support | Notes |
|---------------|---------|-------|
| **Standard ASCII (32-126)** | ✅ Fully supported | All standard characters including $, !, @, #, %, ^, &, * work correctly |
| **Extended ASCII (127-255)** | ❌ Not supported | Shows as garbage or "?" characters |
| **Unicode Latin accented** | ⚠️ Partial support | Common accented vowels (à, é, ü, ï, etc.) work |
| **Unicode Greek letters** | ❌ Not supported | Shows as garbage or "?" characters |
| **Currency symbols** | ❌ Mostly not supported | €, £, ¥, etc. do not work. Use text codes like "EUR", "USD", "kr" instead |
| **Text-based currency codes** | ✅ Supported | "kr", "USD", "EUR", etc. print correctly |

### Recommendations
- Standard ASCII characters (0-127) are used for maximum compatibility
- Accented characters are tested first. Many Latin-1 Supplement characters work
- Extended ASCII (127-255) is avoided. These characters do not print correctly
- Text currency codes ("EUR", "USD", "kr") are used instead of symbols (€, $, £) for reliability
