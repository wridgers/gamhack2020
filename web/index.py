import datetime as dt
import sqlite3

import markdown2
from jinja2 import Template

HEADER = '''
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

Unless otherwise stated, each generation carries over rules from the previous generation.
'''

# GEN 0 ########################################################################

PROTOCOL_RULES = ['''
### Generation 0

#### Protocol

The protocol consists of:

1. You will receive a `game_header` dictionary. This will tell you things like your opponent's name, how many rounds you will play, and any other info.
2. You must send a dictionary which says `"ready": True` to indicate you have recveived the `game_header` and are ready to play.
3. For each round:
	1. You will receive a `round_header` dictionary. This will contain at least the key `deck`, which tells you what you can choose to play from.
	2. You must send a dictionary containing at least `hand`, which must be an element of `deck`.
	3. The system will send you a round end response. This may contain the key `"ended": True` which indicates this was the final round.
4. After the final round, your `run` function must return.

##### Examples

- `game_header`, `{'gen': 0, 'rounds': 3, 'players': ['lightningbot', 'hahbot']}`
- `round_header`, `{'idx': 0, 'round': 1, 'deck': ['R', 'P', 'S']}`
- `round_footer`, `{'idx': 1, 'hands': ['P', 'S'], 'scores': [0, 1]}`
- `idx` is your index in `players`, `hands`, and `scores`

#### Deck

Each players deck is 3x the size of `rounds` and contains equal amounts of:

- **R**ock
- **P**aper
- **S**cissors

#### Hands

- You score a point for winning a hand.
- You score no points for losing a hand.
- The payoff grid looks exactly how you expect.

#### Fouling

It is possible to foul by timeout, crash, invalid hand. If you foul, you lose the game.

''',

# GEN 1 ########################################################################

'''
### Generation 1

Each players deck is now the size of `rounds` and consists of exactly equal quantities of each of the three cards.
''',

# GEN 2 ########################################################################

'''
### Generation 2

The `game_header` will contain an additional `pool` key which contains a list of cards, larger than the number of rounds. The pool is the same for both players, but not shared.

Your `game_header` response (setup dict) must contain an additional key `deck` which contains the cards you are going to play with.

- `deck` must be a subset of `pool`
- `deck` must be the same length as the number of rounds

#### Examples

- `{'gen': 2, 'rounds': 17, 'pool': ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], 'players': ['ralphabot', 'team5']}`
- `{'ready': True, 'deck': ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R']}`

''',

# GEN 3 ########################################################################

'''
### Generation 3

#### Special Card Cost

The first special card is free. After that, each special card costs 0.5 points more than the last. This means if you pick `n` special cards, the total cost will be `n(n-1)/4`. Noting that each win gains you 1 point, you should not pick too many special cards!
''',
]

FOOTER = '''
## Changelog

As we change parts of the game (e.g. fix bugs, balance issues) we will try to update this section (and announce in Mattermost).

- 10:55, numpy installed

## Logging

You don't run the code, the system does. You can get data in a few ways:

- [recent pairings](/recent_pairings.html) which shows recent pairings and has lings to tournament log files.
- `/home/gamhack/logs`, which just contains the same files.
- `/home/gamhack/hack.db` which is an sqlite database.

## Test cases

- [test cases](/tests.html)

## Leaderboard

- [leaderboard](/leaderboard.html)

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


def latest_engine_params():
	conn = sqlite3.connect('hack.db')
	cur = conn.cursor()
	cur.execute('select generation from engine order by cr_date desc limit 1')

	row = cur.fetchone()

	conn.commit()
	conn.close()

	if row:
		(gen, ) = row
	else:
		gen = 0

	return gen


def main():
	gen = latest_engine_params()
	rules = ''.join([HEADER] + PROTOCOL_RULES[:(gen + 1)] + [FOOTER])
	markdown = markdown2.markdown(rules)

	print(Template(TEMPLATE).render(markdown=markdown, now=str(dt.datetime.now())))


if __name__ == '__main__':
	main()
