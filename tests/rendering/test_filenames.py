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


import pytest
from keypunch_bot.encodings import EncodingType
from keypunch_bot.persistance import Format
from keypunch_bot.rendering import get_filename


@pytest.mark.parametrize("medium, output_format, page, total_pages, result", [
    (EncodingType.PUNCHCARD, Format.PNG, 0, 1, "card.png"),
    (EncodingType.TAPE, Format.TEXT, 0, 1, "tape.txt"),
    (EncodingType.TAPE, Format.TEXT, 0, 2, "tape-1.txt"),
    (EncodingType.PUNCHCARD, Format.JPEG, 3, 8, "card-4.jpg"),
    (EncodingType.PUNCHCARD, Format.PNG, 3, 10, "card-04.png"),
    (EncodingType.PUNCHCARD, Format.PNG, 3, 999, "card-004.png"),
    (EncodingType.TAPE, Format.PNG, 3, 1000, "tape-0004.png"),
    (EncodingType.PUNCHCARD, Format.PNG, 1234, 10000, "card-01235.png"),
])
def test_filenmae(medium: EncodingType, output_format: Format,
                  page: int, total_pages: int, result: str):
    assert get_filename(medium, output_format, page, total_pages) == result
