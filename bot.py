import os
from itertools import groupby

import nest_asyncio
import scrython

import database as db

nest_asyncio.apply()

from discord.ext import commands
import discord

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
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
    image_url = card.image_uris()['normal']
    output = image_url
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


@bot.command(name='cube-get-events')
async def get_events(ctx):

    events = db.get_events()
    response = ""
    for (id, event_date, winner, decklist) in events:
        response += "{event_date:<20} {winner:<15} {decklist:<15}\n".format(event_date=event_date, winner=winner, decklist=decklist)

    await ctx.send("```%s```" % (response, ))


def get_details_for_event(event_date):

    (id, event_date, winner, deck_name) = db.get_event(event_date)
    decklist = db.get_decklist(event_date)

    response = ""

    response += "Event Date: %s\n" % event_date
    response += "Event Winner: %s\n" % winner
    response += "Deck: %s\n" % deck_name
    response += "Decklist: \n"

    decklist = sorted(decklist, key=lambda x: x[4])
    grouped_by_type = {k:list(v) for (k,v) in groupby(decklist, lambda x: x[4])}

    def print_group(key, grouped):
        result = ""
        if key in grouped:
            result += key + "\n"
            cards = grouped[key]
            for card in list(cards):
                (id, date, qty, card_name, card_type, card_cost) = card
                result += "\t{qty:<3} {card_name:<30} {card_cost:<15}".format(qty=qty, card_name=card_name, card_cost=card_cost).rstrip() + "\n"
        return result

    response += print_group('Creatures', grouped_by_type)
    response += print_group('Planeswalkers', grouped_by_type)
    response += print_group('Spells', grouped_by_type)
    response += print_group('Artifacts', grouped_by_type)
    response += print_group('Enchantments', grouped_by_type)
    response += print_group('Lands', grouped_by_type)
    response += print_group('Other', grouped_by_type)

    return response

@bot.command(name='cube-get-list')
async def get_list(ctx, event_date):
    await ctx.send("```%s```" % (get_details_for_event(event_date),))


if __name__ == '__main__':
    token = os.environ['DISCORD_TOKEN']
    bot.run(token)
