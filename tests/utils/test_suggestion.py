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
from keypunch_bot.utils.suggestions import levenshtein

LEVENSHTEIN_CASES = [
    ("abcdef", "abcdef", 0),
    ("abc", "dbc", 1),
    ("", "hello", 5),
    ("abcdef", "adcbef", 2),
    ("abc", "defghiabjklmn", 11),
    ("hello", "olleh", 4),
]


@pytest.mark.parametrize("word1, word2, distance", [
    *LEVENSHTEIN_CASES,
    *[(w2, w1, distance) for w1, w2, distance in LEVENSHTEIN_CASES]
])
def test_levenshtein(word1: str, word2: str, distance: int):
    assert levenshtein(word1, word2) == distance
