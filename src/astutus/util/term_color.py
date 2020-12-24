import colorama
import logging
# import astutus.log

logger = logging.getLogger(__name__)
# Which is better?
logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG)
# logger.setFormatter(astutus.log.standard_formatter)

attribute_map = {
    'red': colorama.Fore.RED,
    'blue': colorama.Fore.BLUE,
}


class AnsiSequenceStack(object):

    def __init__(self):
        self.stack = []

    def push(self, attribute):
        self.stack.append(attribute)
        logger.debug(f"push -  stack: {'|'.join(self.stack)}")
        return attribute_map.get(attribute, f"<<{attribute} not implemented>>")

    def pop(self):
        self.stack = self.stack[:-1]
        logger.debug(f"pop - stack: {'|'.join(self.stack)}")
        sequences = [colorama.Style.RESET_ALL]
        # Re-apply all attributes
        for attribute in self.stack:
            sequences.append(attribute_map.get(attribute, f"<<{attribute} not implemented>>"))
        return "".join(sequences)

    def start(self, attribute):
        self.push(attribute)

    def end(self, attribute):
        logger.debug(f"attibute: {attribute}")
        logger.debug(f"end (before pop) - stack: {'|'.join(self.stack)}")
        assert self.stack[-1] == attribute, f"self.stack[-1] {self.stack[-1]} == {attribute}"
        return self.pop()
