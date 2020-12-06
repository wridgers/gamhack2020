import json
import logging
import os
import random
import sqlite3
import subprocess

import pexpect

from db import setupdb, save_result

LOGGER = logging.getLogger(__name__)

BOTS = {
	'always_rock',
	'random_play',
}


class GameException(Exception):
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

	# How many points you lose if you play an invalid hand
	BAD_PLAY_COST = -1

	# How many points you gain if your opponent plays an invalid hand
	BAD_PLAY_REWARD = 1

	CARDS = {'R', 'P', 'S'}

	def __init__(self, rounds, p1_deck, p2_deck):
		self.p1_deck = p1_deck
		self.p2_deck = p2_deck

		self.p1_score = 0
		self.p2_score = 0

		self.current_round = 1
		self.total_rounds = rounds

	def apply(self, p1_card, p2_card):
		if self.current_round > self.total_rounds:
			raise GameException('game is over')

		if p1_card in self.p1_deck and p2_card in self.p2_deck:
			self.p1_deck.remove(p1_card)
			self.p2_deck.remove(p2_card)

			p1_payoff, p2_payoff = self.PAYOFF_TABLE[p1_card, p2_card]

			self.p1_score += p1_payoff
			self.p2_score += p2_payoff

		else:
			if p1_card not in self.p1_deck:
				self.p1_score += self.BAD_PLAY_COST
				self.p2_score += self.BAD_PLAY_REWARD
			else:
				self.p1_deck.remove(p1_card)

			if p2_card not in self.p2_deck:
				self.p1_score += self.BAD_PLAY_REWARD
				self.p2_score += self.BAD_PLAY_COST
			else:
				self.p2_deck.remove(p2_card)

		self.current_round += 1

	def final_scores(self):
		if self.current_round <= self.total_rounds:
			raise GameException('game is not over')

		return (
			self.p1_score,
			self.p2_score,
		)


class GameGen0(BaseGame):
	'''
	Most basic variant. Each player is free to play each card as much as they want.
	'''

	def __init__(self, rounds):
		p1_deck = list(self.CARDS) * rounds
		p2_deck = list(self.CARDS) * rounds
		super().__init__(rounds, p1_deck, p2_deck)


class GameGen1(BaseGame):
	'''
	Slightly more complex, each deck has exactly as many cards in their deck as rounds in the game and equal quantities
	of each card type.
	'''

	def __init__(self, rounds):
		if rounds % len(self.CARDS) != 0:
			# otherwise we can't have equal amounts of cards
			raise GameException('rounds mod len(cards) should be zero')

		p1_deck = list(self.CARDS) * int(rounds / len(self.CARDS))
		p2_deck = list(self.CARDS) * int(rounds / len(self.CARDS))

		super().__init__(rounds, p1_deck, p2_deck)


class GameGen2(BaseGame):
	'''
	This time, players are free to decide the makeup of their deck.

	It's encouraged that the number of rounds is prime.
	'''
	pass


class Engine:
	def __init__(self, p1_bot_name, p2_bot_name):
		self.p1_bot_name = p1_bot_name
		self.p2_bot_name = p2_bot_name

		self.rounds = 50
		self.game = GameGen0(self.rounds)

		self.p1 = pexpect.spawn('python -u -m bots.%s' % (p1_bot_name, ))
		self.p2 = pexpect.spawn('python -u -m bots.%s' % (p2_bot_name, ))

	def game_header(self):
		return {
			'gen': 0,
			'rounds': self.rounds,
			'p1': self.p1_bot_name,
			'p2': self.p2_bot_name,
		}

	def round_header(self, rnd):
		return {
			'round': rnd,
		}

	@staticmethod
	def write_json(p, obj):
		p.read(p.sendline(json.dumps(obj)))

	@staticmethod
	def read_json(p):
		'''
		TODO: timeout + failure
		'''
		return json.loads(p.readline())

	def run(self):
		LOGGER.info('p1: %s, p2: %s', self.p1_bot_name, self.p2_bot_name)

		self.write_json(self.p1, self.game_header())
		self.write_json(self.p2, self.game_header())

		assert self.read_json(self.p1)['ready']
		LOGGER.info('p1 ready')

		assert self.read_json(self.p2)['ready']
		LOGGER.info('p2 ready')

		for i in range(self.rounds):
			self.write_json(self.p1, self.round_header(i + 1))
			self.write_json(self.p2, self.round_header(i + 1))

			p1_move = self.read_json(self.p1)['hand'][0]
			p2_move = self.read_json(self.p2)['hand'][0]

			LOGGER.info('p1_move=%r, p2_move=%r', p1_move, p2_move)

			self.game.apply(p1_move, p2_move)

		self.p1.expect(pexpect.EOF)
		self.p2.expect(pexpect.EOF)

		p1_score, p2_score = self.game.final_scores()
		LOGGER.info('p1_score=%r, p2_score=%r', p1_score, p2_score)

		save_result(self.p1_bot_name, p1_score, self.p2_bot_name, p2_score)


def main():
	bots = list(BOTS)
	random.shuffle(bots)

	p1_bot_name, p2_bot_name = bots[:2]

	engine = Engine(p1_bot_name, p2_bot_name)
	engine.run()


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	setupdb()
	main()
