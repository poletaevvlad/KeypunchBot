import math
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
    def format_line(self, fob, codes_list: list, num: int) -> str:
        self.write(fob, "| ")
        for i in range(80):
            self.write(fob, "x" if i < len(codes_list) and num in codes_list[i].rows else " ")
        self.write(fob, "|\r\n")
    
    def write(self, fob, *args):
        for string in args:
            fob.write(bytes(string, "utf-8"))

    def format(self, encoded, fob, message_format, show_text):
        all_codes = list(encoded)
        self.write(fob, "  ", "_" * 81, "\r\n")
        self.write(fob, " /")
        for i in range(80):
            self.write(fob, all_codes[i].char if show_text and i < len(all_codes) else " ")

        self.write(fob, "|\r\n")
        for line in self.row_numbers():
            self.format_line(fob, all_codes, line)
        self.write(fob, "|", "_" * 81, "|\r\n")


class ImageRenderer (Renderer):
    def get_image_url(self, filename):
        dirpath = path.dirname(path.realpath(__file__))
        return path.join(dirpath, "images", filename)

    def __init__(self):
        self.base = Image.open(self.get_image_url("base.png"))
        self.hole = Image.open(self.get_image_url("hole.png"))
        self.column_numbers = Image.open(self.get_image_url("column_numbers.png"))
        
        number_sheet = Image.open(self.get_image_url("row_numbers.png"))
        self.numbers = [number_sheet.crop((0, 17 * i, 8, 17 * i + 17)) for i in range(10)]
        number_sheet.close()
        
        symbols_sheet = Image.open(self.get_image_url("encoded_symbols.png"))
        symbols_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ&-:#@'=\".<(+|!$*);,%_>/"
        self.symbols = {c: symbols_sheet.crop((8 * i, 0, 8 * i + 8, 14)) for i, c in enumerate(symbols_chars)}

        symbols_sheet.close()
        
    def format(self, encoded, fob, message_format, show_text):
        paper_layer = self.base.copy()
        numbers_layer = Image.new(self.base.mode, self.base.size)
        
        row_numbers = list(self.row_numbers())
        encoded_char = 1
        i = 0
        for column in range(self.columns_count):
            if encoded_char is not None:
                try:
                    encoded_char = next(encoded)
                except StopIteration:
                    encoded_char = None
            x = int(column * 8.5) + 35
            for row in range(12):
                coord = x, row * 24 + 30
                if encoded_char is not None and row_numbers[row] in encoded_char.rows:
                    paper_layer.paste(self.hole, coord)
                elif row > 1:
                    numbers_layer.paste(self.numbers[row - 2], coord)
            if show_text and encoded_char is not None:
                char = encoded_char.char.upper()
                if char in self.symbols:
                    numbers_layer.paste(self.symbols[char], (x, 12))
            i += 1
        numbers_layer.paste(self.column_numbers, (35, 93))
        numbers_layer.paste(self.column_numbers, (35, 284))
        
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

    def __init__(self, name, name_readable, extension, renderer, renderer_attr, send_image=False, join_cards=False):
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
        return "Format({}, {}, {}, {}, {})".format(self.name, self.extension, self.renderer, 
            self.renderer_attr, self.send_image)


image_renderer = ImageRenderer()
ImageRendererArguments = namedtuple("ImageRendererArguments", ["format", "allow_alpha"])
text_renderer = TextRenderer()

Format.png = Format("png", "PNG", ".png", image_renderer, ImageRendererArguments("PNG", True))
Format.jpeg = Format("jpg", "JPEG", ".jpg", image_renderer, ImageRendererArguments("JPEG", False))
Format.jpeg = Format("text", "text", ".txt", text_renderer, None, join_cards=True)
Format.default = Format(None, None, None, image_renderer, ImageRendererArguments("PNG", True), True)