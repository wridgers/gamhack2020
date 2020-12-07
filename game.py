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

		('R', 'P'): (-1, 1),
		('R', 'S'): (1, -1),

		('P', 'R'): (1, -1),
		('P', 'S'): (-1, 1),

		('S', 'R'): (-1, 1),
		('S', 'P'): (1, -1),
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

	def round_header(self, player_idx):
		if self.current_round > self.total_rounds:
			raise GameException('game is over')

		return {
			'round': self.current_round,
			'deck': self.decks[player_idx],
		}

	def apply(self, p1_card, p2_card):
		if self.current_round > self.total_rounds:
			raise GameException('game is over')

		if p1_card in self.decks[0] and p2_card in self.decks[1]:
			self.decks[0].remove(p1_card)
			self.decks[1].remove(p2_card)

			payoffs = self.PAYOFF_TABLE[p1_card, p2_card]

			self.scores[0] += payoffs[0]
			self.scores[1] += payoffs[1]

		else:
			if p1_card not in self.decks[0]:
				self.scores[0] += self.BAD_PLAY_COST
				self.scores[1] += self.BAD_PLAY_REWARD
			else:
				self.decks[0].remove(p1_card)

			if p2_card not in self.decks[1]:
				self.scores[0] += self.BAD_PLAY_REWARD
				self.scores[1] += self.BAD_PLAY_COST
			else:
				self.decks[1].remove(p2_card)

		self.current_round += 1

		return [
			{'opponent_hand': p2_card, },
			{'opponent_hand': p1_card, },
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
