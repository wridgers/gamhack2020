import datetime as dt
import sqlite3

from jinja2 import Template

TEMPLATE = '''<html>
	<head>
		<title>gamhack2020</title>
		<style>
		 table, th, td {
		  border: 1px solid black;
		}
		</style>
	</head>

	<body>
		<h1>gamhack2020</h1>

		<ul>
			<li><a href="./rules.html">rules</a></li>
		</ul>

		<h2>recent pairings</h2>
		<table>
			<thead>
				<tr>
					<td>id</td>
					<td>tournament id</td>
					<td>gen</td>
					<td>p1</td>
					<td>p1 score</td>
					<td>p2</td>
					<td>p2 score</td>
					<td>outcome</td>
					<td>when</td>
					<td>logs id</td>
				</tr>
			</thead>

			<tbody>
				{% for result in results %}
					<tr>
						<td>{{ result[0] }}</td>
						<td>{{ result[1] }}</td>
						<td>{{ result[2] }}</td>
						<td>{{ result[3] }}</td>
						<td>{{ result[4] }}</td>
						<td>{{ result[5] }}</td>
						<td>{{ result[6] }}</td>
						<td>{{ result[7] }}</td>
						<td>{{ result[8] }}</td>

						<td><a href="/logs/{{ result[1] }}.txt">logs</a></td>
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
	cur.execute('select * from pairing_results order by t desc limit 100')
	results = cur.fetchall()

	conn.commit()
	conn.close()

	template = Template(TEMPLATE)

	print(template.render(results=results, now=str(dt.datetime.now())))

if __name__ == '__main__':
	main()
