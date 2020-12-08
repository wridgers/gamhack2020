import json
import random
import sys
from .. import base

class Player(base.Player):
	def run(self):
		header = self.receive()

		_gen = header['gen']
		rounds = header['rounds']

		self.send({
			'ready': True,
		})

		for _ in range(rounds):
			round_header = self.receive()
			deck = round_header['deck']

			self.send({
				'hand': deck[0],
			})

			_response = self.receive()
