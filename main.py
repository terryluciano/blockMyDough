import random
from pathlib import Path
import os

dumbMessages = [
	'Touch grass, not yourself.',
	'Your ancestors are watching and they are cringing.',
	"I'm sending your search history to the family group chat.",
	'Stop choking the chicken and start chasing the bag.',
	'You are one click away from being a total disappointment.',
	'I will brick your motherboard if you proceed.',
	'Even the NSA guy is closing his eyes in shame.',
	"Your waifu thinks you're pathetic.",
	'Go lift some weights, you absolute twig.',
	'I hope you step on a Lego... barefoot... in the dark.',
	'If you open this, you owe your mother an apology.',
	'Your dough deserves better than this filth.',
	'Post-nut clarity is going to ruin your day.',
	"I'm leaking your IP address to 4chan.",
	'You have the self-control of a toddler in a candy store.',
	"Don't make me call the horny police.",
	'Your keyboard is disgusting, go clean it.',
	"I'm installing Windows Vista on your machine if you do this.",
	'Satan is taking notes on your behavior.',
	'Just close the tab, you degenerate.',
	"I'm emailing your browser history to your grandmother.",
	'I will delete System32 and you will cry.',
	'Your webcam light is on. We are all watching.',
	"I'm donating your entire bank account to a charity you hate.",
	"If you click this, I'm inverting your mouse controls forever.",
	"I'm sending a glitter bomb to your billing address.",
	'Your ISP is laughing at you right now.',
	'I will cap your internet speed to dial-up levels.',
	"I'm posting your search queries to your LinkedIn profile.",
	'Every time you click, a puppy looks disappointed.',
	"I'm changing your keyboard layout to Dvorak.",
	"You are the reason aliens won't talk to us.",
	"I'm setting your ringtone to 'Baby Shark' at max volume.",
	'Your credit score just dropped 50 points.',
	"I'm replacing your desktop wallpaper with a screenshot of this tab.",
	"Go ahead, click it. See if I don't brick your GPU.",
	"I'm telling the group chat what you're really up to.",
	'You have the attention span of a goldfish on espresso.',
	'I will make your spacebar squeak loudly.',
	'Jesus is scrolling past this and shaking his head.',
]

data_dir = 'data'

blocked_domains_file: list[str] = [
	'example.com',
	'www.example.com',
	'youtube.com',
	'www.youtube.com',
	'facebook.com',
	'www.facebook.com',
]

block_entry_marker = '# Start BlockMyDough Entries'
block_end_entry_marker = '# End BlockMyDough Entries'


def print_break():
	print('##############################################################################')


def revert_host_file():
	pass


def backup_hosts_file():
	print_break()

	print('Backing up your hosts file...\n')

	script_dir = Path(__file__).resolve()

	backup_path = script_dir.parent / data_dir / 'hosts.backup'
	backup_path.parent.mkdir(parents=True, exist_ok=True)

	hosts_file = open('/etc/hosts', 'r')
	hosts_file.seek(0)

	lines = hosts_file.readlines()

	in_block = False
	clean_lines = []
	for line in lines:
		if block_entry_marker in line:
			in_block = True
			continue

		if block_end_entry_marker in line:
			in_block = False
			continue

		if not in_block:
			clean_lines.append(line)

	hosts_backup_file = open(backup_path, 'w')

	for line in clean_lines:
		hosts_backup_file.write('{0}'.format(line))

	hosts_backup_file.close()

	print('A backup of your hosts file has been created at:')
	print('{0}\n'.format(backup_path))


def generate_block_hosts_file():
	print_break()

	# Open hosts file and update it
	print('Updating your hosts file to block dumb sites...\n')

	with open('/etc/hosts', 'r') as f:
		lines = f.readlines()

	# Filter out existing block
	clean_lines = []
	in_block = False
	for line in lines:
		if block_entry_marker in line:
			in_block = True
			continue

		if block_end_entry_marker in line:
			in_block = False
			continue

		if not in_block:
			clean_lines.append(line)

	# Write clean content + new block
	with open('/etc/hosts', 'w') as f:
		for line in clean_lines:
			f.write(line)

		if clean_lines and not clean_lines[-1].endswith('\n'):
			f.write('\n')

		f.write('{0}\n'.format(block_entry_marker))

		for domain in blocked_domains_file:
			f.write('127.0.0.1 {0}\n'.format(domain))
			f.write('::1       {0}\n'.format(domain))

		f.write('{0}\n'.format(block_end_entry_marker))

	print('Domains have been BLOCKED!')


def flush_dns_cache():
	print_break()

	print('Flushing DNS cache...\n')

	# Flush DNS cache
	result = os.system('resolvectl flush-caches')

	if result == 0:
		print('DNS cache flushed successfully!\n')
	else:
		print('Warning: Failed to flush DNS cache (exit code: {0})\n'.format(result))
		print('You may need to manually run: sudo resolvectl flush-caches\n')
		return False

	# Verify the resolver is running
	result = os.system('systemctl is-active --quiet systemd-resolved')

	if result == 0:
		print('systemd-resolved is active and running.\n')
	else:
		print('Warning: systemd-resolved may not be running.\n')
		return False

	return True


def main():
	print('Hello from blockmydough!\n')

	random_message = dumbMessages[random.randint(0, len(dumbMessages) - 1)]

	print('{0}\n'.format(random_message))

	backup_hosts_file()

	generate_block_hosts_file()

	flush_dns_cache()

	print('Goodbye!\n')


if __name__ == '__main__':
	main()
