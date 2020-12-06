import json
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
			'hand': ['R', ],
		}))


if __name__ == '__main__':
	main()
