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

from typing import Dict, Iterator, ItemsView
from pathlib import Path
import yaml
from .charset import CharacterSet
from .loader import parse_charset


class CharacterSetsRepository:
    def __init__(self, charsets: Dict[str, CharacterSet]):
        self._charsets: Dict[str, CharacterSet] = charsets

    @staticmethod
    def load(path: Path) -> "CharacterSetsRepository":
        results = {}
        for file_path in path.iterdir():
            if file_path.suffix != ".yaml":
                continue
            with file_path.open() as file:
                spec = yaml.load(file, yaml.SafeLoader)
            charset_id, charset = parse_charset(spec)
            results[charset_id] = charset

        return CharacterSetsRepository(results)

    def __contains__(self, charset_id: str) -> bool:
        return charset_id in self._charsets

    def __getitem__(self, charset_id: str) -> CharacterSet:
        return self._charsets[charset_id]

    def __iter__(self) -> Iterator[str]:
        return iter(self._charsets)

    def items(self) -> ItemsView[str, CharacterSet]:
        return self._charsets.items()
