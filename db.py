import sqlite3

DB_FILE = 'hack.db'

SCHEMA = '''

create table if not exists pairing_results (
	id integer primary key,
	tournament_id text not null,
	gen integer not null,
	p1 text not null,
	p1_score integer not null,
	p2 text not null,
	p2_score integer not null,
	outcome text not null,
	t timestamp default current_timestamp
);

'''


def setupdb():
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()
	cur.execute(SCHEMA)

	conn.commit()
	conn.close()


def save_pairing_result(tournament_id, gen, p1_bot_name, p1_score, p2_bot_name, p2_score, outcome):
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()
	cur.execute('''
	insert into pairing_results
	(tournament_id, gen, p1, p1_score, p2, p2_score, outcome)
	values (?, ?, ?, ?, ?, ?, ?)''', (
		tournament_id,
		gen,
		p1_bot_name,
		p1_score,
		p2_bot_name,
		p2_score,
		outcome,
	))

	conn.commit()
	conn.close()


if __name__ == '__main__':
	setupdb()
