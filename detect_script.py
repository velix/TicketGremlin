import usb.core

# Query the physical Star printer
dev = usb.core.find(idVendor=0x0519, idProduct=0x0001)

if dev is None:
    print("Printer completely unplugged or missing driver.")
else:
    print("--- Detected Endpoints ---")
    for cfg in dev:
        for intf in cfg:
            for ep in intf:
                # Bit 7 determines direction: 0 = Out (Write), 1 = In (Read)
                direction = "IN (Read)" if (ep.bEndpointAddress & 0x80) else "OUT (Write)"
                print(f"Address: {hex(ep.bEndpointAddress)} | Direction: {direction}")

