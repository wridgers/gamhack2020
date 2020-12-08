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
			pool = sorted(header['pool'])
			offset = (len(pool) - rounds) // 2
			deck = pool[offset:offset+rounds]
			setup['deck'] = deck

		self.send(setup)

		for _ in range(rounds):
			round_header = self.receive()
			deck = round_header['deck']

			self.send({
				'hand': sorted(deck)[len(deck) // 2],
			})

			_response = self.receive()
