import logging
import re

import astutus.util.util_impl

logger = logging.getLogger(__name__)


class AnsiSequenceStack(object):

    RESET_ALL = '\x1b[0m'

    def __init__(self):
        self.stack = []

    @staticmethod
    def hash_hex_to_escape_sequence(hash_hex: str) -> str:
        # Parse the attribute that might be something like #00ffff into an ANSI escape sequence.
        # Need to translate it to something like:  'orange': '\x1b[38;2;255;165;0m',
        pattern = r"^#([a-f,0-9]{2})([a-f,0-9]{2})([a-f,0-9]{2})$"
        matches = re.match(pattern, hash_hex, re.IGNORECASE)
        assert matches, (pattern, hash_hex)
        rr = matches.group(1)
        gg = matches.group(2)
        bb = matches.group(3)
        red = int(rr, 16)
        green = int(gg, 16)
        blue = int(bb, 16)
        escape_sequence = f'\x1b[38;2;{red};{green};{blue}m'
        return escape_sequence

    @staticmethod
    def attribute_to_escape_sequence(attribute):
        if attribute.startswith("#"):
            return AnsiSequenceStack.hash_hex_to_escape_sequence(attribute)
        else:
            hash_hex = astutus.util.util_impl.convert_color_for_html_input_type_color(attribute)
            return AnsiSequenceStack.hash_hex_to_escape_sequence(hash_hex)

    def push(self, attribute):
        escape_sequence = self.attribute_to_escape_sequence(attribute)
        self.stack.append(escape_sequence)
        logger.debug(f"push -  stack: {'|'.join(self.stack)}")
        return escape_sequence

    def pop(self):
        self.stack = self.stack[:-1]
        logger.debug(f"pop - stack: {'|'.join(self.stack)}")
        sequences = [self.RESET_ALL]
        # Re-apply all attributes
        for attribute in self.stack:
            sequences.append(attribute)
        return "".join(sequences)

    def start(self, attribute):
        self.push(attribute)

    def end(self, attribute):
        logger.debug(f"attibute: {attribute}")
        escape_sequence = self.attribute_to_escape_sequence(attribute)
        logger.debug(f"end (before pop) - stack: {'|'.join(self.stack)}")
        assert self.stack[-1] == escape_sequence, f"self.stack[-1] {self.stack[-1]} == {escape_sequence}"
        return self.pop()
