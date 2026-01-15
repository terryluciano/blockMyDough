import sys
import time

# TODO: idK what this is for yet


def main():
	"""
	Main entry point for BlockMyDough Daemon.
	"""
	print('BlockMyDough Daemon starting...')
	# Placeholder for daemon loop
	try:
		while True:
			time.sleep(60)
	except KeyboardInterrupt:
		print('Daemon stopping...')
		sys.exit(0)


if __name__ == '__main__':
	main()
