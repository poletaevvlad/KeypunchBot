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

from keypunch_bot.rendering import TextStream, punched_tape_renderer

tape = [("", 0x1f), ("h", 0x14), ("e", 0x01), ("l", 0x12), ("l", 0x12),
        ("o", 0x18)]


def test_tape_renderer_with_text():
    stream = TextStream()
    punched_tape_renderer(stream, tape, True)

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
    punched_tape_renderer(stream, tape, False)

    expected = (b"111.11\r\n"
                b"101.00\r\n"
                b"000.01\r\n"
                b"100.10\r\n"
                b"100.10\r\n"
                b"110.00\r\n")
    result = next(stream.generate_files()).getvalue()
    assert expected == result
