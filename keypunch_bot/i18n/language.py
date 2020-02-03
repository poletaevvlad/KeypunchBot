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

from typing import Union, Any, Dict, List, Optional
from abc import ABC, abstractmethod

StringPath = List[Union[str, int]]
StringsGroup = Union[str, List[Any], Dict[str, Any]]


class Language(ABC):
    def __init__(self, fallback: "Language"):
        self.fallback = fallback

    @abstractmethod
    def get_translation(self, path: StringPath) -> Optional[str]:
        pass

    def __getitem__(self, *path: Union[str, int]):
        translation = self.get_translation(list(path))
        if translation is None:
            return self.fallback.__getitem__(*path)
        return translation


# pylint: disable=too-few-public-methods
class NoMessageLanguage(Language):
    def __init__(self):
        super().__init__(None)

    def get_translation(self, path: StringPath) -> Optional[str]:
        return ".".join(str(x) for x in path)


class StringsLanguage(Language):
    def __init__(self, fallback: Language, messages: StringsGroup):
        super().__init__(fallback)
        self.messages = messages

    def get_translation(self, path: StringPath) -> Optional[str]:
        block: StringsGroup = self.messages
        for index in path:
            if isinstance(block, str):
                return None
            if isinstance(block, dict) and isinstance(index, str):
                if index in block:
                    block = block[index]
                else:
                    return None
            elif isinstance(block, list) and isinstance(index, int):
                if 0 <= index < len(block):
                    block = block[index]
                else:
                    return None
        return block if isinstance(block, str) else None
