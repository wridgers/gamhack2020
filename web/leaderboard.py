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

	conn.commit()
	conn.close()

	template = Template(TEMPLATE)

	print(template.render(leaderboard=leaderboard, official_leaderboard=official_leaderboard, now=str(dt.datetime.now())))


if __name__ == '__main__':
	main()
