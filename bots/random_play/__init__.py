import json
import random
import sys
from .. import base

class Player(base.Player):
	def run(self):
		header = self.receive()

		version = header['gen']
		rounds = header['rounds']

		self.send({
			'ready': True,
		})

		for _ in range(rounds):
			round_header = self.receive()

			self.send({
				'hand': [random.choice(['R', 'P', 'S'])],
			})

			_response = self.receive()
