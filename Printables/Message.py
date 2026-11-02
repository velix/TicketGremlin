def getNChars(text, n):
    """Returns the first n characters from a line of text"""
    return text[:n]


class Message:
    def __init__(self, subject=None, body="", max_len=42):
        self.MAX_LEN = max_len
        self.setSubject(subject)
        self.setBody(body)

    def setSubject(self, new_subject):
        self.subject = self.createTextArray(new_subject)

    def createTextArray(self, text):
        # Split the text string into a tmp array based on new lines
        tmp_arr = self.parseNewLines(text)
        text_arr = []
        # Loop through the lines and push them to the text_arr
        for line in tmp_arr:
            # Image lines should not be wrapped, preserve as-is
            if line.startswith("[[image]]"):
                text_arr.append(line.strip())
                continue
            # Continue splitting and adding lines until you're left with
            # something that'll fit on one line.
            while len(line) > self.MAX_LEN:
                nChars = getNChars(line, self.MAX_LEN)
                # Reduce nChars until the last character is a ' '
                nCount = 0
                while nChars[-1] != ' ' and nChars[-1] != '-':
                    nChars = getNChars(line, self.MAX_LEN - nCount)
                    nCount += 1

                    # Check we're not stuck in a loop
                    if nCount > 4 * self.MAX_LEN:
                        raise ValueError("Could not wrap line within 42 chars")

                # Remove nChars from the line
                line = line.replace(nChars, "")
                text_arr.append(nChars.strip())
            # Make sure to add whatever's left
            text_arr.append(line.strip())
        # Strip the last line if it's blank
        if text_arr[-1] == "":
            text_arr.pop(-1)
        # Finally return the text array
        return text_arr

    def setBody(self, body):
        try:
            self.body = self.createTextArray(body)
        except (IndexError, ValueError) as e:
            raise ValueError(f"Body could not be formatted: {e}")

    def parseNewLines(self, text):
        ret = []
        lines = str(text).replace("\r\n", "\n").split("\n")
        for line in lines:
            ret.append(line)
            ret.append("")

        return ret

    def render(self):
        ret = []

        if self.subject is not None:
            for line in self.subject:
                ret.append(line)
            ret.append("")

        for line in self.body:
            ret.append(line)

        return ret
