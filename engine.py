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


def main():
	bots = list(BOTS)
	random.shuffle(bots)

	p1_bot_name, p2_bot_name = bots[:2]
	rounds = 50

	# docker
	# p1 = pexpect.spawn('docker run -i -v %s/bots:/bots -w /bots python:3.8 python -u -m %s' % (os.getcwd(), p1_bot_name))
	# p2 = pexpect.spawn('docker run -i -v %s/bots:/bots -w /bots python:3.8 python -u -m %s' % (os.getcwd(), p2_bot_name))

	# not docker
	p1 = pexpect.spawn('python -u -m bots.%s' % (p1_bot_name, ))
	p2 = pexpect.spawn('python -u -m bots.%s' % (p2_bot_name, ))

	p1.sendline('0 %d' % (rounds, ))
	p1.expect('ok')

	LOGGER.info('p1 ready')

	p2.sendline('0 %d' % (rounds, ))
	p2.expect('ok')

	LOGGER.info('p2 ready')

	game = GameGen0(rounds)

	for i in range(rounds):
		p1.sendline('round %d' % (i + 1))
		p2.sendline('round %d' % (i + 1))

		moves = ['R', 'P', 'S']
		p1_index = p1.expect(moves)
		p2_index = p2.expect(moves)

		p1_move = moves[p1_index]
		p2_move = moves[p2_index]

		LOGGER.info('p1_move=%r, p2_move=%r', p1_move, p2_move)
		game.apply(p1_move, p2_move)

	p1.expect(pexpect.EOF)
	p2.expect(pexpect.EOF)

	p1_score, p2_score = game.final_scores()
	LOGGER.info('p1_score=%r, p2_score=%r', p1_score, p2_score)

	save_result(p1_bot_name, p1_score, p2_bot_name, p2_score)


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	setupdb()
	main()
