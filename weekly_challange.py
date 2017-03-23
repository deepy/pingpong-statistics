import psycopg2.extras
import random
from operator import itemgetter


class Challenge:
    def __init__(self, conn):
        self.conn = conn
        self.cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.cur.execute("""SELECT DISTINCT p.username, p.name, p.elo, p.id FROM matches m LEFT JOIN players p ON p.id IN (m.winner, m.loser) LEFT JOIN inactivity i ON i.player IN (m.winner, m.loser) WHERE daterange((now() - interval '2w')::date, now()::date) @> m.date::date AND (NOT i.date && daterange(date_trunc('week', now())::date, date_trunc('week', now() + interval '1week')::date)) OR i.date IS null ORDER BY p.elo DESC""")
        self.elo = self.cur.fetchall()
        self.active_players = [x['id'] for x in self.elo]
        self.matches = []
        self.playing_users_ids = []
        self.PLAYER_RANGE = 10

    def run(self):
        elo = self.elo[:]
        while len(elo) > 1:
            op1 = elo[0]
            choices_with_weight = [(p, 1.0 / (p['count'] + 1)) for p in self.get_matches_played(op1['id']) if
                                   p['id'] not in self.playing_users_ids][0:self.PLAYER_RANGE]
            op2 = weighted_choice(choices_with_weight)
            elo = [p for p in elo if p['id'] != op1['id'] and p['id'] != op2['id']]
            self.matches.append((op1, op2))
            self.playing_users_ids.append(op1['id'])
            self.playing_users_ids.append(op2['id'])

        if len(elo) == 1:
            op1 = elo[0]
            choices_with_weight = [(p, 1.0 / (p['count'] + 1)) for p in
                                   sorted(self.get_matches_played(op1['id']), key=itemgetter('elo'))[0:self.PLAYER_RANGE]]
            op2 = weighted_choice(choices_with_weight)
            self.matches.append((op1, op2))
        return self.matches

    def get_matches_played(self, id):
        self.cur.execute(
            """
                SELECT id, name, username, elo, COALESCE(count,0) as count from players LEFT JOIN (SELECT a.opponent, count(*) FROM
                (SELECT date, loser AS opponent FROM matches WHERE winner=%s
                UNION
                SELECT date, winner AS opponent FROM matches WHERE loser=%s) a
                GROUP BY opponent) AS matches_played ON matches_played.opponent=id where id != %s AND id = ANY ( %s ) ORDER BY elo DESC;
            """, (id,id,id,self.active_players)
        )

        data = self.cur.fetchall()
        return data

def weighted_choice(choices):
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c
        upto += w
    assert False, "Shouldn't get here"


def pretty_format_matches(matches, header=None):
    message = "```"
    if header:
        message += "{: >20} - {: <20}\n".format(*header)
    return message+"\n".join(["{: >20} - {: <20}".format(m[0]['username'], m[1]['username']) for m in matches])+"```"


ref_data = [
    {
        'username': 'tobias.tjader',
        'elo': 2146,
        'matches_played': [
            {'username': 'tommy.myllymaki', 'elo': 201, 'played': 3},
            {'username': 'lars.lindstrom', 'elo': 101, 'played': 1},
        ]
    },
    {
        'username': 'tommy.myllymaki',
        'elo': 201,
        'matches_played': [
            {'username': 'tobias.tjader', 'elo': 2146, 'played': 3},
            {'username': 'lars.lindstrom', 'elo': 101, 'played': 100},
        ]
    },
    {
        'username': 'lars.lindstrom',
        'elo': 101,
        'matches_played': [
            {'username': 'tommy.myllymaki', 'elo': 201, 'played': 100},
            {'username': 'tobias.tjader', 'elo': 2146, 'played': 1},
        ]
    },
]

#matches = Challenge(ref_data).run()
#print(pretty_format_matches(matches))
