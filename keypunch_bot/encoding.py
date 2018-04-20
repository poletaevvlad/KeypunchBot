# -*- coding: utf-8 -*-

import math
from collections import namedtuple


CodeRegister = namedtuple("CodeRegister", ["activation"])
CodeSymbol = namedtuple("CodeSymbol", ["code", "register"])


class CharCount:
    def __init__(self):
        self.codes = 0
        self.supported = 0
        self.images = 0


class CharTable:
    def __init__(self, codes):
        self.codes = dict()
        self.substitution = dict()
        self.type = "tape"
        for section in codes:
            entry = codes[section]
            if section == "substitution":
                self.substitution = dict(entry)
            elif section == "type":
                self.type = entry
            else:
                self._add_group(entry)

    def _make_code(self, code):
        if isinstance(code, list):
            res = 0
            for digit in code:
                res |= 1 << digit
            return res
        return code

    def _add_group(self, group):
        if "activation" not in group:
            register = None
        else:
            register = CodeRegister(group["activation"])
        for key in group["codes"]:
            entry = CodeSymbol(self._make_code(group["codes"][key]), register)
            for char in key:
                self.codes[char] = entry

    def _get_code(self, char):
        char = char.upper()
        while char in self.substitution:
            char = self.substitution[char]
        return char, self.codes.get(char)

    def encode(self, text):
        register = None
        for char in text:
            char, code = self._get_code(char)
            if code is None:
                continue
            if code.register is not None and register != code.register:
                register = code.register
                yield None, register.activation
            yield char, code.code

    def count_chars(self, text, per_image):
        result = CharCount()
        register = None
        for char in text:
            char, code = self._get_code(char)
            if code is not None:
                result.supported += 1
                if code.register is not None and register != code.register:
                    register = code.register
                    result.codes += 1
                result.codes += 1
        result.images = math.ceil(result.codes / per_image)
        return result


def digits(value):
    if isinstance(value, int) or isinstance(value, float):
        result = set()
        i = 0
        while value > 0:
            if value & 1 != 0:
                result.add(i)
            value >>= 1
            i += 1
        return result
    elif isinstance(value, CodeSymbol):
        return digits(value.code)
    elif isinstance(value, CodeRegister):
        return digits(value.activation)
    else:
        raise ValueError("Unknown type of " + value)


def split_images(encoded, per_image):
    chars = list(encoded)
    for pos in range(0, len(chars), per_image):
        yield chars[pos: pos + per_image]
