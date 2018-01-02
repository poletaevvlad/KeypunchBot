# -*- coding: utf-8 -*-

from PIL import Image
from os import path
from collections import namedtuple


class Renderer:
    columns_count = 80

    def __init__(self):
        pass

    def row_numbers(self):
        yield 12
        yield 11
        for i in range(0, 10):
            yield i

    def format(self, codes, text):
        raise Exception("Renderer class cannot be used")


class TextRenderer(Renderer):
    def format_line(self, fob, codes_list, num):
        self.write(fob, "| ")
        for i in range(80):
            if i < len(codes_list) and num in codes_list[i].rows:
                self.write(fob, "x")
            else:
                self.write(fob, " ")
        self.write(fob, "|\r\n")

    def write(self, fob, *args):
        for string in args:
            fob.write(bytes(string, "utf-8"))

    def format(self, encoded, fob, message_format, show_text):
        all_codes = list(encoded)
        self.write(fob, "  ", "_" * 81, "\r\n")
        self.write(fob, " /")
        for i in range(80):
            if show_text and i < len(all_codes):
                self.write(fob, all_codes[i].char)
            else:
                self.write(fob, " ")
        self.write(fob, "|\r\n")
        for line in self.row_numbers():
            self.format_line(fob, all_codes, line)
        self.write(fob, "|", "_" * 81, "|\r\n")


class ImageRenderer (Renderer):
    symbols_chars = ("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ&-:#@'=\".<(+|!$*);,"
                     "%_>?/")

    def get_image_url(self, filename):
        dirpath = path.dirname(path.realpath(__file__))
        return path.join(dirpath, "images", filename)

    def __init__(self):
        self.base = Image.open(self.get_image_url("base.png"))
        self.hole = Image.open(self.get_image_url("hole.png"))
        self.column_nums = Image.open(self.get_image_url("column_numbers.png"))

        number_sheet = Image.open(self.get_image_url("row_numbers.png"))
        self.numbers = [number_sheet.crop((0, 17 * i, 8, 17 * i + 17))
                        for i in range(10)]
        number_sheet.close()

        symbols_sheet = Image.open(self.get_image_url("encoded_symbols.png"))
        self.symbols = {c: symbols_sheet.crop((8 * i, 0, 8 * i + 8, 14))
                        for i, c in enumerate(ImageRenderer.symbols_chars)}

        symbols_sheet.close()

    def format(self, encoded_message, fob, message_format, show_text):
        paper_layer = self.base.copy()
        numbers_layer = Image.new(self.base.mode, self.base.size)

        row_numbers = list(self.row_numbers())
        encoded = 1
        i = 0
        for column in range(self.columns_count):
            if encoded is not None:
                try:
                    encoded = next(encoded_message)
                except StopIteration:
                    encoded = None
            x = int(column * 8.5) + 35
            for row in range(12):
                coord = x, row * 24 + 30
                if encoded is not None and row_numbers[row] in encoded.rows:
                    paper_layer.paste(self.hole, coord)
                elif row > 1:
                    numbers_layer.paste(self.numbers[row - 2], coord)
            if show_text and encoded is not None:
                char = encoded.char.upper()
                if char in self.symbols:
                    numbers_layer.paste(self.symbols[char], (x, 12))
            i += 1
        numbers_layer.paste(self.column_nums, (35, 93))
        numbers_layer.paste(self.column_nums, (35, 284))

        result = Image.alpha_composite(paper_layer, numbers_layer)
        if not message_format.renderer_attr.allow_alpha:
            background = Image.new("RGBA", result.size, color=(255, 255, 255))
            new_result = Image.alpha_composite(background, result)
            result.close()
            result = new_result.convert("RGB")
            background.close()
            new_result.close()
        result.save(fob, message_format.renderer_attr.format)
        result.close()
        paper_layer.close()
        numbers_layer.close()


class Format:
    formats = dict()

    def __init__(self, name, name_readable, extension, renderer, renderer_attr,
                 send_image=False, join_cards=False):
        self.name = name
        self.extension = extension
        self.renderer = renderer
        self.renderer_attr = renderer_attr
        self.send_image = send_image
        self.join_cards = join_cards
        self.name_readable = name_readable
        if name is not None:
            self.formats[name] = self

    def make_filename(self, filename):
        return filename + self.extension

    @classmethod
    def get_by_name(cls, name):
        if name in cls.formats:
            return cls.formats[name]
        return None

    def is_default(self):
        return self.name is None

    def __str__(self):
        return "<Format: name={}>".format(self.name)


image_renderer = ImageRenderer()
ImageRendererArgs = namedtuple("ImageRendererArgs", ["format", "allow_alpha"])
text_renderer = TextRenderer()

Format.png = Format("png", "PNG", ".png", image_renderer,
                    ImageRendererArgs("PNG", True))
Format.jpeg = Format("jpeg", "JPEG", ".jpg", image_renderer,
                     ImageRendererArgs("JPEG", False))
Format.jpeg = Format("text", "text", ".txt", text_renderer,
                     None, join_cards=True)
Format.default = Format(None, None, None, image_renderer,
                        ImageRendererArgs("PNG", True), True)
