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
from typing import Iterable, List, Union
from textwrap import dedent
import yaml
from xml.etree import ElementTree
import pytest

LOCALES_PATH = Path(__file__).parents[2] / "keypunch_bot" / "data" / "i18n"


def check_html_string(string: str):
    ElementTree.fromstring(f"<root>{string}</root>")


@pytest.mark.parametrize("string", [
    "a, b", "a, <b>b</b>", "<i>a, <b>b</b></i>"
])
def test_check_valid(string: str):
    check_html_string(string)


@pytest.mark.parametrize("string", [
    "a, < b", "<i>a, <b></i>b</b>", "<i>a</i", "<i>a</b>",
    "<i title=name>x</i>", "<i>a<i>"
])
def test_check_invalid(string: str):
    with pytest.raises(ElementTree.ParseError):
        check_html_string(string)


def find_yaml_strings(path: Path, locale: str) -> \
        Iterable[List[Union[str, int]]]:
    with (path / f"{locale}.yaml").open() as file:
        data = yaml.load(file, yaml.CLoader)

    def find_strings(path: List[str], value):
        if isinstance(value, str):
            yield path
        elif isinstance(value, list):
            for index, entry in enumerate(value):
                yield from find_strings([*path, index], entry)
        elif isinstance(value, dict):
            for key in value:
                yield from find_strings([*path, key], value[key])

    return find_strings([], data)


def test_find_yaml_strings(tmp_path):
    path = Path(tmp_path)
    yaml = dedent("""\
        a: string
        b: 1
        c: {d: 1, e: a, f: [b, 2, c], g: ""}
        h: [1, "2", 3]
        """)
    (path / "en.yaml").write_text(yaml)

    paths = list(find_yaml_strings(path, "en"))
    assert paths == [
        ["a"], ["c", "e"], ["c", "f", 0], ["c", "f", 2], ["c", "g"], ["h", 1]
    ]


@pytest.mark.parametrize("locale, path", [
    (locale, path)
    for locale in ["en", "ru"]
    for path in find_yaml_strings(LOCALES_PATH, locale)
])
def test_string(locale: str, path: List[Union[int, str]]):
    with (LOCALES_PATH / (locale + ".yaml")).open() as file:
        data = yaml.load(file, yaml.CLoader)
        for part in path:
            data = data[part]

    check_html_string(data)
