import os
import discord
import scrython
import nest_asyncio

nest_asyncio.apply()

from discord.ext import commands

bot = commands.Bot(command_prefix='!')
exchange_rate = 1.30


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def card(ctx, *card_name: str):
    cardname = " ".join(card_name)
    print("got: " + cardname)
    card = scrython.cards.Named(fuzzy=cardname)
    cardname = card.name()
    oracle_text = card.oracle_text()
    image_url = card.image_uris()['normal']
    output = cardname + '\n' + oracle_text + '\n' + image_url
    print(output)
    await ctx.send(output)


@bot.command()
async def price(ctx, *card_name: str):
    cardname = " ".join(card_name)
    print("got: " + cardname)
    card = scrython.cards.Named(fuzzy=cardname)
    card_set = card.set_name()

    usd_price = card.prices(mode="usd")
    usd_foil_price = card.prices(mode="usd_foil")

    cad_price = "N/A"
    cad_foil_price = "N/A"

    if usd_price:
      cad_price = "${:.2f} CAD".format(float(usd_price) * exchange_rate)
    if usd_foil_price:
      cad_foil_price = "${:.2f} CAD".format(float(usd_foil_price) * exchange_rate)

    output = "{cardname} - {card_set} - Non-foil: {cad_price}   Foil: {cad_foil_price}".format(
        cardname=card.name(), card_set=card_set, cad_price=cad_price, cad_foil_price=cad_foil_price)
    await ctx.send(output)


if __name__ == '__main__':
    token = os.environ['DISCORD_TOKEN']
    bot.run(token)
