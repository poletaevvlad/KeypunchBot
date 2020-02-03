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

from keypunch_bot.rendering.text_stream import TextStream


def test_writing_text():
    stream = TextStream()
    stream.write_line("hello")
    stream.write_line("world")
    stream.break_page()
    stream.write_line("second page")

    buffers = list(stream.generate_files())
    assert len(buffers) == 1
    assert buffers[0].getvalue() == b"hello\r\nworld\r\n\r\nsecond page\r\n"
