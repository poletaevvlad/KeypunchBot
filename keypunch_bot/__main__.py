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

import click
from keypunch_bot.keypunchbot import KeyPunchBot
from keypunch_bot.persistance import InMemoryStore, MongoStore


@click.command()
@click.option("--api-key", required=True, envvar="API_KEY")
@click.option("--mongo")
def main(api_key, mongo):
    if mongo is None:
        store = InMemoryStore()
    else:
        store = MongoStore(mongo)

    keypunch = KeyPunchBot(api_key, store)
    keypunch.initialize()
    keypunch.start_polling()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
