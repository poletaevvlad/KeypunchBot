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

from unittest.mock import MagicMock
from pathlib import Path
import pytest
from keypunch_bot.i18n import TranslationManager


def test_loading(tmpdir):
    temp_path = Path(tmpdir)
    (temp_path / "en.yaml").write_text("a: A-en\nb: B-en\n")
    (temp_path / "ru.yaml").write_text("a: A-ru\n")
    (temp_path / "uk.yaml").write_text("b: B-uk\n")

    manager = TranslationManager.load(temp_path, default="en")
    assert len(manager.languages) == 3
    assert set(manager.languages.keys()) == {"en", "ru", "uk"}
    assert manager.languages["en"]["a"] == "A-en"
    assert manager.languages["en"]["c"] == "c"
    assert manager.languages["ru"]["a"] == "A-ru"
    assert manager.languages["ru"]["b"] == "B-en"
    assert manager.languages["ru"]["c"] == "c"


def test_loading_no_default(tmpdir):
    with pytest.raises(FileNotFoundError) as exception:
        TranslationManager.load(Path(tmpdir), default="en")
    assert str(exception.value) == "Cannot open default language file"


@pytest.mark.parametrize("lang_code, expected", [
    ("en", "en"), ("ru", "ru"), ("fr", "en"), ("ru-UA", "ru"), ("uk-UA", "uk")
])
def test_getting_language(lang_code: str, expected: str):
    languages = {
        "en": MagicMock(),
        "ru": MagicMock(),
        "uk": MagicMock()
    }
    manager = TranslationManager("en", languages)
    result = manager.get(lang_code)
    assert result is languages[expected]


def test_default():
    en_language = MagicMock()
    manager = TranslationManager("en", dict(en=en_language))
    assert manager.default_lang is en_language
