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

import re
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


@dataclass
class EncodingParams:
    per_page: int
    max_length: int = -1
    max_pages: int = -1
    break_with_line: bool = False

    @property
    def has_max_length(self):
        return self.max_length >= 0

    @property
    def has_max_pages(self):
        return self.max_pages >= 0


class CharacterSet:
    def __init__(self, name: str, charset_type: EncodingType,
                 substitutions: Dict[str, str] = None):
        self.name: str = name
        self.type: EncodingType = charset_type
        self._chars: Dict[str, CharacterEntry] = {}
        if substitutions is None:
            substitutions = {}
        self.substitutions: Dict[str, str] = substitutions

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

    def __iter__(self):
        return iter(self._chars)

    def fix_string(self, message: str) -> str:
        message = message.strip()
        for char, substitition in self.substitutions.items():
            message = message.replace(char, substitition)
        message = re.sub(r"\s*[\n\r]+\s*", "\n", message)
        message = re.sub(r"[^\S\n\r]+", " ", message)
        return message

    def encode(self, message: str, params: EncodingParams) -> \
            EncodingResult:
        result = EncodingResult(params.per_page)
        activation: List[int] = []
        for char in message:
            if params.break_with_line and is_linebreak(char):
                result.break_page()
            elif char not in self:
                result.add_unknown(char)
            else:
                entry = self[char]
                if entry.needs_activation and activation != entry.activation:
                    result.add_code("", entry.activation)
                    activation = entry.activation
                result.add_code(char, entry.codes)

            if params.has_max_length and \
               result.total_length > params.max_length:
                raise MessageTooLongError()
            if params.has_max_pages and result.pages_count > params.max_pages:
                raise TooManyPagesError()
        return result
