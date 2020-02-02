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
from keypunch_bot.encodings import CharacterSet, EncodingType, \
    MessageTooLongError, TooManyPagesError


def test_creating():
    charset = CharacterSet("Charset", EncodingType.PUNCHCARD)
    charset.add_characters(dict(a=[1, 2, 3], b=[4, 6]))
    charset.add_characters(dict(c=[7]), activation=[15])

    assert charset.name == "Charset"
    assert charset.type == EncodingType.PUNCHCARD

    assert charset["a"].codes == [1, 2, 3]
    assert not charset["a"].needs_activation

    assert charset["c"].codes == [7]
    assert charset["c"].needs_activation
    assert charset["c"].activation == [15]


def test_encoding_simple():
    charset = CharacterSet("Charset", EncodingType.PUNCHCARD)
    charset.add_characters(dict(a=[1, 2], b=[3]))

    result = charset.encode("acacb", 3)
    assert result.result == [[("a", 1), ("", 2), ("a", 1)],
                             [("", 2), ("b", 3)]]
    assert result.unknown == {"c"}
    assert result.unknown_count == 2


def test_register_switching():
    charset = CharacterSet("Charset", EncodingType.PUNCHCARD)
    charset.add_characters(dict(a=[1], b=[2]))
    charset.add_characters(dict(c=[3], d=[4]), activation=[50])
    charset.add_characters(dict(e=[5], f=[6]), activation=[51])

    result = charset.encode("accdabecf", 100)
    assert len(result.result) == 1

    expected_codes = [1, 50, 3, 3, 4, 1, 2, 51, 5, 50, 3, 51, 6]
    assert [x[1] for x in result.result[0]] == expected_codes
    expected_chars = [
        "a", "", "c", "c", "d", "a", "b", "", "e", "", "c", "", "f"
    ]
    assert [x[0] for x in result.result[0]] == expected_chars


def test_message_too_long():
    charset = CharacterSet("Charset", EncodingType.PUNCHCARD)
    charset.add_characters(dict(a=[1]))
    with pytest.raises(MessageTooLongError):
        charset.encode("aaaaaaaaa", 100, max_length=5)


def test_message_too_long_ignores_unknown():
    charset = CharacterSet("Charset", EncodingType.PUNCHCARD)
    charset.add_characters(dict(a=[1]))
    charset.encode("abbbbbbba", 100, max_length=5)


def test_too_many_pages():
    charset = CharacterSet("Charset", EncodingType.PUNCHCARD)
    charset.add_characters(dict(a=[1]))
    with pytest.raises(TooManyPagesError):
        charset.encode("aaaaaaaaaaaaaaaaaa", 5, max_pages=3)


def test_breaks_with_newline():
    charset = CharacterSet("Charset", EncodingType.PUNCHCARD)
    charset.add_characters(dict(a=[1]))
    result = charset.encode("aaa\naaaa\naaaaaa", 50, break_with_line=True)
    assert [len(x) for x in result.result] == [3, 4, 6]


def test_does_not_break_with_newline():
    charset = CharacterSet("Charset", EncodingType.PUNCHCARD)
    charset.add_characters({"a": [1], "\n": [2]})
    result = charset.encode("aaa\naaaa\naaaaaa", 50)
    assert [len(x) for x in result.result] == [15]
