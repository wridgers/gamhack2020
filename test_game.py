import collections

import pytest

from game import BaseGame, GameGen0, GameGen1, GameGen2, GameGen3
from game import EverybodyDiesException, P1FoulException, P2FoulException, GameException


@pytest.mark.parametrize('hands, exception, scores', [
	[(None, 'S'), P1FoulException, [-1, 1]],
	[('R', None), P2FoulException, [1, -1]],
	[(None, None), P1FoulException, [-1, 1]],
])
def test_base_game_none(hands, exception, scores):
	game = BaseGame(['p1', 'p2'], 3)
	game.decks = [['R'] * 3, ['S'] * 3]

	with pytest.raises(exception):
		game.apply(hands)

	assert game.final_scores() == scores


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


def test_gen2_game():
	game = GameGen2(['p1', 'p2'], 3)
	game.decks = [['R', 'R', 'R'], ['S', 'S', 'S']]

	game_header = game.game_header()
	assert game_header['gen'] == 2
	assert game_header['rounds'] == 3
	assert game_header['players'] == ['p1', 'p2']

	game.apply(['R', 'S'])
	game.apply(['R', 'S'])

	p1_header, p2_header = game.round_headers()
	assert p1_header['round'] == 3
	assert p1_header['deck'] == ['R']
	assert p2_header['round'] == 3
	assert p2_header['deck'] == ['S']

	with pytest.raises(P1FoulException):
		game.apply(['P', 'S']) # p1 can't play P

	assert game.final_scores() == [-1, 1]


@pytest.mark.parametrize('deck, foul', [
	[None, True],
	[[], True],
	[['R', 'R', 'R'], True],
	[['R', 'R', 'P', 'P', 'R'], True],
	[['R', 'R', 'P', 'P', '?'], True],
	[['R', 'R', 'P', 'P', 'S'], False],
])
def test_gen2_setup(deck, foul):
	game = GameGen2(['p1', 'p2'], 5)
	assert game.pool == ['R', 'R', 'P', 'P', 'S', 'S']
	assert game.total_rounds == 5

	setup = {
		'ready': True,
	}

	if deck:
		setup['deck'] = deck

	if foul:
		with pytest.raises(P1FoulException):
			game.setup(0, setup)

	else:
		game.setup(0, setup)


def test_gen3_game_k():
	game = GameGen3(['p1', 'p2'], 7)
	game.decks = [
		['R', 'R', 'P', 'P', 'S', 'S', 'C'],
		['R', 'R', 'P', 'P', 'S', 'S', 'C'],
	]

	with pytest.raises(EverybodyDiesException):
		game.apply(['C', 'C'])

	assert game.final_scores() == [-1, -1]


def test_gen3_game_l():
	game = GameGen3(['p1', 'p2'], 4)
	game.decks = [
		['R', 'R', 'R', 'L'],
		['P', 'R', 'P', 'L'],
	]
	compare = lambda x, y: collections.Counter(x) == collections.Counter(y)


	p1_response, p2_response = game.apply(['L', 'P'])
	assert compare(p1_response['look'], ['P', 'R', 'L'])
	assert 'look' not in p2_response

	assert game.scores == [0, 1]

	p1_response, p2_response = game.apply(['R', 'L'])
	assert 'look' not in p1_response
	assert compare(p2_response['look'], ['R', 'R'])

	assert game.scores == [1, 1]
