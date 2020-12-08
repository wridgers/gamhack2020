import datetime as dt
import sqlite3

import markdown2
from jinja2 import Template

RULES = '''
# GAMHACK 2020

You should be able to do `git clone teamX@gamhack2020.smithersbet.com`, where `X` is your team number. SSH keys were
copied from gbadmin, so anything you use currently should work. Feel free to add others. Before each simulated game,
your code will be pulled from this repository.

## Implementation Notes

Your bot should be implemented in `__init__.py` as a class called `Player`. It will get two queues on `__init__` -- one
to read from, one to write to. We provide a `base.py` with a minimal wrapper around this. You should implement
`Player.run()`. Your code will be run in a thread, and must always respond within 100ms when required -- including
returning in a timely fashion.

## Protocol

The protocol consists of:

1. You will receive a "header" dictionary. This will tell you things like your opponent's name, how many rounds you will play, and any other info.
2. You must send a dictionary which says at least `"ready": True`.
3. For each round:
	1. You will receive a round header dictionary. This will contain at least the key `deck`, which tells you what you can choose to play from.
	2. You must send a dictionary containing at least `hand`, which must be an element of `deck`.
	3. The system will send you a round end response. This may contain the key `"ended": True` which indicates this was the final round.
4. After the final round, your `run` function must return.

## Logging

You don't run the code, the system does. You can get data in a few ways:

- The [online logs directory](/logs) on this server.
- `/home/gamhack/logs`, which just contains the same files.
- `/home/gamhack/hack.db` which is an sqlite database.

## Links

- [recent pairings](/recent_pairings.html)

## Source code dumps

(Will 404 until we make them!)

- [First](/dump1.zip)
- [Second](/dump2.zip)
- [Third](/dump3.zip)
- [Final](/dump4.zip)
'''


TEMPLATE = '''<html>
	<head>
		<title>GAMHACK 2020</title>
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
