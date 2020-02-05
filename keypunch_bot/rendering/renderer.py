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

from typing import TypeVar, List, Tuple
try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol
from .stream import Stream

TStream = TypeVar("TStream", bound=Stream, contravariant=True)


# pylint: disable=too-few-public-methods
class Renderer(Protocol[TStream]):
    def __call__(self, stream: TStream, message: List[Tuple[str, int]],
                 show_text: bool):
        pass


def bit_set(number: int, bit: int) -> bool:
    return number & (1 << bit) != 0


PUNCHED_CARD_ROWS = [11, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
