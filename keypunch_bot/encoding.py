from math import ceil
from collections import namedtuple


EncodedCharacter = namedtuple("EncodedCharacter", ["char", "rows"])


class Encoder:
    __slots__ = ["codes"]
    
    columns_count = 80
    
    def __init__(self, codes):
        self.codes = dict()

        for symbols in codes:
            code = codes[symbols]
            for char in symbols:
                self.codes[char] = set(code)
    
    def encode(self, text: str):
        return (EncodedCharacter(c, self.codes[c]) if c in self.codes else {} for c in text)
            
    def char_supported(self, char):
        return char in self.codes
    
    def filter_string(self, string):
        class Counter:
            def __init__(self):
                self.value = 0

            def inc(self):
                self.value +=1 

        counter = Counter()
        def filter_characters(counter):
            previous_supported = False
            for char in string:
                if self.char_supported(char):
                    yield char
                    previous_supported = True
                    counter.inc()
                elif previous_supported:
                    yield " "
                    previous_supported = False
            
        filtered = "".join(filter_characters(counter))
        return filtered.strip(), counter.value

    def split_by_card(self, text):
        string = ""
        for char in text:
            if char == "\n":
                if len(string) > 0:
                    yield string
                    string = ""
            string += char
            if len(string) >= self.columns_count:
                yield string
                string = ""

    def num_cards(self, text):
        return ceil(len(text) / self.columns_count)