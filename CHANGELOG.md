# Changelog

# 0.6.0
- Added support for connecting to the printer over Ethernet (Network) using the `--host` and `--port` flags.
- Added a config file (`~/.config/gremlin/gremlin.ini`) for storing the printer host/port, with CLI flags taking priority.
- `--print-config` now also prints the connection type (usb/network) and config file path.

# 0.5.1
- Fixed a bug where looping through a long string without white-spaces (like links) would trigger the infinite-loop protection before the string could be broken.

# 0.5.0
- Added image support and a companion 'ImgMessage' class (WIP) for sending simple photos.
- Added support for trimming incoming messages down only on 'breakable' characters.

# 0.3.0
- Added support for due-dates and a companion "Task" class as a new Message type.

# 0.2.0
- Message class created for printer

# 0.1.0
- Made it work! The 20 year old printer lives!
