import sqlite3

DB_FILE = 'hack.db'


def setupdb():
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()
	cur.execute('''create table if not exists results (
		id integer primary key,
		tournament_id text not null,
		gen integer not null,
		p1 text not null,
		p1_score integer not null,
		p2 text not null,
		p2_score integer not null,
		t timestamp default current_timestamp
	)''')

	conn.commit()
	conn.close()


def save_result(tournament_id, gen, p1_bot_name, p1_score, p2_bot_name, p2_score):
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()
	cur.execute('''
	insert into results
	(tournament_id, gen, p1, p1_score, p2, p2_score)
	values (?, ?, ?, ?, ?, ?)''', (
		tournament_id,
		gen,
		p1_bot_name,
		p1_score,
		p2_bot_name,
		p2_score
	))

	conn.commit()
	conn.close()
