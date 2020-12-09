import datetime as dt
import sqlite3

from jinja2 import Template

TEMPLATE = '''<html>
	<head>
		<style>
			table, th, td {
				border: 1px solid black;
			}
		</style>
	</head>

	<body>
		<table style="width: 100%;">
			<thead>
				<tr>
					<th>id</th>
					<th>tournament id</th>
					<th>gen</th>
					<th>p1</th>
					<th>p1 score</th>
					<th>p2</th>
					<th>p2 score</th>
					<th>outcome</th>
					<th>when</th>
					<th>logs id</th>
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
	cur.execute('select * from pairing_results order by cr_date desc limit 100')
	results = cur.fetchall()

	conn.commit()
	conn.close()

	template = Template(TEMPLATE)

	print(template.render(results=results, now=str(dt.datetime.now())))

if __name__ == '__main__':
	main()
