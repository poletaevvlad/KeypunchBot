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

from typing import List, Tuple
from .text_stream import TextStream
from .renderer import bit_set, PUNCHED_CARD_ROWS


def punched_tape_renderer(stream: TextStream, message: List[Tuple[str, int]],
                          show_text: bool):
    for char, code in message:
        encoded = format(code, "05b")
        encoded = f"{encoded[0:3]}.{encoded[3:]}"
        if show_text and char != "":
            encoded += f"  {char}"
        stream.write_line(encoded)


def pad_right(text: str, width: int, char: str = " ") -> str:
    return text + char * (width - len(text))


def punched_card_renderer(stream: TextStream, message: List[Tuple[str, int]],
                          show_text: bool):
    stream.write_line("  " + "_" * 81)
    text = ""
    if show_text:
        text = "".join(" " if x[0] == "" else x[0] for x in message)
    stream.write_line(f" /{pad_right(text, 80)}|")

    for row_bit in PUNCHED_CARD_ROWS:
        row = []
        for _, code in message:
            row.append("x" if bit_set(code, row_bit) else " ")
        stream.write_line(f"| {pad_right(''.join(row), 80)}|")

    stream.write_line(f"|{'_' * 81}|")
