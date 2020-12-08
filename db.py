import sqlite3

DB_FILE = 'hack.db'

SCHEMA = [
'''
create table if not exists engine (
	generation integer not null,
	rounds integer not null,
	cr_date timestamp default current_timestamp
);
''',
'''
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
''',
'''
create table if not exists tournament_results (
	id integer primary key,
	tournament_id text not null,
	player text not null,
	elimination_round integer not null
);
''',
]


def setupdb():
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()
	for statement in SCHEMA:
		cur.execute(statement)

	conn.commit()
	conn.close()


def latest_engine_params():
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()
	cur.execute('select generation, rounds from engine order by cr_date desc limit 1')

	params = cur.fetchone()

	conn.commit()
	conn.close()

	return params or (0, 50)


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

def save_tournament_result(tournament_id, rankings):
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()
	for t_round, player_list in enumerate(rankings):
		elimination_round = t_round - len(rankings) + 1
		for player_name in player_list:
			cur.execute(
				'''
					insert into tournament_results
					(tournament_id, player, elimination_round)
					values (?, ?, ?)
				''',
				(
					tournament_id,
					player_name,
					elimination_round,
				)
			)

	conn.commit()
	conn.close()

if __name__ == '__main__':
	setupdb()
