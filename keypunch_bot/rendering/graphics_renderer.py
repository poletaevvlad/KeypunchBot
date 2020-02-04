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

from typing import List, Tuple, Dict
from pathlib import Path
import itertools
from PIL import Image
from .graphics_stream import GraphicsStream
from .renderer import PUNCHED_CARD_ROWS, bit_set


# pylint: disable=too-few-public-methods
class Font:
    font: Dict[str, Image.Image]
    font_loaded: bool = False

    @classmethod
    def load_font(cls):
        if cls.font_loaded:
            return

        location = Path(__file__).parents[1] / "data" / "images"
        font_image_map = load_image_map(location / "font.png", 8, 14)
        with (location / "font_symbols.txt").open() as file:
            font_characters = [c for line in file for c in line
                               if c not in "\n\r"]
        cls.font = dict(zip(font_characters, font_image_map))
        cls.font_loaded = True


def load_image(file_path: Path):
    return Image.open(str(file_path))


def load_image_map(file_path: Path, width: int, height: int):
    image = load_image(file_path)
    rows, columns = image.size[1] // height, image.size[0] // width
    return [image.crop((width * j, height * i,
                        width * (j + 1), height * (i + 1)))
            for i in range(rows) for j in range(columns)]


class GraphicsPunchcardRenderer:
    base: Image.Image
    hole: Image.Image
    col_numbers: Image.Image
    row_numbers: List[Image.Image]
    images_loaded: bool = False

    @classmethod
    def load_images(cls):
        location = Path(__file__).parents[1] / "data" / "images" / "punchcard"
        cls.base = load_image(location / "base.png")
        cls.hole = load_image(location / "hole.png")
        cls.col_numbers = load_image(location / "column_numbers.png")
        cls.row_numbers = load_image_map(location / "row_numbers.png", 8, 17)
        cls.images_loaded = True
        Font.load_font()

    def __init__(self):
        if not GraphicsPunchcardRenderer.images_loaded:
            GraphicsPunchcardRenderer.load_images()

    def __call__(self, stream: GraphicsStream, message: List[Tuple[str, int]],
                 show_text: str):
        paper_layer = self.base.copy()
        numbers_layer = Image.new("RGBA", paper_layer.size)

        for i, col_code in itertools.zip_longest(range(0, 80), message):
            char, code = col_code if col_code is not None else ("", 0)
            x = int(i * 8.5) + 35
            for row, bit in enumerate(PUNCHED_CARD_ROWS):
                y = row * 24 + 30

                if bit_set(code, bit):
                    paper_layer.paste(self.hole, (x, y))
                elif bit < 10:
                    numbers_layer.paste(self.row_numbers[bit], (x, y))

            if show_text and char in Font.font:
                numbers_layer.paste(Font.font[char], (x, 12))

        numbers_layer.paste(self.col_numbers, (35, 93))
        numbers_layer.paste(self.col_numbers, (35, 284))
        stream.add_layer(paper_layer)
        stream.add_layer(numbers_layer)


class GraphicsTapeRenderer:
    base: Image.Image
    hole: Image.Image
    left: Image.Image
    right: Image.Image
    images_loaded = False

    @classmethod
    def load_images(cls):
        location = Path(__file__).parents[1] / "data" / "images" / "tape"
        cls.base = load_image(location / "base.png")
        cls.hole = load_image(location / "hole.png")
        cls.left = load_image(location / "left.png")
        cls.right = load_image(location / "right.png")
        cls.images_loaded = True
        Font.load_font()

    def __init__(self):
        if not GraphicsTapeRenderer.images_loaded:
            GraphicsTapeRenderer.load_images()

    def __call__(self, stream: GraphicsStream, message: List[Tuple[str, int]],
                 show_text: str):
        y_offset = 5 if show_text else 0
        width = (self.left.size[0] + self.right.size[0] +
                 len(message) * self.base.size[0])
        image = Image.new("RGBA", (width, self.base.size[1] + y_offset))

        image.paste(self.left, (0, y_offset))
        x = self.left.size[0]
        for char, code in message:
            image.paste(self.base, (x, y_offset))
            for bit in range(5):
                if not bit_set(code, bit):
                    continue
                y = y_offset + 15 + \
                    self.hole.size[1] * (bit + (0 if bit < 2 else 1))
                image.paste(self.hole, (x, y))
            if show_text and char in Font.font:
                image.paste(Font.font[char], (x, 0))
            x += self.base.size[0]
        image.paste(self.right, (x, y_offset))
        stream.add_layer(image)
