# -*- coding: utf-8 -*-
#
# Copyright 2017, 2018, 2020 Vladislav Poletaev
#
# This file is part of KeyunchBot.
#
# KeyunchBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# KeypunchBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KeypunchBot. If not, see <http://www.gnu.org/licenses/>.

import enum
import unicodedata
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from .errors import MessageTooLongError, TooManyPagesError


class EncodingType(enum.Enum):
    PUNCHCARD = "punchcard"
    TAPE = "tape"


@dataclass
class CharacterEntry:
    activation: List[int]
    codes: List[int]

    @property
    def needs_activation(self) -> bool:
        return len(self.activation) != 0


class EncodingResult:
    def __init__(self, per_page: int):
        self._per_page: int = per_page
        self._next_page: bool = True

        self.result: List[List[Tuple[str, int]]] = []
        self.total_length: int = 0
        self.unknown: Set[str] = set()
        self.unknown_count: int = 0

    def add_code(self, char: str, codes: List[int]):
        self.total_length += 1
        for code in codes:
            if self._next_page:
                self.result.append([(char, code)])
                self._next_page = False
            else:
                last = self.result[-1]
                last.append((char, code))
                self._next_page = len(self.result[-1]) == self._per_page
            char = ""

    def add_unknown(self, char: str):
        self.unknown.add(char)
        self.unknown_count += 1

    @property
    def pages_count(self):
        return len(self.result)

    def break_page(self):
        self._next_page = True


def is_linebreak(char: str):
    return unicodedata.category(char) in {"Zl", "Zp", "Cc"}


class CharacterSet:
    def __init__(self, name: str, charset_type: EncodingType):
        self.name: str = name
        self.type: EncodingType = charset_type
        self._chars: Dict[str, CharacterEntry] = {}

    def add_characters(self, characters: Dict[str, List[int]],
                       activation: List[int] = None):
        if activation is None:
            activation = []
        for charset, codes in characters.items():
            entry = CharacterEntry(activation=activation, codes=codes)
            for char in charset:
                self._chars[char] = entry

    def __getitem__(self, char: str) -> CharacterEntry:
        return self._chars[char]

    def __contains__(self, char: str) -> bool:
        return char in self._chars

    def encode(self, message: str, per_page: int, max_length: int = -1,
               max_pages: int = -1, break_with_line: bool = False) -> \
            EncodingResult:
        result = EncodingResult(per_page)
        activation: List[int] = []
        for char in message:
            if break_with_line and is_linebreak(char):
                result.break_page()
            elif char not in self:
                result.add_unknown(char)
            else:
                entry = self[char]
                if entry.needs_activation and activation != entry.activation:
                    result.add_code("", entry.activation)
                    activation = entry.activation
                result.add_code(char, entry.codes)

            if max_length != -1 and result.total_length > max_length:
                raise MessageTooLongError()
            if max_pages != -1 and result.pages_count > max_pages:
                raise TooManyPagesError()
        return result
