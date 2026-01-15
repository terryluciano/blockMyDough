import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path('.') / 'env' / '.env'

load_dotenv(dotenv_path=env_path)

environment = os.getenv('ENVIRONMENT', 'prod')

# Default production paths (FHS-compliant)
_DEFAULT_DATA_DIR = Path('/var/lib/blockmydough')
_DEFAULT_RUN_DIR = Path('/run/blockmydough')

# Allow override for development
DATA_DIR = Path(os.getenv('DATA_DIR', _DEFAULT_DATA_DIR))
RUN_DIR = Path(os.getenv('RUN_DIR', _DEFAULT_RUN_DIR))  # figure this out later

# Derived paths
STATE_FILE = DATA_DIR / 'state.json'
DOMAINS_FILE = DATA_DIR / 'domains.txt'
SCHEDULES_FILE = DATA_DIR / 'schedules.json'
PRESETS_FILE = DATA_DIR / 'presets.json'
AUTH_KEY_FILE = DATA_DIR / 'auth.key'
SOCKET_PATH = RUN_DIR / 'daemon.sock'

HOSTS_FILE = '/etc/hosts'

# Section Markers
DOMAINS_MARKER_START = '# <domains>'
DOMAINS_MARKER_END = '# </domains>'
SCHEDULES_MARKER_START = '# <schedules>'
SCHEDULES_MARKER_END = '# </schedules>'
PRESETS_MARKER_START = '# <presets>'
PRESETS_MARKER_END = '# </presets>'


DUMB_MESSAGES: list[str] = [
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
