import logging

LOGGER = logging.getLogger(__name__)


class GameException(Exception):
	pass


class P1FoulException(GameException):
	pass


class P2FoulException(GameException):
	pass


class BaseGame():
	PAYOFF_TABLE = {
		('R', 'R'): (0, 0),
		('P', 'P'): (0, 0),
		('S', 'S'): (0, 0),

		('R', 'P'): (0, 1),
		('R', 'S'): (1, 0),

		('P', 'R'): (1, 0),
		('P', 'S'): (0, 1),

		('S', 'R'): (0, 1),
		('S', 'P'): (1, 0),
	}

	GEN = -1

	# How many points you lose if you play an invalid hand
	BAD_PLAY_COST = -1

	# How many points you gain if your opponent plays an invalid hand
	BAD_PLAY_REWARD = 1

	CARDS = {'R', 'P', 'S'}

	def __init__(self, players, rounds, decks):
		assert len(players) == 2
		assert len(decks) == 2

		self.players = players
		self.decks = decks
		self.scores = [0, 0]

		self.current_round = 1
		self.total_rounds = rounds

	def game_header(self):
		return {
			'gen': self.GEN,
			'rounds': self.total_rounds,
			'players': self.players,
		}

	def round_headers(self):
		if self.current_round > self.total_rounds:
			raise GameException('game is over')

		return [
			{
				'round': self.current_round,
				'deck': self.decks[player_idx],
			}
			for player_idx in range(len(self.players))
		]

	def apply(self, hands):
		if self.current_round > self.total_rounds:
			raise GameException('game is over')

		# no sanity checking here, plus hax to make tests work
		p1_hand, p2_hand = hands
		p1_card = p1_hand[0] if isinstance(p1_hand, list) else p1_hand
		p2_card = p2_hand[0] if isinstance(p2_hand, list) else p2_hand

		if not p1_card or p1_card not in self.decks[0]:
			self.current_round = self.total_rounds + 1  # TODO: gross hack to 'end' the game
			self.scores = [-1, 1] # p1 loses

			raise P1FoulException('invalid card')

		if not p2_card or p2_card not in self.decks[1]:
			self.current_round = self.total_rounds + 1  # TODO: gross hack to 'end' the game
			self.scores = [1, -1] # p2 loses

			raise P2FoulException('invalid card')

		self.decks[0].remove(p1_card)
		self.decks[1].remove(p2_card)

		payoffs = self.PAYOFF_TABLE[p1_card, p2_card]

		self.scores[0] += payoffs[0]
		self.scores[1] += payoffs[1]

		self.current_round += 1

		return [
			{'opponent_hand': p2_hand, },
			{'opponent_hand': p1_hand, },
		]

	def final_scores(self):
		if self.current_round <= self.total_rounds:
			raise GameException('game is not over')

		return self.scores


class GameGen0(BaseGame):
	'''
	Most basic variant. Each player is free to play each card as much as they want.
	'''

	GEN = 0

	def __init__(self, players, rounds):
		decks = [
			list(self.CARDS) * rounds,
			list(self.CARDS) * rounds,
		]

		super().__init__(players, rounds, decks)


class GameGen1(BaseGame):
	'''
	Slightly more complex, each deck has exactly as many cards in their deck as rounds in the game and equal quantities
	of each card type.
	'''

	GEN = 1

	def __init__(self, players, rounds):
		if rounds % len(self.CARDS) != 0:
			# otherwise we can't have equal amounts of cards
			raise GameException('rounds mod len(cards) should be zero')

		decks = [
			list(self.CARDS) * int(rounds / len(self.CARDS)),
			list(self.CARDS) * int(rounds / len(self.CARDS)),
		]

		super().__init__(players, rounds, decks)


class GameGen2(BaseGame):
	'''
	This time, players are free to decide the makeup of their deck.

	It's encouraged that the number of rounds is prime.
	'''

	GEN = 2


class GameGen3(BaseGame):
	'''
	Gen2 but with more cards, KILL and PEAK.
	'''

	GEN = 3
	CARDS = {'R', 'P', 'S', 'K', 'P'}


class GameGen4(BaseGame):
	'''
	Gen3 but with card picking at the beginning.
	'''

	GEN = 4
	CARDS = {'R', 'P', 'S', 'K', 'P'}
