from pathlib import Path
from typing import Iterable, List
from textwrap import dedent
import yaml
from xml.etree import ElementTree
import pytest


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


def find_yaml_strings(path: Path, locale: str) -> Iterable[List[str]]:
    with (path / f"{locale}.yaml").open() as file:
        data = yaml.load(file)

    print(data)
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
