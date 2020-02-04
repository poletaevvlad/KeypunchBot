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

import os
from pathlib import Path
from typing import List
from .bot import ChatBot, MessageContext
from .persistance import Store, Format
from .encodings import CharacterSetsRepository, params_factory
from .encodings import TooManyPagesError, MessageTooLongError
from .rendering import renderer_factory, get_filename


# pylint: disable=no-self-use
class KeyPunchBot(ChatBot):
    def __init__(self, api_key: str, store: Store):
        super().__init__(api_key, store)
        data_root = Path(__file__).parents[0] / "data"
        self.charsets = CharacterSetsRepository.load(data_root / "charsets")

    def initialize(self):
        self.on_command("start", self.show_message, ["help", "welcome"])
        self.on_command("about", self.show_message, ["help", "about"])
        self.on_command("help", self.show_help)
        self.on_command("showtext", self.set_text_visible, True)
        self.on_command("hidetext", self.set_text_visible, False)
        for charset in self.charsets:
            self.on_command(charset, self.select_character_set, charset)
        self.on_command("png", self.set_format, Format.PNG)
        self.on_command("jpeg", self.set_format, Format.JPEG)
        self.on_command("text", self.set_format, Format.TEXT)
        self.on_command("cancel", self.cancel_format)
        self.on_command("characters", self.show_characters)

        for part in os.environ.get("HEART_COMMAND", "").split(";"):
            part = part.strip()
            if part != "":
                self.on_command(part, self.show_message, ["heart"])

        super().initialize()

    def show_message(self, ctx: MessageContext, message: List[str]):
        ctx.answer(ctx.lang[message])

    def set_text_visible(self, ctx: MessageContext, visible: bool):
        message_block = "on" if visible else "off"
        if ctx.data.show_text == visible:
            ctx.answer(ctx.lang["text", message_block, "already"])
            return
        ctx.save(show_text=visible)
        ctx.answer(ctx.lang["text", message_block, "set"])

    def select_character_set(self, ctx: MessageContext, charset: str):
        charset_obj = self.charsets[charset]
        if ctx.data.charset == charset:
            ctx.answer(ctx.lang.get("set_charset", "already",
                                    encoding=charset_obj.name))
            return
        ctx.save(charset=charset)
        ctx.answer(ctx.lang.get("set_charset", "selected",
                                encoding=charset_obj.name,
                                kind=["set_charset", charset_obj.type.value]))

    def generate(self, ctx: MessageContext, format: Format, charset: str,
                 text: str):
        encoder = self.charsets[charset]
        text = encoder.fix_string(text)
        params = params_factory(format, encoder.type)
        try:
            encoding = encoder.encode(text, params)
            if encoding.unknown_count > 0:
                if encoding.unknown_count > encoding.total_length / 2:
                    ctx.answer(ctx.lang["encoding", "most_unsupported"])
                    return
                ctx.answer(ctx.lang["encoding", "some_unsupported"])
        except MessageTooLongError:
            ctx.answer(ctx.lang.get("encoding", "too_long",
                                    columns=str(params.max_length)))
            return
        except TooManyPagesError:
            ctx.answer(ctx.lang.get("encoding", "too_many_pages",
                                    pages=str(params.max_pages)))
            return

        stream, renderer = renderer_factory(format, encoder.type)
        for page in encoding.result:
            renderer(stream, page, ctx.data.show_text)
            stream.break_page()

        files_count = stream.get_files_count()
        for i, file in enumerate(stream.generate_files()):
            if format == Format.DEFAULT:
                ctx.send_photo(file)
            else:
                filename = get_filename(encoder.type, format, i, files_count)
                ctx.send_file(file, filename)

    def text(self, ctx: MessageContext):
        self.generate(ctx, ctx.data.output_format, ctx.data.charset,
                      ctx.message)
        ctx.save(format=Format.DEFAULT)

    def set_format(self, ctx: MessageContext, output_format: Format):
        message = ctx.message
        if len(message) == 0:
            ctx.save(format=output_format)
            ctx.answer(ctx.lang.get("format", "prompt",
                                    format=["format", output_format.value]))
        else:
            self.generate(ctx, output_format, ctx.data.charset, message)

    def cancel_format(self, ctx: MessageContext):
        if ctx.data.output_format == Format.DEFAULT:
            ctx.answer(ctx.lang["cancel", "fail"])
        else:
            ctx.save(format=Format.DEFAULT)
            ctx.answer(ctx.lang["cancel", "done"])

    def show_characters(self, ctx: MessageContext):
        charsets = list(self.charsets.items())
        charsets.sort(key=lambda value: value[1].name)
        characters_list = "".join(
            ctx.lang.get("characters", "characters_line", entry=line)
            for line in ctx.lang.get_object("characters", "supported",
                                            ctx.data.charset))
        charsets_list = "".join(
            ctx.lang.get("characters", "charset_line",
                         charset=charset.name, command=charset_id,
                         kind=["characters", "kinds", charset.type.value])
            for charset_id, charset in charsets
        )
        ctx.answer(ctx.lang.get("characters", "help",
                                charset=self.charsets[ctx.data.charset].name,
                                charsets_list=charsets_list,
                                characters_list=characters_list))

    def show_help(self, ctx: MessageContext):
        charsets = list(self.charsets.items())
        charsets.sort(key=lambda value: value[1].name)
        encodings = "".join(ctx.lang.get("help", "encoding_line",
                                         command=charset_id, name=charset.name)
                            for charset_id, charset in charsets)
        ctx.answer(ctx.lang.get("help", "help", encodings=encodings))

    def unknown_command(self, ctx: MessageContext):
        ctx.answer(ctx.lang.get(["unknown", "command"], suggestion=""))

    def unsupported_type(self, ctx: MessageContext):
        ctx.answer(ctx.lang["unknown", "type"])
