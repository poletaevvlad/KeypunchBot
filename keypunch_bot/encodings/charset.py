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
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass


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
        self.unknown: Set[str] = set()
        self.unknown_count: int = 0

    def add_code(self, char: str, codes: List[int]):
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

    def encode(self, message: str, per_page: int) -> EncodingResult:
        result = EncodingResult(per_page)
        for char in message:
            try:
                entry = self[char]
                result.add_code(char, entry.codes)
            except KeyError:
                result.add_unknown(char)
        return result
