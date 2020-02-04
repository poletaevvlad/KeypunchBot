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
from keypunch_bot.webhook_server import start_webhook_server


@click.group()
@click.option("--api-key", help="Telegram api key", required=True)
@click.option("--mongo", help="MongoDB connection string")
@click.pass_context
def main(ctx, api_key, mongo):
    if mongo is None:
        store = InMemoryStore()
    else:
        store = MongoStore(mongo)

    bot = KeyPunchBot(api_key, store)
    bot.initialize()
    ctx.obj = bot


@main.command()
@click.pass_context
def polling(ctx):
    bot: KeyPunchBot = ctx.obj
    bot.start_polling()


@main.command()
@click.option("--url", help="The URL this service will be available at",
              required=True)
@click.option("--port", help="The TCP/IP port", type=click.INT,
              required=True)
@click.pass_context
def webhook(ctx, url, port):
    bot: KeyPunchBot = ctx.obj
    start_webhook_server(bot, url, port)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
