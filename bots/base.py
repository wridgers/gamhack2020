class Player:
	def __init__(self, player_in_queue, player_out_queue):
		self.player_in_queue = player_in_queue
		self.player_out_queue = player_out_queue

	def send(self, obj):
		self.player_out_queue.put(obj)

	def receive(self):
		return self.player_in_queue.get()
