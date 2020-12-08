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

	POOL = []
	CARDS = set()

	def __init__(self, players, rounds):
		assert len(players) == 2

		self.players = players
		self.decks = [[]] * len(players)
		self.scores = [0] * len(players)

		self.current_round = 1
		self.total_rounds = rounds

	def game_header(self):
		header = {
			'gen': self.GEN,
			'rounds': self.total_rounds,
			'players': self.players,
		}

		if self.POOL:
			header['pool'] = self.POOL

		return header

	def setup(self, player_idx, obj):
		assert obj['ready'], "not ready"

		if 'deck' in obj:
			assert self.POOL, "no pool"
			assert not self.decks[player_idx], "already has deck"

			# TODO: check deck is subset of pool
			self.decks[player_idx] = obj['deck']

		# TODO: hack...
		if self.GEN == 0:
			assert len(self.decks[player_idx]) == self.total_rounds * len(self.CARDS), "incorrect deck size"
		else:
			assert len(self.decks[player_idx]) == self.total_rounds, "incorrect deck size"

	def round_headers(self):
		if self.current_round > self.total_rounds:
			raise GameException('game is over')

		return [
			{
				'idx': player_idx,
				'round': self.current_round,
				'deck': self.decks[player_idx],
			}
			for player_idx in range(len(self.players))
		]

	def apply(self, hands):
		if self.current_round > self.total_rounds:
			raise GameException('game is over')

		# TODO: no sanity checking here, plus hax to make tests work
		p1_hand, p2_hand = hands
		p1_card = p1_hand[0] if isinstance(p1_hand, list) else p1_hand
		p2_card = p2_hand[0] if isinstance(p2_hand, list) else p2_hand
		cards = (p1_card, p2_card)

		for player_idx, card in enumerate(cards):
			if not card or card not in self.decks[player_idx]:
				# gross hacks to 'end' the game
				self.current_round = self.total_rounds + 1
				self.scores = [[-1, 1], [1, -1]][player_idx]
				raise [P1FoulException, P2FoulException][player_idx]('invalid card: %s' % (card, ))

		payoffs = self.PAYOFF_TABLE[cards]

		for player_idx, card in enumerate(cards):
			self.decks[player_idx].remove(card)

		for player_idx, payoff in enumerate(payoffs):
			self.scores[player_idx] += payoff

		self.current_round += 1

		return [
			{
				'idx': player_idx,
				'hands': hands,
				'scores': self.scores,
			}
			for player_idx in range(len(self.players))
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
	CARDS = {'R', 'P', 'S'}

	def __init__(self, players, rounds):
		super().__init__(players, rounds)
		self.decks = [
			list(self.CARDS) * rounds,
			list(self.CARDS) * rounds,
		]


class GameGen1(BaseGame):
	'''
	Slightly more complex, each deck has exactly as many cards in their deck as rounds in the game and equal quantities
	of each card type.
	'''

	GEN = 1
	CARDS = {'R', 'P', 'S'}

	def __init__(self, players, rounds):
		if rounds % len(self.CARDS) != 0:
			# otherwise we can't have equal amounts of cards
			raise GameException('rounds mod len(cards) should be zero')

		super().__init__(players, rounds)
		self.decks = [
			list(self.CARDS) * int(rounds / len(self.CARDS)),
			list(self.CARDS) * int(rounds / len(self.CARDS)),
		]


class GameGen2(BaseGame):
	'''
	This time, players are free to decide the makeup of their deck from an available pool.

	It's encouraged that the number of rounds is prime.
	'''

	GEN = 2
	POOL = ['R'] * 5 + ['P'] * 5 + ['S'] * 5
	CARDS = {'R', 'P', 'S'}


class GameGen3(BaseGame):
	'''
	Gen2 but with more cards, KILL, PEAK, and STEAL.
	'''

	GEN = 3
	CARDS = {'R', 'P', 'S', 'K', 'P'}


class GameGen4(BaseGame):
	'''
	Gen3 but with card picking at the beginning.
	'''

	GEN = 4
	CARDS = {'R', 'P', 'S', 'K', 'P'}
