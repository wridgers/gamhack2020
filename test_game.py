import pytest

from game import BaseGame, GameGen0, GameGen1, GameGen2
from game import P1FoulException, P2FoulException, GameException


@pytest.mark.parametrize('moves, exception, scores', [
	[(None, 'S'), P1FoulException, [-1, 1]],
	[('R', None), P2FoulException, [1, -1]],
	[(None, None), P1FoulException, [-1, 1]],
])
def test_base_game_none(moves, exception, scores):
	game = BaseGame(['p1', 'p2'], 3, [['R'] * 3, ['S'] * 3])

	with pytest.raises(exception):
		game.apply(*moves)

	assert game.final_scores() == scores


def test_gen0_game():
	game = GameGen0(['p1', 'p2'], 3)

	game_header = game.game_header()
	assert game_header['gen'] == 0
	assert game_header['rounds'] == 3
	assert game_header['players'] == ['p1', 'p2']

	round_header = game.round_header(0) # p1 header
	assert round_header['round'] == 1
	assert len(round_header['deck']) == 9

	# valid move nets p2 a point
	game.apply('R', 'P')

	assert(game.scores[0] == -1)
	assert(game.scores[1] == 1)

	round_header = game.round_header(1) # p2 header
	assert round_header['round'] == 2
	assert len(round_header['deck']) == 8

	# game is not over, raise
	with pytest.raises(GameException):
		game.final_scores()

	# draw
	game.apply('S', 'S')
	assert(game.scores[0] == -1)
	assert(game.scores[1] == 1)

	round_header = game.round_header(0) # p1 header
	assert round_header['round'] == 3
	assert len(round_header['deck']) == 7

	# invalid move from p2 nets p1 a point, and punishes p2
	with pytest.raises(P2FoulException):
		game.apply('R', '?')

	# game is over, raise
	with pytest.raises(GameException):
		game.apply('?', '?')

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

	game.apply('R', 'P') # p2 win
	game.apply('S', 'R') # p2 win

	round_header = game.round_header(0) # p1 header
	assert round_header['round'] == 3
	assert round_header['deck'] == ['P']

	round_header = game.round_header(1) # p2 header
	assert round_header['round'] == 3
	assert round_header['deck'] == ['S']

	game.apply('P', 'S') # p2 win

	with pytest.raises(GameException):
		# game is over, calling round_header is stupid
		round_header = game.round_header(0)

	with pytest.raises(GameException):
		# game is over, calling round_header is stupid
		round_header = game.round_header(1)

	p1_score, p2_score = game.final_scores()
	assert(p1_score == -3)
	assert(p2_score == 3)


def test_gen1_game_invalid_move():
	game = GameGen1(['p1', 'p2'], 3)

	game.apply('R', 'P')

	with pytest.raises(P2FoulException):
		game.apply('S', 'P') # p2 plays P twice, oops

	assert game.final_scores() == [1, -1]


def test_gen2_game():
	game = GameGen2(['p1', 'p2'], 3, [['R', 'R', 'R'], ['S', 'S', 'S']])

	game_header = game.game_header()
	assert game_header['gen'] == 2
	assert game_header['rounds'] == 3
	assert game_header['players'] == ['p1', 'p2']

	game.apply('R', 'S')
	game.apply('R', 'S')

	round_header = game.round_header(0) # p1 header
	assert round_header['round'] == 3
	assert round_header['deck'] == ['R']

	round_header = game.round_header(1) # p2 header
	assert round_header['round'] == 3
	assert round_header['deck'] == ['S']

	with pytest.raises(P1FoulException):
		game.apply('P', 'S') # p1 can't play P

	assert game.final_scores() == [-1, 1]
