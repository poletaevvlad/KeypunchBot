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

from unittest import mock
from pathlib import Path
from keypunch_bot.encodings import CharacterSetsRepository


def test_loading(tmpdir):
    temp_path = Path(tmpdir)
    (temp_path / "file1").write_text("1")
    (temp_path / "file2.yaml").write_text("2")
    (temp_path / "file3.yaml").write_text("3")
    (temp_path / "file4.yaml").write_text("4")

    charsets = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]
    with mock.patch("keypunch_bot.encodings.repository.parse_charset") as m:
        def side_effect(spec):
            assert spec in {2, 3, 4}
            return f"charset_{spec}", charsets[spec - 2]

        m.side_effect = side_effect
        repo = CharacterSetsRepository.load(temp_path)

    for i, charset_id in enumerate(["charset_2", "charset_3", "charset_4"]):
        assert charset_id in repo
        assert repo[charset_id] == charsets[i]
