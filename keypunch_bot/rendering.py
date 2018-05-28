# -*- coding: utf-8 -*-
#
# Copyright 2017, 2018 Vladislav Poletaev
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

from os import path
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from PIL import Image

from .encoding import digits


class ImageRenderer:
    symbols = None

    def open_image(self, filename):
        dirpath = "./keypunch_bot"
        return Image.open(path.join(dirpath, "images", filename))

    def split_map(self, image, width, height, rows=None, columns=None):
        if rows is None:
            rows = image.size[1] // height
        if columns is None:
            columns = image.size[0] // width
        for i in range(rows):
            for j in range(columns):
                yield image.crop((width * j, height * i, width * (j + 1),
                                  height * (i + 1)))

    def __init__(self, base):
        self.base = self.open_image(base)
        if self.symbols is None:
            with open("./keypunch_bot/images/encoded_symbols.txt", "r",
                      encoding="utf-8") as f:
                chars = [c for c in f.read() if c != "\n" and c != "\r"]
            symbols_sheet = self.open_image("encoded_symbols.png")
            images = self.split_map(symbols_sheet, 8, 14)
            self.symbols = dict(zip(chars, images))
        symbols_sheet.close()

    def render(self, encoded_message, output_format, show_text, fob):
        image = self.render_transparent(encoded_message, show_text)
        if isinstance(image, list):
            if len(image) == 1:
                image = image[0]
            else:
                img = Image.alpha_composite(image[0], image[1])
                image[0].close()
                image[1].close()
            for i in range(2, len(image)):
                img = Image.alpha_composite(img, image[i])
                image[i].close
            image = img

        if output_format == "jpeg":
            background = Image.new("RGBA", image.size, color=(255, 255, 255))
            new_result = Image.alpha_composite(background, image)
            image.close()
            image = new_result.convert("RGB")
            background.close()
            new_result.close()
        image.save(fob, output_format.upper())
        image.close()


class PunchCardRenderer:
    bit_positions = [11, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


class PunchCardImageRenderer(ImageRenderer, PunchCardRenderer):
    def __init__(self):
        super().__init__("base.png")

        self.hole = self.open_image("hole.png")
        self.column_nums = self.open_image("column_numbers.png")

        number_sheet = self.open_image("row_numbers.png")
        self.numbers = list(self.split_map(number_sheet, 8, 17, 10, 1))
        number_sheet.close()

    def render_transparent(self, encoded_message, show_text):
        paper_layer = self.base.copy()
        numbers_layer = Image.new(self.base.mode, self.base.size)

        for i, code in zip_longest(range(0, 80), encoded_message):
            bits = set() if code is None else digits(code[1])
            x = int(i * 8.5) + 35
            for row, bit in enumerate(self.bit_positions):
                coord = x, row * 24 + 30
                if bit in bits:
                    paper_layer.paste(self.hole, coord)
                elif bit < 10:
                    numbers_layer.paste(self.numbers[bit], coord)
            if show_text and code is not None:
                char = code[0]
                if char is not None and char in self.symbols:
                    numbers_layer.paste(self.symbols[code[0]], (x, 12))
        numbers_layer.paste(self.column_nums, (35, 93))
        numbers_layer.paste(self.column_nums, (35, 284))
        return [paper_layer, numbers_layer]


class TapeImageRenderer(ImageRenderer):
    offset = 5

    def __init__(self):
        super().__init__("tape_base.png")
        self.left = self.open_image("tape_left.png")
        self.hole = self.open_image("tape_hole.png")
        self.right = self.open_image("tape_right.png")

    def render_transparent(self, encoded_message, show_text):
        y0 = self.offset if show_text else 0
        encoded_message = list(encoded_message)
        width = (self.left.size[0] + self.right.size[0] +
                 len(encoded_message) * self.base.size[0])
        image = Image.new("RGBA", (width, self.base.size[1] + y0))
        image.paste(self.left, (0, y0))
        x = self.left.size[0]
        for char, code in encoded_message:
            image.paste(self.base, (x, y0))
            for bit in digits(code):
                y = y0 + 15 + self.hole.size[1] * (bit + (0 if bit < 2 else 1))
                image.paste(self.hole, (x, y))
            if show_text and char is not None and char in self.symbols:
                image.paste(self.symbols[char], (x, 0))
            x += self.base.size[0]
        image.paste(self.right, (x, y0))
        return image


class TapeTextFormatter:
    def render(self, encoded_message, output_format, show_text, fob):
        i = 0
        for char, code in encoded_message:
            fob.write(format(code, "05b"))
            if i < 13:
                fob.write(" ")
                i += 1
            elif i >= 13:
                fob.write("\r\n")
                i = 0


class PunchcardTextFormatter(PunchCardRenderer):
    def format_line(self, fob, codes_list, num):
        fob.write("| ")
        for char, code in codes_list:
            fob.write("x" if num in code else " ")
        fob.write(" " * (80 - len(codes_list)))
        fob.write("|\r\n")

    def render(self, encoded_message, output_format, show_text, fob):
        all_codes = list(map(lambda x: (x[0], digits(x[1])), encoded_message))
        fob.write("  " + "_" * 81 + "\r\n /")
        for i, code in zip_longest(range(80), all_codes):
            if show_text and code is not None and code[0] is not None:
                fob.write(code[0])
            else:
                fob.write(" ")
        fob.write("|\r\n")
        for line in self.bit_positions:
            self.format_line(fob, all_codes, line)
        fob.write("|" + "_" * 81 + "|\r\n")
