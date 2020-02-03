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

import pytest
from keypunch_bot.i18n.language import StringsLanguage, NoMessageLanguage

MESSAGES = {
    "a": "A",
    "b": {
        "c": "C",
        "d": ["D0", "D1", "D2"],
        "e": {
            "f": "F"
        }
    }
}

PATH_EXAMPLES = [
    (["a"], "A"),
    (["c"], "c"),
    (["b", "c"], "C"),
    (["b", "g"], "b.g"),
    (["b", "e"], "b.e"),
    (["b", 1], "b.1"),
    (["b", "e", "f"], "F"),
    (["b", "d", "x"], "b.d.x"),
    (["b", "d", 1], "D1"),
    (["b", "d", 4], "b.d.4"),
    (["b", "d", -2], "b.d.-2")
]


@pytest.mark.parametrize("path, string", PATH_EXAMPLES)
def test_get_string(path, string):
    language = StringsLanguage(NoMessageLanguage(), MESSAGES)
    assert language.__getitem__(*path) == string


@pytest.mark.parametrize("path, string", PATH_EXAMPLES)
def test_get_string_collection(path, string):
    language = StringsLanguage(NoMessageLanguage(), MESSAGES)
    assert language[path] == string
