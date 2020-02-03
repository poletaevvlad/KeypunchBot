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

from pathlib import Path
from typing import List
from .bot import ChatBot, MessageContext
from .persistance import Store
from .encodings import CharacterSetsRepository


# pylint: disable=no-self-use
class KeyPunchBot(ChatBot):
    def __init__(self, api_key: str, store: Store):
        super().__init__(api_key, store)
        data_root = Path(__file__).parents[0] / "data"
        self.charsets = CharacterSetsRepository.load(data_root / "charsets")

    def initialize(self):
        self.on_command("start", self.show_message, ["help", "welcome"])
        self.on_command("about", self.show_message, ["help", "about"])
        self.on_command("showtext", self.set_text_visible, True)
        self.on_command("hidetext", self.set_text_visible, False)
        for charset in self.charsets:
            self.on_command(charset, self.select_character_set, charset)

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

    def text(self, ctx: MessageContext):
        pass
