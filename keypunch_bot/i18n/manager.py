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
from pathlib import Path
import yaml
from .language import Language, StringsLanguage, NoMessageLanguage


def load_language(fallback: Language, path: Path) -> Language:
    with path.open() as file:
        messages = yaml.load(file, yaml.CLoader)
    return StringsLanguage(fallback, messages)


class TranslationManager:
    def __init__(self, default: str, languages: Dict[str, Language]):
        self.default = default
        self.languages = languages

    @staticmethod
    def load(location: Path, *, default: str) -> "TranslationManager":
        default_path = location / (default + ".yaml")
        if not default_path.is_file():
            raise FileNotFoundError("Cannot open default language file")
        default_lang = load_language(NoMessageLanguage(), default_path)
        languages: Dict[str, Language] = {default: default_lang}
        for filepath in location.iterdir():
            if filepath.suffix != ".yaml":
                continue
            name = filepath.stem
            if name != default:
                languages[name] = load_language(default_lang, filepath)
        return TranslationManager(default, languages)

    def get(self, language: str) -> Language:
        if language in self.languages:
            return self.languages[language]
        dash_pos = language.find("-")
        if dash_pos >= 0:
            language = language[:dash_pos]
            if language in self.languages:
                return self.languages[language]
        return self.languages[self.default]
