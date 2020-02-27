from pathlib import Path
from typing import Iterable
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
