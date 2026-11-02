from escpos.printer import Network
from datetime import datetime
from Printables.Message import Message
from Printables.Task import Task

MAX_LINE_LEN = 42
DEFAULT_PORT = 9100


class StarPrinter:
    """Network (Ethernet) connection to the Star printer over raw TCP 9100."""

    def __init__(self, host, port=DEFAULT_PORT):
        self.connection = "network"
        # timeout bounds how long a hung printer can block a print job
        self.device = Network(host, port, timeout=10, profile="TSP600")
        self.max_line_len = 42

    def _printHorizontalLine(self, char='-', length=42):
        """Print a horizontal line of specified character and length"""
        self.device.textln(char * length)

    def _printTitleBorder(self, title, border_char='='):
        """Print title with border above and below"""
        self.device.set(align='center')
        self._printHorizontalLine(border_char, self.max_line_len)
        self.device.set(bold=True, align='center')
        self.device.textln(title)
        self.device.set(bold=False, align='center')
        self._printHorizontalLine(border_char, self.max_line_len)
        self.device.set(align='left')

    def printMessage(self, message):
        self.printNow()
        self.device.ln()
        
        # Check if this is a Task (has due_date attribute)
        is_task = isinstance(message, Task)
        
        # Print subject with border if it exists
        if message.subject is not None:
            # For border printing, we want the subject as a single line
            # Join multi-line subjects with spaces
            title = ' '.join(message.subject)
            self._printTitleBorder(title, '=')
            self.device.ln()
        
        # Print body
        for line in message.body:
            if str(line).startswith("[[image]]"):
                filepath = line.replace("[[image]]", "")
                self.device.image(filepath)
            else:
                self.writeLine(line)
        
        # Print due date for tasks
        if is_task:
            self.device.ln()
            due_text = "DUE: "
            if str(message.due_date).upper() == "ASAP":
                due_text += "ASAP"
            else:
                due_date = datetime.strptime(str(message.due_date), "%m%d%Y")
                due_text += due_date.strftime("%m/%d/%Y")
            
            self.device.set(bold=True, align='center')
            self.device.textln(due_text)
            self.device.set(bold=False, align='left')
        
        # End of ticket marker with padding
        self.device.ln()
        self.device.set(align='center')
        self._printHorizontalLine('-', self.max_line_len)
        self.device.set(align='left')
        self.device.ln()

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
        self.device.set(align='right')
        self.device.textln(now)
        self.device.set(align='left')

    def printDueDate(self, dueDate):
        if str(dueDate).upper() != "ASAP":
            now = datetime.strptime(dueDate, "%m%d%Y")
            self.writeLine("Due: " + now.strftime("%m/%d/%Y"))
        else:
            self.writeLine("Due: ASAP")
            self.device.ln()
