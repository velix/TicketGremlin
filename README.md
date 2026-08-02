# Ticket Gremlin (gremlin)

> Author: [Kyle Beasley](www.github.com/krbeasely)

A small python program that prints "Work Tickets", notes, tasks, etc on a Star Micronics TSP650. I mean the OG version released sometime between 1995 and 2005. Not the TSP650ii. However the program should still work. This is also only tested on Linux (Debian 13). Other operating systems (and other flavors of linux) might find this program unusable.

> Inspired by CodingWithLewis's YouTube Video, *I Fixed My ADHD with a Receipt Printer*. I watched the first 23 seconds, said "That's genius I need to do this" and clicked off to Ebay. Thank you for the inspiration Lewis! I've since gone back and finished the video. <3
>
> [Full Vid Here](https://www.youtube.com/watch?v=xg45b8UXoZI)

---

### Coming Features:

- Auto-Configuration: The first time gremlin runs, it will ask you to create a configuration file to store some basic information like your printer type (for when more printers are supported) and (possibly) users that will be sending tickets. 

---

## Installation

1. Clone the repo wherever you keep your applications.

```$ git clone git@github.com:krbeasley/TicketGremlin && cd TicketGremlin```

2. Create a Virtual Environment for gremlin to live in. (You don't want him escaping)

```python3 -m venv .venv```

3. Install the dependencies.

```$ pip install -r requirements.txt```

> The requirements.txt file includes both the "Usb" and "Network" portions of the escpos package, so gremlin can talk to your printer over USB or Ethernet. Serial and Bluetooth aren't supported (yet).

4. \[Optional\] Create an alias for gremlin.
    - Make gremlin's `main.py` file executable. ```chmod +x main.py```
    - Using your editor of choice, modify your ```~/.bash_aliases``` file.
    - Append the following:
    ```
    # ~/.bash_aliases : Assuming you installed to ~/Apps
    #  
    # Setup gremlin
    gremlinConfigDir="$HOME/Apps/TicketGremlin"
    alias gremlin="$gremlinConfigDir/.venv/bin/python3 $gremlinConfigDir/gremlin"
    ```
    - Run ```source ~/.bashrc``` and ```gremlin``` becomes a globally available resource.

5. \[Not Optional\] Ensure you have permission to use the printer.

    - Enter ```cat /etc/group | grep $USER``` into your terminal to view all of the groups you are a part of.
    - If you do not see your username included in the "lp" group, add yourself (assuming you have sudo permission) by entering ```sudo usermod -aG lp <your_username>```. The next time you log into your shell, you will have the necessary permissions.

6. Give it a shot! Run ```gremlin --print-config``` to see what happens.

## Connecting over Ethernet (Network)

By default gremlin looks for the printer on USB. To connect to a network-connected printer (via its Ethernet port) you can pass the printer's IP address with the `--host` flag:

```
gremlin -t "Network test" -m "Hello from ethernet!" --host 192.168.1.50
```

By default gremlin uses port `9100`, which is the standard printer port for ESC/POS over Ethernet. If your printer listens elsewhere, pass `--port`:

```
gremlin -m "..." --host 192.168.1.50 --port 9101
```

### Config file (optional)

Rather than typing `--host` every time, you can store it in a config file. Create `~/.config/gremlin/gremlin.ini`:

```
[printer]
host = 192.168.1.50
port = 9100
```

Now every gremlin command will use that printer automatically. Any flags you pass on the command line (like `--host` or `--port`) take priority over the config file. To use a different config file, pass `--config /path/to/gremlin.ini`.

### Troubleshooting Ethernet connections

- Run `gremlin --print-config` (with your `--host`) to confirm gremlin shows `Connection: network` instead of `Connection: usb`.
- Double check the printer's IP address. Most thermal printers can print their own network config via a self-test/label button on the back.
- Ensure the printer and your machine are on the same network, and that port `9100` isn't blocked by a firewall.
- If you don't pass `--host` (and no `host` is in your config file), gremlin falls back to USB — so a missing flag looks exactly like an unplugged USB printer.

## Basic Usage

Printing tasks is extremely simple. Simply provide gremlin with a `-m` message and he'll print it for you. Optionally, you can include a `-t` title.

```
gremlin -t "This is my task!"\
-m "There are many more like it but this one is mine!"
```

Prints the ticket:

```

2025-08-19 -- 13:10:30
This is my task!

There are many more like it but this one 
is mine!

```

To pass a due date onto a task, specify it with the ```-d``` flag. Any date can be passed as long as it's in the ```MMDDYYYY``` format. (I'm American, okay?). You may also pass along ```ASAP``` to emphasize the urgency of this task.

```
gremlin -m "I have to have this done soon." -d "04202025"
```

Prints:

```

2025-08-19 -- 13:10:30

Due: 04/20/2025

I have to have this done soon.

```

New lines are as simple as including `\n` in the title or the body of the task.

Images can be included by starting a new line with `[[image]]` followed by the full path to the image you with to print.

```\n[[image]]/path/to/image.jpg\n```

## Troubleshooting

### "My printer kinda-sorta prints right? And the cut function isn't working..."

> Your Star Micronics TSP650 does not fully understand the ESC/POS commands this application uses. To put your printer in ESCPOS mode, you must flip `Dip Switch 1-1` from `On` to `Off`. Turn off your printer first. Unplug it even.

1. Flip your printer.
2. Using a Philips head screwdriver, unscrew the Dip Switch cover plate from the base of the printer.
3. Locate the wider of the two Dip Switch sets. Find the switch labeled "1" (furthest left) and flip it off.
4. Reassemble your printer and turn it back on.
5. Try to run it again.

---

## Character Set Support

The Star Micronics TSP650 printer supports the following character sets:

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

---

