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

		wants = ['R', 'P', 'S']
		random.shuffle(wants)
		wants = wants * (rounds // 3) + wants[:rounds % 3]
		if 'pool' in header:
			setup['deck'] = list(wants)

		self.send(setup)

		for _ in range(rounds):
			round_header = self.receive()
			deck = round_header['deck']

			want = wants.pop(0)

			self.send({
				'hand': want,
			})

			_response = self.receive()
