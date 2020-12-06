import datetime as dt
import sqlite3

import markdown2
from jinja2 import Template

RULES = '''
# rules

## todo: write rules
'''


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
		{{ markdown }}

		<p>generated {{ now }}</p>
	</body>
</html>
'''

def main():
	template = Template(TEMPLATE)
	markdown = markdown2.markdown(RULES)

	print(template.render(markdown=markdown, now=str(dt.datetime.now())))


if __name__ == '__main__':
	main()
