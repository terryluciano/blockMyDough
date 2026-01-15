import os
import random
from pathlib import Path

dumbMessages = [
	"Bestie, stay locked in. We're manifesting that success today!",
	'No cap, your future self is gonna be so proud if you stay focused.',
	"Main character energy only. Don't let the distractions win.",
	"Slay your goals, one task at a time. You've got the vision!",
	'Big brain moves only. Keep that grindset going, fam.',
	"That's a major flex to stay disciplined. Keep it 100!",
	"We're on that glow-up journey. Focus is the vibe.",
	"Don't let the side quests distract you from the main quest.",
	"Period. You're doing amazing, sweetie. Keep pushing!",
	'Straight fire! Your dedication is unmatched. Stay on track.',
	"It's the focus for me. You're absolutely killing it!",
	"No distractions allowed. We're chasing that bread and that growth.",
	'Real talk, consistency is the ultimate cheat code. Keep going!',
	'W energy. Stay focused and watch everything fall into place.',
	"Secure the bag, secure the future. You're doing the most (in a good way)!",
]


script_dir = Path(__file__).resolve()
data_dir_name = 'data'
backup_path = script_dir.parent.parent / data_dir_name / 'hosts.backup'

blocked_domains_file: list[str] = [
	'example.com',
	'www.example.com',
	'youtube.com',
	'www.youtube.com',
	'facebook.com',
	'www.facebook.com',
	'apnews.com',
	'www.apnews.com',
	'cnn.com',
	'www.ccn.com',
	'edition.cnn.com',
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

	backup_path.parent.mkdir(parents=True, exist_ok=True)

	hosts_file = open('/etc/hosts')
	hosts_file.seek(0)

	lines = hosts_file.readlines()

	in_block = False
	clean_lines: list[str] = []
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
		hosts_backup_file.write(f'{line}')

	hosts_backup_file.close()

	print('A backup of your hosts file has been created at:')
	print(f'{backup_path}\n')


def generate_block_hosts_file():
	print_break()

	# Open hosts file and update it
	print('Updating your hosts file to block dumb sites...\n')

	with open('/etc/hosts') as f:
		lines = f.readlines()

	# Filter out existing block
	clean_lines: list[str] = []
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

		f.write(f'{block_entry_marker}\n')

		for domain in blocked_domains_file:
			f.write(f'127.0.0.1 {domain}\n')
			f.write(f'::1       {domain}\n')

		f.write(f'{block_end_entry_marker}\n')

	print('Domains have been BLOCKED!')


def flush_dns_cache():
	print_break()

	print('Flushing DNS cache...\n')

	# Flush DNS cache
	result = os.system('resolvectl flush-caches')

	if result == 0:
		print('DNS cache flushed successfully!\n')
	else:
		print(f'Warning: Failed to flush DNS cache (exit code: {result})\n')
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

	print(f'{random_message}\n')

	backup_hosts_file()

	generate_block_hosts_file()

	flush_dns_cache()

	print('Goodbye!\n')


if __name__ == '__main__':
	main()
