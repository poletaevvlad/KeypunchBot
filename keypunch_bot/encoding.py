from yaml import load
class Encoder:
    __slots__ = ["codes"]
    
    def __init__(self, codes):
        self.codes = dict()

        for symbols in codes:
            code = codes[symbols]
            for char in symbols:
                self.codes[char] = set(code)
    
    def encode(self, text: str):
        for i in range(0, len(text), 80):
            yield (self.codes[c] if c in self.codes else {} for c in text[i: i + 80])