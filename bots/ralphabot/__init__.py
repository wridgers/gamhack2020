import json
import random
import sys
from .. import base

class Player(base.Player):
	def run(self):
		header = self.receive()

		_gen = header['gen']
		rounds = header['rounds']

		setup = {
			'ready': True,
		}

		if 'pool' in header:
			setup['deck'] = sorted(header['pool'], reverse=True)[:rounds]

		self.send(setup)

		for _ in range(rounds):
			round_header = self.receive()
			deck = round_header['deck']

			self.send({
				'hand': max(deck),
			})

			_response = self.receive()
