import datetime as dt
import sqlite3

from jinja2 import Template

LEADERBOARD_QUERY = '''
	select player, sum(elimination_round)
	from tournament_results
	where cr_date >= datetime('now', '-1 hour')
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

		<p>generated {{ now }}</p>
	</body>
</html>
'''


def main():
	conn = sqlite3.connect('hack.db')

	cur = conn.cursor()
	cur.execute(LEADERBOARD_QUERY)
	leaderboard = cur.fetchall()

	conn.commit()
	conn.close()

	template = Template(TEMPLATE)

	print(template.render(leaderboard=leaderboard, now=str(dt.datetime.now())))


if __name__ == '__main__':
	main()
