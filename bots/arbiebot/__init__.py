import json
import logging
import random
import sys

from itertools import groupby
from .. import base


LOGGER = logging.getLogger(__name__)


class Player(base.Player):
	def run(self):
		header = self.receive()

		_gen = header['gen']
		rounds = header['rounds']
		players = header['players']

		idx = players.index('arbiebot')

		setup = {
			'ready': True,
			'deck': random.sample(header['pool'], rounds),
		}

		self.send(setup)

		original_pool = header['pool'].copy()
		opp_plays = []

		for _ in range(rounds):
			round_header = self.receive()
			deck = round_header['deck'].copy()

			opp_potential = original_pool.copy()
			for x in opp_plays:
				opp_potential.remove(x)

			counts = {
				card: len(list(cards))
				for card, cards in groupby(opp_potential)
			}

			LOGGER.info('Orig. pool=%r', original_pool)
			LOGGER.info('Opp. plays=%r', opp_plays)
			LOGGER.info('Opp. poss.=%r', opp_potential)
			LOGGER.info('Counts    =%r', counts)

			most_likely = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:1]

			if not most_likely:
				hand = random.choice(deck)
			else:
				card, _ = most_likely[0]
				hand = self.opposite_of(card)

				if hand not in deck:
					hand = random.choice(deck)

			self.send({
				'hand': hand,
			})

			response = self.receive()
			opp_plays.append(response['hands'][1 - idx])

	@staticmethod
	def opposite_of(hand):
		if hand == 'R':
			return 'P'
		elif hand == 'P':
			return 'S'
		elif hand == 'S':
			return 'R'
		elif hand == 'C':
			return 'L'
		elif hand == 'L':
			return 'T'
		elif hand == 'T':
			return 'C'
