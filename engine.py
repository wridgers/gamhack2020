import importlib
import json
import logging
import os
import random
import re
import sqlite3
import subprocess
import sys
import threading
import queue

from game import GameGen0
from db import setupdb, save_result

LOGGER = logging.getLogger(__name__)


class P1FoulException(Exception):
	pass


class P2FoulException(Exception):
	pass

TIMEOUT = 0.1

class PlayerThread(threading.Thread):
	def __init__(self, player_num, player_module):
		self.player_in_queue = queue.Queue(maxsize=1)
		self.player_out_queue = queue.Queue(maxsize=1)
		self.player_module = player_module
		self.player = player_module.Player(self.player_in_queue, self.player_out_queue)
		self.player_num = player_num
		self.exception_class = [P1FoulException, P2FoulException][player_num - 1]
		super().__init__(daemon=True)

	def run(self):
		self.player.run()

	def join(self):
		super().join(timeout=TIMEOUT)
		if self.is_alive():
			raise self.exception_class('timed out on exit')

	def send(self, obj):
		try:
			return self.player_in_queue.put(obj, timeout=TIMEOUT)
		except queue.Full:
			raise self.exception_class('timed out on write')

	def receive(self):
		try:
			return self.player_out_queue.get(timeout=TIMEOUT)
		except queue.Empty:
			raise self.exception_class('timed out on read')

	def __str__(self):
		return "%s(%s, %s)" % (self.__class__.__name__, self.player_num, self.player_module)

class Engine:
	FOUL_COST = -100
	FOUL_WIN = 1

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
			LOGGER.info("NEW ROUND; players=%s", players)
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

	@staticmethod
	def make_player(player_num, player_name):
		module = importlib.import_module('bots.' + player_name)
		return PlayerThread(player_num, module)

	def run_pairing(self, player_names):
		assert len(player_names) == 2
		LOGGER.info('p1: %s, p2: %s', *player_names)

		players = []
		for idx, player_name in enumerate(player_names):
			player = self.make_player(idx + 1, player_name)
			player.start()
			players.append(player)

		try:
			game = self.game_class(self.rounds)
			for player in players:
				player.send(self.game_header(player_names))

			for idx, player in enumerate(players):
				assert player.receive()['ready']
				LOGGER.info('p%s ready', idx + 1)

			for i in range(self.rounds):
				for player in players:
					player.send(self.round_header(i + 1))

				moves = []
				for player in players:
					moves.append(player.receive()['hand'][0])

				LOGGER.info('p1_move=%r, p2_move=%r', *moves)

				game.apply(*moves)

			for idx, player in enumerate(players):
				player.join()

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
