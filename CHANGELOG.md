# Changelog

# 0.6.0
- Support was added for connecting to the printer over Ethernet (Network) using the `--host` and `--port` flags.
- A config file (`~/.config/gremlin/gremlin.ini`) was added for storing the printer host/port. CLI flags take priority.
- `--print-config` now also prints the connection type (usb/network) and config file path.

# 0.5.1
- A bug was fixed where a long string without white-spaces (like links) could trigger the infinite-loop protection before the string could be broken.

# 0.5.0
- Image support and a companion 'ImgMessage' class (WIP) were added for sending simple photos.
- Support was added for trimming incoming messages only on 'breakable' characters.

# 0.3.0
- Support was added for due-dates and a companion "Task" class as a new Message type.

# 0.2.0
- The Message class was created for the printer.

# 0.1.0
- It was made to work! The 20 year old printer lives!
