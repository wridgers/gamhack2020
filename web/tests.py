import datetime as dt
import sqlite3

import markdown2
from jinja2 import Template

HEADER = '''
# Test cases
'''

# GEN 0 ########################################################################

PROTOCOL_RULES = ['''
### Generation 0

    def test_gen0_game():
    	game = GameGen0(['p1', 'p2'], 3)
    
    	game_header = game.game_header()
    	assert game_header['gen'] == 0
    	assert game_header['rounds'] == 3
    	assert game_header['players'] == ['p1', 'p2']
    
    	p1_header, _p2_header = game.round_headers()
    	assert p1_header['round'] == 1
    	assert len(p1_header['deck']) == 9
    
    	# valid move nets p2 a point
    	game.apply(['R', 'P'])
    
    	assert(game.scores[0] == 0)
    	assert(game.scores[1] == 1)
    
    	_p1_header, p2_header = game.round_headers()
    	assert p2_header['round'] == 2
    	assert len(p2_header['deck']) == 8
    
    	# game is not over, raise
    	with pytest.raises(GameException):
    		game.final_scores()
    
    	# draw
    	game.apply(['S', 'S'])
    	assert(game.scores[0] == 0)
    	assert(game.scores[1] == 1)
    
    	p1_header, _p2_header = game.round_headers()
    	assert p1_header['round'] == 3
    	assert len(p1_header['deck']) == 7
    
    	# invalid move from p2 nets p1 a point, and punishes p2
    	with pytest.raises(P2FoulException):
    		game.apply(['R', '?'])
    
    	# game is over, raise
    	with pytest.raises(GameException):
    		game.apply(['?', '?'])
    
    	# p2 fouled, so loses
    	p1_score, p2_score = game.final_scores()
    	assert(p1_score == 1)
    	assert(p2_score == -1)
''',

# GEN 1 ########################################################################

'''
### Generation 1

    def test_gen1_game():
    	with pytest.raises(GameException):
    		game = GameGen1(['p1', 'p2'], 17)
    
    	game = GameGen1(['p1', 'p2'], 3)
    
    	game_header = game.game_header()
    	assert game_header['gen'] == 1
    	assert game_header['rounds'] == 3
    	assert game_header['players'] == ['p1', 'p2']
    
    	assert(set(game.decks[0]) == {'R', 'P', 'S'})
    	assert(set(game.decks[1]) == {'R', 'P', 'S'})
    
    	game.apply(['R', 'P']) # p2 win
    	game.apply(['S', 'R']) # p2 win
    
    	p1_header, p2_header = game.round_headers()
    	assert p1_header['round'] == 3
    	assert p1_header['deck'] == ['P']
    	assert p2_header['round'] == 3
    	assert p2_header['deck'] == ['S']
    
    	game.apply(['P', 'S']) # p2 win
    
    	with pytest.raises(GameException):
    		# game is over, calling round_headers is stupid
    		game.round_headers()
    
    	with pytest.raises(GameException):
    		# game is over, calling round_headers is stupid
    		game.round_headers()
    
    	p1_score, p2_score = game.final_scores()
    	assert(p1_score == 0)
    	assert(p2_score == 3)
    
    
    def test_gen1_game_invalid_move():
    	game = GameGen1(['p1', 'p2'], 3)
    
    	game.apply(['R', 'P'])
    
    	with pytest.raises(P2FoulException):
    		game.apply(['S', 'P']) # p2 plays P twice, oops
    
    	assert game.final_scores() == [1, -1]
''',

# GEN 2 ########################################################################

'''
### Generation 2

''',

# GEN 3 ########################################################################

'''
### Generation 3

''',
]

FOOTER = ''''''


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
