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

from typing import Dict, Any, Tuple, Union, List
from .charset import EncodingType, CharacterSet

CodeSpec = Union[int, List[int], List[List[int]]]


def bitmask_to_int(bits: List[int]) -> int:
    value = 0
    for bit in bits:
        value |= 1 << bit
    return value


def process_codes(codes: CodeSpec) -> List[int]:
    if isinstance(codes, int):
        return [codes]
    return [code if isinstance(code, int) else bitmask_to_int(code)
            for code in codes]


def process_code_list(code_list: Dict[str, CodeSpec]) -> Dict[str, List[int]]:
    return {
        char: process_codes(codes)
        for char, codes in code_list.items()
    }


def parse_charset(spec: Dict[str, Any]) -> Tuple[str, CharacterSet]:
    charset = CharacterSet(spec["name"], EncodingType(spec["type"]),
                           spec.get("substitutions", {}))
    charset.add_characters(process_code_list(spec["common"]))
    if "registers" in spec:
        for register in spec["registers"]:
            activation = process_codes(register["activation"])
            codes = process_code_list(register["codes"])
            charset.add_characters(codes, activation=activation)
    return spec["id"], charset
