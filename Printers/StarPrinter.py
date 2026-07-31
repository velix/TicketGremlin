from escpos.printer import Usb, Network
from datetime import datetime
from Printables import Message

MAX_LINE_LEN = 42
DEFAULT_PORT = 9100


class StarPrinter:
    def __init__(self, host=None, port=DEFAULT_PORT):
        self.connection = "usb" if host is None else "network"
        if host is None:
            self.device = Usb(0x0519, 0x0001, 0, profile="TSP600", out_ep=0x03)
        else:
            self.device = Network(host, port, profile="TSP600")
        self.max_line_len = 42

    def printMessage(self, message):
        self.printNow()
        for line in message.render():
            if str(line).startswith("[[image]]"):
                # draw an image
                filepath = line.replace("[[image]]", "")
                self.device.image(filepath)
            else:
                self.writeLine(line)

    def writeLine(self, line):
        self.device.textln(line)

    def writeBarcode(self, data, format="CODE39"):
        self.device.barcode(data, format, width=3)

    def writeQR(self, data):
        self.device.qr(data, size=5)

    def cut(self):
        self.device.cut()

    def printNow(self):
        now = datetime.today().strftime("%H:%M:%S -- %m/%d/%Y")
        self.writeLine(now)

    def printDueDate(self, dueDate):
        if str(dueDate).upper() != "ASAP":
            now = datetime.strptime(dueDate, "%m%d%Y")
            self.writeLine("Due: " + now.strftime("%m/%d/%Y"))
        else:
            self.writeLine("Due: ASAP")
            self.device.ln()
