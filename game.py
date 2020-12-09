import logging
import math
import random

from itertools import groupby

LOGGER = logging.getLogger(__name__)


def filter_nones(obj):
	return {
		k: v
		for k, v in obj.items()
		if v is not None
	}

class GameException(Exception):
	pass


class EverybodyDiesException(GameException):
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
	CARDS = set()

	LOOK_SIZE = 3

	def __init__(self, players, rounds):
		assert len(players) == 2

		self.players = players
		self.decks = [[]] * len(players)
		self.scores = [0] * len(players)

		self.current_round = 1
		self.total_rounds = rounds

	@property
	def pool(self):
		return []

	def game_header(self):
		return filter_nones({
			'gen': self.GEN,
			'rounds': self.total_rounds,
			'pool': list(self.pool) or None,
			'players': list(self.players),
		})

	def setup(self, player_idx, obj):
		try:
			assert obj['ready'], 'not ready'


			if 'deck' in obj:
				assert self.pool, 'no pool'
				assert not self.decks[player_idx], 'already has deck'
				assert len(obj['deck']) == self.total_rounds, 'incorrect deck size'

				assert all(x in self.CARDS for x in obj['deck']), 'unknown card'
				assert all(x == 'C' for x in obj['deck']) or all(
					len(list(group)) <= len([x for x in self.pool if x == card])
					for card, group in groupby(sorted(obj['deck']))
				), 'invalid setup deck'

				card_cost = 0.0

				for card in obj['deck']:
					if card not in ('R', 'P', 'S'):
						self.scores[player_idx] -= card_cost
						card_cost += 0.5

				# assert self.scores[player_idx] >= 0, 'over-bought'

				self.decks[player_idx] = list(obj['deck'])

			else:
				assert not self.pool, 'no deck supplied'

		except AssertionError as e:
			self.end_in_favour_of(1 - player_idx)
			raise [P1FoulException, P2FoulException][player_idx]() from e

	def round_headers(self):
		if self.current_round > self.total_rounds:
			raise GameException('game is over')

		return [
			{
				'idx': player_idx,
				'round': self.current_round,
				'deck': list(self.decks[player_idx]),
			}
			for player_idx in range(len(self.players))
		]

	def look(self, player_idx):
		deck = self.decks[player_idx]
		look_size = len(deck) // 2
		return random.sample(deck, look_size)

	def apply(self, hands):
		if self.current_round > self.total_rounds:
			raise GameException('game is over')

		assert len(hands) == 2, 'expected exactly two hands!'

		for player_idx, hand in enumerate(hands):
			try:
				assert hand is not None, 'hand must be played'
				assert type(hand) == str, 'hand should be a str: %r' % (hand, )
				assert len(hand) == 1, 'hand size should be exactly one: %r' % (hand, )

			except AssertionError as e:
				self.end_in_favour_of(1 - player_idx)
				raise [P1FoulException, P2FoulException][player_idx]('invalid hand: %r' % (hand, )) from e

		cards = tuple([hand[0] for hand in hands])

		for player_idx, card in enumerate(cards):
			if not card or card not in self.decks[player_idx]:
				self.end_in_favour_of(1 - player_idx)
				raise [P1FoulException, P2FoulException][player_idx]('invalid card: %s (deck: %s)' % (card, self.decks[player_idx]))

		chickens = [x == 'C' for x in cards]
		rps = [x in ('R', 'P', 'S') for x in cards]

		looks = [x == 'L' for x in cards]
		thieves = [x == 'T' for x in cards]

		if all(chickens):
			self.end_in_favour_of(None)
			raise EverybodyDiesException('both players played CHICKEN')

		elif any(looks):
			payoffs = [0 if x else 0 for x in looks]

		elif any(chickens):
			payoffs = [1 if x else 0 for x in chickens]

		elif not any(rps):
			payoffs = [0] * len(self.players)

		elif any(thieves):
			payoffs = [0 if x else 1 for x in thieves]

		else:
			payoffs = self.PAYOFF_TABLE[cards]

		for player_idx, card in enumerate(cards):
			self.decks[player_idx].remove(card)

		for player_idx, payoff in enumerate(payoffs):
			self.scores[player_idx] += payoff

		self.current_round += 1

		took = []
		for player_idx, thieve in enumerate(thieves):
			if not thieve or any(chickens):
				took.append(None)
				continue

			# Return played card to target of theft
			# Unless it's a steal.
			if cards[1 - player_idx] != 'T':
				self.decks[1 - player_idx].append(cards[1 - player_idx])

			stolen_card = random.choice(self.decks[1 - player_idx])
			self.decks[1 - player_idx].remove(stolen_card)
			self.decks[player_idx].append(stolen_card)

			took.append(stolen_card)

		return [
			filter_nones({
				'idx': player_idx,
				'hands': list(hands),
				'scores': list(self.scores),
				'look': self.look(1 - player_idx) if looks[player_idx] and not any(chickens) else None,
				'took': took[player_idx],
			})
			for player_idx in range(len(self.players))
		]

	def end_in_favour_of(self, player_idx):
		self.current_round = self.total_rounds + 1

		if player_idx == 0:
			self.scores = [1, -1]
		elif player_idx == 1:
			self.scores = [-1, 1]
		else:
			self.scores = [-1, -1]

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
	CARDS = {'R', 'P', 'S'}

	@property
	def pool(self):
		count = math.ceil(self.total_rounds / 2)
		return ['R'] * count + ['P'] * count + ['S'] * count


class GameGen3(GameGen2):
	'''
	Gen2 but with more cards, CHICKEN (C), LOOK (L), and TAKE (T).
	'''

	GEN = 3
	CARDS = {'R', 'P', 'S', 'C', 'L', 'T'}

	@property
	def pool(self):
		count = math.ceil(self.total_rounds / 2)
		return ['R'] * count + ['P'] * count + ['S'] * count + ['C'] * 2 + ['L'] * 2 + ['T'] * 2


class GameGen4(GameGen3):
	'''
	Gen3 but with card picking at the beginning.
	'''

	GEN = 4
	CARDS = {'R', 'P', 'S', 'C', 'L', 'T'}
