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

from typing import Dict
from ..encodings import EncodingType
from ..persistance import Format

FILE_EXTENSIONS: Dict[Format, str] = {
    Format.PNG: "png",
    Format.JPEG: "jpg",
    Format.TEXT: "txt",
}


def get_filename(medium_type: EncodingType, output_format: Format,
                 page_num: int, total_pages: int) -> str:
    prefix = "card" if medium_type == EncodingType.PUNCHCARD else "tape"
    if total_pages >= 2:
        digits = 1
        while total_pages >= 10:
            digits += 1
            total_pages //= 10
        prefix += f"-{page_num + 1:0{digits}}"
    return f"{prefix}.{FILE_EXTENSIONS[output_format]}"
