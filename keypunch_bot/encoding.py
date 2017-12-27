class Encoder:
    __slots__ = ["codes"]
    
    def __init__(self, file: str):
        self.codes = dict()

        with open(file) as f:
            for line in f:
                symbol, code = line.split(" ", 1)
                code = set(ord(a) - ord('0') if '0' <= a <= '9' else 11 + ord(a) - ord('A') for a in code.strip())
                for c in symbol: 
                    self.codes[c] = code
    
    def encode(self, text: str) -> iter:
        for char in text:
            yield self.codes[char] if char in self.codes else {}