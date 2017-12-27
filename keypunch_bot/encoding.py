class Encoder:
    __slots__ = ["codes"]
    
    def __init__(self, codes):
        self.codes = dict()

        for symbols in codes:
            code = codes[symbols]
            for char in symbols:
                self.codes[char] = code
    
    def encode(self, text: str) -> iter:
        for char in text:
            yield self.codes[char] if char in self.codes else {}