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
import yaml
from ..persistance import Format
from .charset import EncodingType, EncodingParams


def get_config():
    if hasattr(get_config, "_value"):
        return getattr(get_config, "_value")

    config_path = Path(__file__).parents[1] / "data" / "encoding.yaml"
    with config_path.open() as file:
        params_config = yaml.load(file, yaml.CLoader)
    setattr(get_config, "_value", params_config)
    return params_config


# pylint: disable=redefined-builtin
def params_factory(format: Format, type: EncodingType) -> EncodingParams:
    config = get_config()
    medium = config["text" if format == Format.TEXT else "image"]
    variant = medium["tape" if type == EncodingType.TAPE else "punchcard"]
    return EncodingParams(
        per_page=variant["per_page"],
        max_length=variant.get("length", -1),
        max_pages=variant.get("pages", -1),
        break_with_line=type == EncodingType.PUNCHCARD
    )
