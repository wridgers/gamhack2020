import json
import logging
import os
import random
import re
import sqlite3
import subprocess
import sys

import pexpect

from db import setupdb, save_result

LOGGER = logging.getLogger(__name__)


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


class P1FoulException(Exception):
	pass


class P2FoulException(Exception):
	pass


class Engine:
	TIMEOUT = 100

	game_class = GameGen0

	def __init__(self, tournament_id):
		self.tournament_id = tournament_id
		self.players = []

		self.rounds = 5

	def game_header(self, player_names):
		return {
			'gen': 0,
			'rounds': self.rounds,
			'p1': player_names[0],
			'p2': player_names[1],
		}

	def round_header(self, rnd):
		return {
			'round': rnd,
		}

	@staticmethod
	def write_json(p, obj):
		data = json.dumps(obj)
		LOGGER.info("Wrote: %s", data)
		got = p.read(p.sendline(data))
		LOGGER.info("Got: %s", got)

	@staticmethod
	def read_json(p):
		'''
		TODO: timeout + failure
		'''
		data = p.readline()
		LOGGER.info("Data read: %s", data)
		return json.loads(data)

	def get_players(self):
		module_re = re.compile('^[a-z0-9][a-z0-9_]+$')
		with os.scandir('bots') as it:
			for entry in it:
				if not entry.is_dir(follow_symlinks=True):
					LOGGER.info("skipping %s (not dir)", entry.name)
					continue
				elif not module_re.match(entry.name):
					LOGGER.info("skipping %s (bad name)", entry.name)
					continue
				LOGGER.info("adding %s", entry.name)
				yield entry.name

	def run(self):
		players = list(self.get_players())
		random.shuffle(players)
		while len(players) > 1:
			next_players = []
			for i in range(len(players) // 2):
				round_players = players[i*2:i*2+2]
				LOGGER.info("Pairing %s against %s", *round_players)
				winner = self.run_pairing(round_players)
				if winner > 0:
					winning_player = round_players[winner - 1]
					LOGGER.info("Round winner: %s", winning_player)
					next_players.append(winning_player)
				else:
					LOGGER.info("Draw: Both proceed")
					next_players.extend(round_players)
			if len(players) % 2 == 1:
				# last player gets a bye
				LOGGER.info("Giving a bye to: %s", players[-1])
				next_players.append(players[-1])
			if players == next_players:
				LOGGER.info("Draw in final round!")
				break
			players = next_players

	def run_pairing(self, player_names):
		try:
			assert len(player_names) == 2
			LOGGER.info('p1: %s, p2: %s', *player_names)

			players = [
				pexpect.spawn('python -u -m bots.%s' % (player_name,), timeout=self.TIMEOUT / 1e3)
				for player_name in player_names
			]

			game = self.game_class(self.rounds)
			for player in players:
				self.write_json(player, self.game_header(player_names))

			for idx, player in enumerate(players):
				assert self.read_json(player)['ready']
				LOGGER.info('p%s ready', idx + 1)

			for i in range(self.rounds):
				for player in players:
					self.write_json(player, self.round_header(i + 1))

				moves = []
				for player in players:
					moves.append(self.read_json(player)['hand'][0])

				LOGGER.info('p1_move=%r, p2_move=%r', *moves)

				game.apply(*moves)

			for player in players:
				player.expect(pexpect.EOF)
				player.kill(0)

			scores = game.final_scores()

		except P1FoulException:
			LOGGER.info('p1 fouled. bad p1')
			scores = [self.FOUL_COST, self.FOUL_WIN]

		except P2FoulException:
			LOGGER.info('p2 fouled. bad p2')
			scores = [self.FOUL_WIN, self.FOUL_COST]

		LOGGER.info('p1_score=%r, p2_score=%r', *scores)

		save_result(self.tournament_id, 0, player_names[0], scores[0], player_names[1], scores[1])

		if scores[0] > scores[1]:
			return 1
		if scores[1] > scores[0]:
			return 2
		return 0


def main():
	tournament_id = sys.argv[1]
	engine = Engine(tournament_id)
	engine.run()


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	setupdb()
	main()
