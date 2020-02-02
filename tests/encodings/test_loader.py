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

from typing import Any, List
import pytest
from keypunch_bot.encodings import EncodingType
from keypunch_bot.encodings.loader import parse_charset

CODE_CASES = [
    (5, [5]),
    ([2, 7], [2, 7]),
    ([[1, 3, 4], [0, 1, 2]], [26, 7]),
    ([3, [0, 2]], [3, 5])
]


@pytest.mark.parametrize("type_str, type_value", [
    ("tape", EncodingType.TAPE),
    ("punchcard", EncodingType.PUNCHCARD)
])
def test_loading(type_str: str, type_value: EncodingType):
    spec = dict(id="charset", name="Charset", type=type_str,
                common=dict(a=1, b=[2], c=[[3]]))
    charset_id, charset = parse_charset(spec)

    assert charset_id == "charset"
    assert charset.name == "Charset"
    assert charset.type == type_value
    assert charset["a"].codes == [1]
    assert charset["b"].codes == [2]
    assert charset["c"].codes == [8]
    assert charset.substitutions == {}


def test_substitutions():
    spec = dict(id="charset", name="Charset", type="tape",
                common={}, substitutions=dict(a="b", c="d"))
    charset = parse_charset(spec)[1]
    assert charset.substitutions == {"a": "b", "c": "d"}


@pytest.mark.parametrize("value, expected", CODE_CASES)
def test_common_processing_codes(value: Any, expected: List[int]):
    spec = dict(id="charset", name="Charset", type="tape",
                common=dict(a=value))
    charset = parse_charset(spec)[1]
    assert charset["a"].codes == expected
    assert charset["a"].activation == []


@pytest.mark.parametrize("value, expected", CODE_CASES)
def test_register_activation_codes(value: Any, expected: List[int]):
    spec = dict(id="charset", name="Charset", type="tape",
                common={}, registers=[dict(activation=value, codes={"a": 3})])
    charset = parse_charset(spec)[1]
    assert charset["a"].codes == [3]
    assert charset["a"].activation == expected


@pytest.mark.parametrize("value, expected", CODE_CASES)
def test_register_value_codes(value: Any, expected: List[int]):
    spec = dict(id="charset",
                name="Charset",
                type="tape",
                common={},
                registers=[
                    dict(activation=[4], codes={"a": value})
                ])
    charset = parse_charset(spec)[1]
    assert charset["a"].codes == expected
    assert charset["a"].activation == [4]
