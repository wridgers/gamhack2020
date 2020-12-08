import json
import random
import sys
from .. import base

import logging
LOGGER = logging.getLogger(__name__)

class Player(base.Player):
	def run(self):
		header = self.receive()

		_gen = header['gen']
		rounds = header['rounds']

		setup = {
			'ready': True,
		}

		if 'pool' in header:
			setup['deck'] = random.sample(header['pool'], rounds)

		self.send(setup)

		last = None

		beat = {'R': 'P', 'P': 'S', 'S': 'R'}

		for _ in range(rounds):
			round_header = self.receive()
			deck = round_header['deck']

			if beat.get(last) not in deck:
				LOGGER.info("random play!")
				play = random.choice(deck)
			else:
				play = beat[last]

			self.send({
				'hand': play,
			})

			response = self.receive()
			last = response['hands'][1 - response['idx']]
			LOGGER.info("last: %s hands: %s idx: %s", last, response['hands'], response['idx'])
