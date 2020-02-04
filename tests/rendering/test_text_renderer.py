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

from pathlib import Path
import string
import itertools
import pytest
from keypunch_bot.rendering import TextStream, punched_tape_renderer, \
    punched_card_renderer

TAPE = [("", 0x1f), ("h", 0x14), ("e", 0x01), ("l", 0x12), ("l", 0x12),
        ("o", 0x18)]
CARD = [
    ("-", 0),
    *zip(string.ascii_lowercase, (1 << i for i in range(12))),
    ("+", 0b111111111111),
    *zip(itertools.cycle(["", " "]), (1 << i for i in range(12)))
]


def test_tape_renderer_with_text():
    stream = TextStream()
    punched_tape_renderer(stream, TAPE, True)

    expected = (b"111.11\r\n"
                b"101.00  h\r\n"
                b"000.01  e\r\n"
                b"100.10  l\r\n"
                b"100.10  l\r\n"
                b"110.00  o\r\n")
    result = next(stream.generate_files()).getvalue()
    assert expected == result


def test_tape_renderer_without_text():
    stream = TextStream()
    punched_tape_renderer(stream, TAPE, False)

    expected = (b"111.11\r\n"
                b"101.00\r\n"
                b"000.01\r\n"
                b"100.10\r\n"
                b"100.10\r\n"
                b"110.00\r\n")
    result = next(stream.generate_files()).getvalue()
    assert expected == result


@pytest.mark.parametrize("show_text, file", [
    (True, "card_text.txt"), (False, "card_no_text.txt")
])
def test_punchcard_renderer_with_text(show_text: bool, file: str):
    stream = TextStream()
    punched_card_renderer(stream, CARD, show_text)
    result_str = next(stream.generate_files()).getvalue().decode("utf-8")
    print(result_str)
    expected_file = Path(__file__).parents[0] / "assets" / file
    assert result_str.splitlines() == expected_file.read_text().splitlines()
