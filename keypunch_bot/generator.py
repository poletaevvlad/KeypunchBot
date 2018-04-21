from io import BytesIO, StringIO

import yaml

from .encoding import CharTable
from .rendering import PunchCardImageRenderer, PunchcardTextFormatter
from .rendering import TapeImageRenderer, TapeTextFormatter


class Format:
    def __init__(self, chartable, format, text_formatter, image_renderer):
        self.chartable = chartable
        self.format = format

    @property
    def is_text(self):
        return self.format == "text"

    @property
    def renderer(self):
        return self.text_formatter if self.is_text else self.image_renderer

    def create_buffer(self):
        if self.is_text:
            return StringIO()
        else:
            return BytesIO()

    @property
    def reuse_buffer(self):
        return self.is_text

    @property
    def file_extension(self):
        if self.format == "jpeg":
            return ".jpg"
        elif self.format == "text":
            return ".txt"
        else:
            return self.format


class TapeFormat(Format):
    text_formatter = TapeTextFormatter()
    image_renderer = TapeImageRenderer()

    def __init__(self, chartable, is_text):
        super().__init__(chartable, is_text, self.text_formatter,
                         self.image_renderer)

    @property
    def max_images(self):
        return 1 if self.is_text else 10

    @property
    def per_image(self):
        return 1024 if self.is_text else 100

    def make_filename(self, num, total):
        if total == 1:
            return "tape" + self.file_extension
        else:
            return "tape{}{}".format(num + 1, self.file_extension)


class PunchcardFormat(Format):
    text_formatter = PunchcardTextFormatter()
    image_renderer = PunchCardImageRenderer()

    def __init__(self, chartable, is_text):
        super().__init__(chartable, is_text, self.text_formatter,
                         self.image_renderer)
        self.per_image = 80

    @property
    def max_images(self):
        return 10 if self.is_text else 5

    def make_filename(self, num, total):
        if total == 1:
            return "punchcard" + self.file_extension
        elif self.is_text:
            return "punchcards" + self.file_extension
        else:
            return "punchcard{}{}".format(num + 1, self.file_extension)


class FormatsManager:
    formats = ["png", "jpeg", "text"]

    def __init__(self, config_file):

        with open(config_file) as f:
            charsets = yaml.load(f)
        self.char_tables = dict()
        for charset in charsets:
            self.char_tables[charset] = CharTable(charsets[charset])

    def get(self, code_table, format):
        if code_table not in self.char_tables:
            raise ValueError("unknown code table: " + code_table)
        ct = self.char_tables[code_table]
        if ct.type == "tape":
            return TapeFormat(ct, format)
        else:
            return PunchcardFormat(ct, format)

    def get_info(self, code_table):
        if code_table not in self.char_tables:
            raise ValueError("unknown code table: " + code_table)
        ct = self.char_tables[code_table]
        return ct.name, ct.type

    def get_all(self):
        for key in sorted(self.char_tables.keys()):
            yield self.char_tables[key].name, key, self.char_tables[key].type

    def get_supported_characters(self, char_table):
        return self.char_tables[char_table].supported
