#!/usr/bin/python

import json
import dateutil.parser
import psycopg2
import datetime
import sys
import requests

class Match(object):
    pass


class Player(object):
    pass


def parsePlayer(data, newRating, prevRating):
    player = Player()
    player.name = data['name']
    player.username = data['username']
    player.elo = {"current": newRating, "previous": prevRating}
    return player


def parsefile(file):
    matches = []
    for entry in file:
        match = Match()
        match.date = dateutil.parser.parse(entry['date'])
        match.winner = parsePlayer(entry['winnerData'], entry['winnerNewRating'], entry['winnerPrevRating'])
        match.loser = parsePlayer(entry['loserData'], entry['loserNewRating'], entry['loserPrevRating'])
        match.score = (entry['winnerScore'] + entry['loserScore'])
        match.elo = entry['winnerNewRating'] - entry['winnerPrevRating']
        matches.append(match)
    return matches


if __name__ == '__main__':
    import json
    with open("config.json", "r+") as f:
        config = json.loads(f.read())
    conn = psycopg2.connect(config['db'])
    c = conn.cursor()

    c.execute("select date from matches ORDER by date desc LIMIT 1")

    if len(sys.argv)==1:
        r = requests.get(config['address'])
        filename = r.json()
    else:
        filename = sys.argv[1]

    try:
        last_date = c.fetchone()[0]
    except:
        last_date = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)


    def updatePlayer(c, player):
        c.execute("SELECT * FROM players WHERE username = %s", [player.username])
        result = c.fetchone()
        if result is None:
            c.execute("INSERT INTO players (name, username, elo) values (%s, %s, %s) RETURNING id",
                      (player.name, player.username, player.elo['current']))
            return c.fetchone()[0]
        else:
            c.execute("UPDATE players SET elo = %s::int WHERE username = %s", (player.elo['current'], player.username))
            return result[0]


    users = {}
    for match in sorted(parsefile(filename), key=lambda x: x.date):
        if match.date > last_date:
            winner = updatePlayer(c, match.winner)
            loser = updatePlayer(c, match.loser)
            c.execute("INSERT INTO matches (date, winner, loser, score, elo) values (%s::timestamp with time zone, %s, %s, %s, %s)",
                      (match.date, winner, loser, match.score, match.elo))
    conn.commit()
    c.close()
    conn.close()
