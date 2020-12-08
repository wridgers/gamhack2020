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

	# TODO: check decks are legal (only contain CARDS)
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
				'idx': player_idx,
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
