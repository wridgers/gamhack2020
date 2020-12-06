import json
import random
import sys

def main():
	header = json.loads(sys.stdin.readline())

	version = header['gen']
	rounds = header['rounds']

	print(json.dumps({
		'ready': True,
	}))

	for _ in range(rounds):
		round_header = json.loads(sys.stdin.readline())

		print(json.dumps({
			'hand': [random.choice(['R', 'P', 'S']), ],
		}))


if __name__ == '__main__':
	main()
