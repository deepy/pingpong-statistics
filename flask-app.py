import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, jsonify
from os.path import exists
from os import makedirs

db = "dbname=pingis user=alex"
conn = psycopg2.connect(db)

cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/api/history/<username>')
def history(username):
    try:
        cur.execute("""select p.id, p.username, date, score, CASE WHEN p.id=m.winner THEN 'x' ELSE '' END AS win FROM players p LEFT JOIN matches m ON (m.winner = p.id OR m.loser = p.id) where p.username = %s order by p.id, date""", (username,))
        rows = cur.fetchall()
        my_list = []
        for row in rows:
            my_list.append(row)
        return jsonify(my_list)
    except Exception as e:
        print(e)
        return jsonify([])

@app.route('/api/elo/<username>')
def elo(username):
    try:
        cur.execute("""select elo, username FROM players WHERE username=%s""", (username,))
        base_elo = cur.fetchone()['elo']
        cur.execute("""select p.id, p.username, date, score, CASE WHEN p.id=m.loser THEN -m.elo ELSE m.elo END AS elo_change FROM players p LEFT JOIN matches m ON (m.winner = p.id OR m.loser = p.id) where p.username = %s order by date desc""", (username,))
        rows = cur.fetchall()
        my_list = []
        first = True
        for row in rows:
            if not first:
                base_elo += row['elo_change']
            else:
                first = False
            row['elo'] = base_elo
            my_list.append(row)
        return jsonify(my_list)
    except Exception as e:
        print(e)
        return jsonify([])

@app.route('/api/unfinished')
def unfinished():
    try:
        cur.execute("""select m.id,date,score,m.elo, to_json(w) as winner, to_json(l) as loser from matches m LEFT JOIN players w ON winner = w.id LEFT JOIN players l ON loser = l.id""")
        rows = cur.fetchall()
        my_list = []
        for row in rows:
            my_list.append(row)
        return jsonify(my_list)
    except Exception as e:
        print(e)
        return jsonify([])

if __name__ == '__main__':
    app.run('0.0.0.0')