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

from io import BytesIO
from typing import Iterable
from .stream import Stream


class TextStream(Stream):
    NEWLINE = "\r\n"

    def __init__(self):
        self._stream = BytesIO()

    def break_page(self):
        self.write_line("")

    def write_line(self, line: str):
        chunk = (line + TextStream.NEWLINE).encode("utf-8")
        self._stream.write(chunk)

    def generate_files(self) -> Iterable[BytesIO]:
        self._stream.seek(0)
        yield self._stream
