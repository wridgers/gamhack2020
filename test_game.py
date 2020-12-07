import pytest

from game import BaseGame, GameGen0, GameGen1, GameGen2, GameException


def test_base_game_none():
	game = BaseGame(['p1', 'p2'], 3, ['R'] * 3, ['S'] * 3)

	# None means bot didn't provide a hand in time
	game.apply(None, 'S')
	game.apply('R', None)
	game.apply(None, None)

	p1_score, p2_score = game.final_scores()
	assert(p1_score == 0)
	assert(p2_score == 0)


def test_gen0_game():
	game = GameGen0(['p1', 'p2'], 3)

	# valid move nets p2 a point
	game.apply('R', 'P')
	assert(game.scores[0] == -1)
	assert(game.scores[1] == 1)

	# invalid move from p2 nets p1 a point, and punishes p2
	game.apply('R', '?')
	assert(game.scores[0] == 0)
	assert(game.scores[1] == 0)

	# game is not over, raise
	with pytest.raises(GameException):
		game.final_scores()

	# draw
	game.apply('S', 'S')
	assert(game.scores[0] == 0)
	assert(game.scores[1] == 0)

	# game is over, raise
	with pytest.raises(GameException):
		game.apply('?', '?')

	p1_score, p2_score = game.final_scores()
	assert(p1_score == 0)
	assert(p2_score == 0)

def test_gen1_game():
	with pytest.raises(GameException):
		game = GameGen1(['p1', 'p2'], 17)

	game = GameGen1(['p1', 'p2'], 3)

	assert(set(game.p1_deck) == {'R', 'P', 'S'})
	assert(set(game.p2_deck) == {'R', 'P', 'S'})

	game.apply('R', 'P') # p2 win
	game.apply('S', 'R') # p2 win
	game.apply('P', 'S') # p2 win

	p1_score, p2_score = game.final_scores()
	assert(p1_score == -3)
	assert(p2_score == 3)

def test_gen1_game_invalid_move():
	game = GameGen1(['p1', 'p2'], 3)

	# p2 plays P twice, oops
	game.apply('R', 'P') # p2 win
	game.apply('S', 'P') # p2 bad
	game.apply('P', 'S') # p2 win

	p1_score, p2_score = game.final_scores()
	assert(p1_score == - 1 + game.BAD_PLAY_REWARD - 1)
	assert(p2_score == + 1 + game.BAD_PLAY_COST + 1)

def test_gen2_game():
	game = GameGen2(['p1', 'p2'], 3, ['R', 'R', 'R'], ['S', 'S', 'S'])

	game.apply('R', 'S')
	game.apply('P', 'S') # p1 can't play P
	game.apply('R', 'S')

	p1_score, p2_score = game.final_scores()
	assert(p1_score == 1 + 1 + game.BAD_PLAY_COST)
	assert(p2_score == -1 -1 + game.BAD_PLAY_REWARD)

	# p1 has an R left, but p2 has an empty deck
	assert(game.p1_deck == ['R'])
	assert(not game.p2_deck)
