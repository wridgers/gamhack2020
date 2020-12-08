import importlib
import json
import logging
import math
import os
import random
import re
import sqlite3
import subprocess
import sys
import threading
import queue

from game import GameGen0, GameGen1, GameGen2, GameGen3
from game import EverybodyDiesException, P1FoulException, P2FoulException
from db import setupdb, save_pairing_result, save_tournament_result

LOGGER = logging.getLogger(__name__)

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
			LOGGER.debug('sending %r to %d', obj, self.player_num)
			return self.player_in_queue.put(obj, timeout=TIMEOUT)

		except queue.Full:
			raise self.exception_class('timed out on write')

	def receive(self):
		try:
			obj = self.player_out_queue.get(timeout=TIMEOUT)
			LOGGER.debug('recv. %r from %d', obj, self.player_num)
			return obj

		except queue.Empty:
			raise self.exception_class('timed out on read')

	def __str__(self):
		return "%s(%s, %s)" % (self.__class__.__name__, self.player_num, self.player_module)


class Engine:
	game_classes = [
		GameGen0,
		GameGen1,
		GameGen2,
		GameGen3,
	]

	def __init__(self, tournament_id, gen, rounds):
		self.tournament_id = tournament_id
		self.players = []

		self.gen = gen
		self.rounds = rounds

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

	@staticmethod
	def allocate_tournament(active_players):
		random.shuffle(active_players)
		rounds = math.ceil(math.log2(len(active_players)))
		players = [None] * 2 ** rounds
		i = 0
		for player_name in active_players:
			players[i] = player_name
			i += 2
			if i >= len(players):
				i = 1
		return players

	def run_pairing(self, player_names):
		if player_names[0] is None:
			LOGGER.info("Bye for %s", player_names[1])
			return player_names[1]
		elif player_names[1] is None:
			LOGGER.info("Bye for %s", player_names[0])
			return player_names[0]
		else:
			LOGGER.info("Pairing %s against %s", *player_names)
			winner = self.run_match(player_names)
			if winner > 0:
				winning_player = player_names[winner - 1]
				LOGGER.info("Round winner: %s", winning_player)
				return winning_player
			elif winner == 0:
				winning_player = random.choice(player_names)
				LOGGER.info("Draw: %s wins randomly", winning_player)
				return winning_player
			else:
				LOGGER.info("Both players lose")
				return None

	def run(self):
		players = self.allocate_tournament(list(self.get_players()))
		LOGGER.info("Pairings: %s", players)
		player_last_rounds = []
		while len(players) > 1:
			players_gone = []
			LOGGER.info("NEW ROUND; players=%s", players)
			next_players = []
			assert abs(math.log2(len(players)) % 1) < 0.00001, players
			for i in range(len(players) // 2):
				paired_players = players[i*2:i*2+2]
				winning_player = self.run_pairing(paired_players)
				for player in paired_players:
					if player is not None and player != winning_player:
						players_gone.append(player)
				next_players.append(winning_player)
			LOGGER.info("Eliminated players this round: %s", players_gone)
			player_last_rounds.append(players_gone)
			players = next_players
		player_last_rounds.append(players)
		save_tournament_result(self.tournament_id, player_last_rounds)

		LOGGER.info("Tournament winner: %s", players)

	@staticmethod
	def make_player(player_num, player_name):
		module = importlib.import_module('bots.' + player_name)
		return PlayerThread(player_num, module)

	def run_match(self, player_names):
		assert len(player_names) == 2
		LOGGER.info('p1: %s, p2: %s', *player_names)

		players = []
		for idx, player_name in enumerate(player_names):
			player = self.make_player(idx + 1, player_name)
			player.start()
			players.append(player)

		try:
			game = self.game_classes[self.gen](player_names, self.rounds)

			for player in players:
				player.send(game.game_header())

			for idx, player in enumerate(players):
				game.setup(idx, player.receive())
				LOGGER.info('%s ready', player_names[idx])

			for i in range(self.rounds):
				for player, round_header in zip(players, game.round_headers()):
					player.send(round_header)

				hands = []
				for player in players:
					hands.append(player.receive().get('hand', None))

				LOGGER.info('p1_hand=%r, p2_hand=%r', *hands)

				responses = game.apply(hands)

				for idx, response in enumerate(responses):
					players[idx].send(response)

			for idx, player in enumerate(players):
				player.join()

			outcome = 'win'

		except EverybodyDiesException:
			LOGGER.exception('EVERYBODY DIES.')
			outcome = 'chicken'

		except P1FoulException:
			LOGGER.exception('%s fouled' % (player_names[0], ))
			game.end_in_favour_of(2)
			outcome = 'foul'

		except P2FoulException:
			LOGGER.exception('%s fouled' % (player_names[1], ))
			game.end_in_favour_of(1)
			outcome = 'foul'

		scores = game.final_scores()
		LOGGER.info('p1_score=%r, p2_score=%r', *scores)

		if outcome == 'win' and scores[0] == scores[1]:
			outcome = 'draw'

		save_pairing_result(self.tournament_id, self.gen, player_names[0], scores[0], player_names[1], scores[1], outcome)

		if outcome == 'chicken':
			return -1

		if scores[0] > scores[1]:
			return 1
		if scores[1] > scores[0]:
			return 2

		return 0


def main():
	tournament_id = sys.argv[1]

	params = [
		(0, 5, ),
		(1, 6, ),
		(2, 13, ),
		(3, 13, ),
	]

	for gen, rounds in params:
		engine = Engine("%s-%s" % (tournament_id, gen), gen, rounds)
		engine.run()


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	setupdb()
	main()
