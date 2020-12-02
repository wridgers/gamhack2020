import random
import sys

def main():
	header = sys.stdin.readline().split(' ')

	version = int(header[0])
	rounds = int(header[1])

	print('ok')

	for _ in range(rounds):
		_line = sys.stdin.readline()
		print(random.choice(['R', 'P', 'S']))


if __name__ == '__main__':
	main()
