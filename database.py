import sqlite3

import scrython

conn = sqlite3.connect('cube.db')
c = conn.cursor()


def init():
    c.execute('CREATE TABLE event (id INTEGER PRIMARY KEY AUTOINCREMENT, event_date text, winner text, deckname text)')
    c.execute(
        'CREATE TABLE event_decklist (id INTEGER PRIMARY KEY AUTOINCREMENT, event_date text, card_qty integer, card_name text, card_type text, card_mana_cost text)')


def type_line_to_type(type_line):
    type_line = type_line.lower()

    if "creature" in type_line:
        return "Creatures"
    if "planeswalker" in type_line:
        return "Planeswalkers"
    if "instant" in type_line or "sorcery" in type_line:
        return "Spells"
    if "artifact" in type_line:
        return "Artifacts"
    if "enchantment" in type_line:
        return "Enchantments"
    if "land" in type_line:
        return "Lands"
    return "Other"


def get_card_metadata(card_name):
    try:
        card = scrython.cards.Named(fuzzy=card_name)
        card_type = card.type_line()
        card_mana_cost = card.mana_cost().replace('{', '').replace('}', '')
        real_type = type_line_to_type(card_type)

        return (card_name, real_type, card_mana_cost)
    except Exception as e:
        print(e)
        return (card_name, "Other", "?")


def insert_decklist(metadata):
    (event_date, winner, deckname, decklist_filename) = metadata

    print("Inserting decklist %s for date %s" % (decklist_filename, event_date))

    with open(decklist_filename, 'r') as f:
        lines = f.readlines()
        rows = []
        for line in lines:
            line = line.strip('\n')
            if len(line) == 0:
                continue
            (card_count, separator, card_name) = line.strip('\n').partition(' ')
            print(card_name)

            (_, card_type, card_mana_cost) = get_card_metadata(card_name)

            rows.append((event_date, int(card_count), card_name, card_type, card_mana_cost))

        c.executemany(
            'INSERT INTO event_decklist (event_date, card_qty, card_name, card_type, card_mana_cost) VALUES (?,?,?,?,?)',
            rows)


def insert_event(metadata):
    (event_date, winner, deckname, decklist_filename) = metadata
    print("Inserting event for date " + event_date)
    rows = [(event_date, winner, deckname)]
    c.executemany('INSERT INTO event (event_date, winner, deckname) VALUES (?,?,?)', rows)


def get_events():
    c.execute("select * from event")
    return c.fetchall()


def get_event(event_date):
    c.execute("select * from event where event_date = ?", (event_date,))
    return c.fetchone()


def get_decklist(event_date):
    c.execute("select * from event_decklist where event_date = ?", (event_date,))
    return c.fetchall()


def insert():
    for event in event_metadata:
        insert_event(event)
        insert_decklist(event)

    conn.commit()


if __name__ == '__main__':
    event_metadata = [
        ('2019-05-20', 'Sean', 'UW Control', 'data/2019-05-20_Cube_Winner_Sean_-_UW_Control.txt'),
        ('2019-08-03', 'Phil', 'UW Control', 'data/2019-08-03_Cube_Winner_Phil_-_UW_Control.txt'),
        ('2019-08-31', 'Phil', 'UB Artifacts', 'data/2019-08-31_Cube_Winner_Phil_-_UB_Artifacts.txt'),
        ('2019-08-31', 'Phil', 'UW Artifacts', 'data/2019-08-31_Cube_Winner_Phil_UW_Artifacts.txt'),
        ('2019-12-20', 'Brian', 'UWr Control Twin', 'data/2019-12-20_Cube_Winner_Brian_-_URw_Control_Twin.txt'),
        ('2020-01-04', 'Matt', 'Oath Ramp', 'data/2020-01-04_Cube_Winner_Matt_-_Oath_Ramp.txt')
    ]

    # init()
    # insert()

    conn.commit()
    conn.close()
