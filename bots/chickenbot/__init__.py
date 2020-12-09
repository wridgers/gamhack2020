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
			setup['deck'] = ['C'] * rounds

		self.send(setup)

		for _ in range(rounds):
			round_header = self.receive()
			deck = round_header['deck']

			self.send({
				'hand': min(deck),
			})

			_response = self.receive()
