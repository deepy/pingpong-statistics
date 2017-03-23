import psycopg2
import psycopg2.extras
import json
import sys

import slack_api

with open("config.json", "r+") as f:
	config = json.loads(f.read())

slack = slack_api.PinguSlack(token=config['slack_token'], username=config['user_name'])
from weekly_challange import Challenge, pretty_format_matches

conn = psycopg2.connect(config['db'])

matches = Challenge(conn).run()

cur = conn.cursor()
cur.execute("SELECT daterange(date_trunc('week', now())::date, date_trunc('week', now() + interval '1week')::date, '[)')")

result = cur.fetchall()[0][0]
challenge = pretty_format_matches(matches, header=(str(result.lower), str(result.upper)))
slack_api.send_message(config['slack_channel'], challenge)
print(challenge)

query = "INSERT INTO weekly_matchups (date, opponent1, opponent2) VALUES( daterange(date_trunc('week', now())::date, date_trunc('week', now() + interval '1week')::date, '[)'), %s, %s)"
for m in matches:
	p1, p2 = m[0][0], m[1][2]
	cur.execute(query, (m[0][3], m[1][0]))
	slack.send_weekly_challenge(p1, p2)
	slack.send_weekly_challenge(p2, p1)
conn.commit()
