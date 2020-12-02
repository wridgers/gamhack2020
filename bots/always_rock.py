import sys

def main():
	header = sys.stdin.readline().split(' ')

	version = int(header[0])
	rounds = int(header[1])

	print('ok')

	for _ in range(rounds):
		_line = sys.stdin.readline()
		print('R')


if __name__ == '__main__':
	main()
