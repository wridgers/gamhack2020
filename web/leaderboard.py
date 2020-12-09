from collections import defaultdict
import datetime as dt
import sqlite3

from jinja2 import Template

LEADERBOARD_QUERY = '''
	select player, sum(max(0,elimination_round*3+10))
	from tournament_results
	where cr_date >= datetime('now', '-10 minute')
	group by 1
	order by 2 desc
'''

OFFICIAL_LEADERBOARD_QUERY = '''
	select player, sum(max(0,elimination_round*3+10))
	from tournament_results
	join official using (tournament_id)
	group by 1
	order by 2 desc
'''

OFFICIAL_RESULTS_QUERY = '''
	select tournament_id, elimination_round, player
	from tournament_results
	join official using (tournament_id)
	order by 1, 2
'''

TEMPLATE = '''<html>
	<head>
		<style>
			table, th, td {
				border: 1px solid black;
			}
		</style>
	</head>

	<body>
		<h2>Last 10 mins</h2>

		<table>
			<thead>
				<tr>
					<th>pos</th>
					<th>team</th>
					<th>score</th>
				</tr>
			</thead>

			<tbody>
				{% for result in leaderboard %}
					<tr>
						<td>{{ loop.index }}</td>
						<td>{{ result[0] }}</td>
						<td>{{ result[1] }}</td>
					</tr>
				{% endfor %}
			</tbody>
		</table>

		<h2>Official Only</h2>

		<table>
			<thead>
				<tr>
					<th>pos</th>
					<th>team</th>
					<th>score</th>
				</tr>
			</thead>

			<tbody>
				{% for result in official_leaderboard %}
					<tr>
						<td>{{ loop.index }}</td>
						<td>{{ result[0] }}</td>
						<td>{{ result[1] }}</td>
					</tr>
				{% endfor %}
			</tbody>
		</table>

		<h2>Individual Tournament Results</h2>

		{% for tournament in tournament_results %}
		<h3>{{ tournament.tournament_id }}</h3>
		<table>
			<thead>
				<tr>
					<th>Final Round</th>
					<th>Players</th>
				</tr>
			</thead>
			<tbody>
				{% for round in tournament.elimination_rounds %}
					<tr>
						<td>{{ loop.index }}</td>
						<td>{{ round }}</td>
					</tr>
				{% endfor %}
			</tbody>
		</table>
		{% endfor %}

		<p>generated {{ now }}</p>
	</body>
</html>
'''


def main():
	conn = sqlite3.connect('hack.db')

	cur = conn.cursor()
	cur.execute(LEADERBOARD_QUERY)
	leaderboard = cur.fetchall()
	cur.execute(OFFICIAL_LEADERBOARD_QUERY)
	official_leaderboard = cur.fetchall()

	cur.execute(OFFICIAL_RESULTS_QUERY)
	tournament_eliminations = defaultdict(lambda: defaultdict(list))
	for tournament_id, elimination_round, player in cur:
		tournament_eliminations[tournament_id][elimination_round].append(player)
	tournament_results = []
	for tournament_id, rounds in sorted(tournament_eliminations.items(), reverse=True):
		tournament_result = []
		for elimination_round in range(0, -5, -1):
			tournament_result.append(', '.join(rounds[elimination_round]))
		tournament_results.append({'tournament_id': tournament_id, 'elimination_rounds': tournament_result})

	conn.commit()
	conn.close()

	template = Template(TEMPLATE)

	print(template.render(leaderboard=leaderboard, official_leaderboard=official_leaderboard, tournament_results=tournament_results, now=str(dt.datetime.now())))


if __name__ == '__main__':
	main()
