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

from typing import List


def levenshtein(word1: str, word2: str) -> int:
    array = [[0 for j in range(len(word1) + 1)] for i in range(len(word2) + 1)]
    for i in range(1, len(word2) + 1):
        array[i][0] = i
    for j in range(1, len(word1) + 1):
        array[0][j] = j

    for i in range(1, len(word2) + 1):
        for j in range(1, len(word1) + 1):
            subst = 1 if word1[j - 1] != word2[i - 1] else 0
            array[i][j] = min(array[i - 1][j] + 1,
                              array[i][j - 1] + 1,
                              array[i - 1][j - 1] + subst)
    return array[-1][-1]


def compute_suggestions(word: str, possible: List[str],
                        max_dist: int = 2) -> List[str]:
    words = [(command, levenshtein(word, command)) for command in possible]
    words = filter(lambda x: x[1] <= max_dist, words)
    words = sorted(words, key=lambda x: x[1])
    return [word[0] for word in words]
