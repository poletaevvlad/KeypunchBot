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
from typing import Iterable, List, Optional
from PIL import Image
from .stream import Stream


class GraphicsStream(Stream):
    NEWLINE = "\r\n"

    def __init__(self, output_format: str):
        self.output_format = output_format.upper()
        self._images: List[Optional[Image.Image]] = [None]

    def break_page(self):
        self._images.append(None)

    def add_layer(self, layer: Image.Image):
        image = self._images[-1]
        if image is None:
            image = layer
        else:
            image = Image.alpha_composite(image, layer)
        self._images[-1] = image

    def generate_files(self) -> Iterable[BytesIO]:
        for image in self._images:
            if image is None:
                continue

            if self.output_format == "JPEG":
                background = Image.new("RGBA", image.size, (255, 255, 255))
                image = Image.alpha_composite(background, image).convert("RGB")

            io_buffer = BytesIO()
            image.save(io_buffer, self.output_format)
            io_buffer.seek(0)
            yield io_buffer

    def get_files_count(self) -> int:
        return sum(1 if img is not None else 0 for img in self._images)
