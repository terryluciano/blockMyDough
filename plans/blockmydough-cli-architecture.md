# BlockMyDough CLI Daemon Architecture

## What This Tool Does

BlockMyDough is a **self-control tool** that blocks distracting websites by modifying `/etc/hosts`. The key features:

1. **Block domains** - Add entries to `/etc/hosts` pointing domains to `127.0.0.1`
2. **Timer-based blocking** - "Block YouTube for 2 hours" → cannot unblock until timer expires
3. **Schedule-based blocking** - "Block social media Mon-Fri 9am-5pm"
4. **Tamper protection** - If someone edits `/etc/hosts` to remove blocks, instantly re-apply them
5. **Passphrase protection** - Cannot stop blocking or remove domains without passphrase

---

## Real-World Usage Examples

### Example 1: Start a Focus Session

```bash
# You want to focus for 2 hours - block all distracting sites
$ blockmydough block --for 2h

🔒 Blocking 15 domains for 2 hours
   Started: 10:00 AM
   Ends at: 12:00 PM

   Blocked domains:
   - youtube.com
   - facebook.com
   - twitter.com
   - reddit.com
   ... and 11 more

⚠️  Sites are now blocked. Enter passphrase to cancel early.
```

Now if you try to visit youtube.com in your browser → Connection refused.

### Example 2: Try to Cheat (It Wont Work)

```bash
# You try to manually edit /etc/hosts to remove the blocks
$ sudo nano /etc/hosts
# Delete the BlockMyDough entries and save...

# Within 1 second, the daemon detects the change:
[blockmydough-daemon] Tampering detected! Re-applying blocks...
[blockmydough-daemon] 15 domains re-blocked.

# The blocks are back. You cannot cheat.
```

### Example 3: Try to Stop the Daemon

```bash
$ blockmydough stop

🔒 Active block in progress (1h 23m remaining)
   Enter passphrase to stop: ********

❌ Incorrect passphrase. Daemon still running.
```

```bash
# Even if you try to kill it directly:
$ sudo systemctl stop blockmydough

# The watchdog notices and restarts it within 1 second:
[systemd] blockmydough.service: Stopping...
[blockmydough-watchdog] Main daemon stopped! Restarting...
[systemd] blockmydough.service: Started BlockMyDough Daemon

# You literally cannot stop it without the passphrase.
```

### Example 4: Set Up a Work Schedule

```bash
$ blockmydough schedule add \
    --name "work-hours" \
    --days mon,tue,wed,thu,fri \
    --from 09:00 \
    --to 17:00

✅ Schedule 'work-hours' created

   When active, these domains will be blocked:
   - All domains in your block list (15 domains)

   Schedule:
   ┌────────────────────────────────────────┐
   │ Mon  Tue  Wed  Thu  Fri  Sat  Sun      │
   │ ████ ████ ████ ████ ████ ░░░░ ░░░░     │
   │ 9am ──────────────────── 5pm           │
   └────────────────────────────────────────┘
```

### Example 5: Add a Domain While Blocking is Active

```bash
# You realize you also need to block Netflix
$ blockmydough add netflix.com

✅ Added netflix.com to block list
   Immediately applied - netflix.com is now blocked

$ blockmydough list

Blocked Domains (16):
  1. youtube.com        ⛔ ACTIVE
  2. www.youtube.com    ⛔ ACTIVE
  3. facebook.com       ⛔ ACTIVE
  4. netflix.com        ⛔ ACTIVE (just added)
  ...
```

### Example 6: Using Presets to Quickly Add Common Sites

```bash
# List available presets
$ blockmydough preset list

Available Presets:
  social       - Facebook, Twitter, Instagram, TikTok, Snapchat (12 domains)
  video        - YouTube, Netflix, Twitch, Disney+, Hulu (15 domains)
  news         - CNN, BBC, NYT, Reddit, HackerNews (20 domains)
  gaming       - Steam, Discord, Twitch, Reddit gaming subs (10 domains)
  shopping     - Amazon, eBay, Etsy, AliExpress (8 domains)
  all          - All of the above combined (65 domains)

$ blockmydough preset add social

✅ Added 12 domains from 'social' preset:
   - facebook.com
   - www.facebook.com
   - twitter.com
   - x.com
   - instagram.com
   - www.instagram.com
   - tiktok.com
   - www.tiktok.com
   - snapchat.com
   - web.snapchat.com
   - threads.net
   - www.threads.net

$ blockmydough preset add video

✅ Added 15 domains from 'video' preset
   (3 were already in your list, 12 new domains added)
```

---

## System Architecture

### How the Pieces Fit Together

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              YOUR COMPUTER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐         ┌──────────────────────────────────────────┐     │
│   │   Terminal   │         │          Background Daemon               │     │
│   │              │         │                                          │     │
│   │  blockmydough│ ──────► │  ┌────────────┐  ┌─────────────────┐     │     │
│   │  add youtube │  socket │  │   Socket   │  │  File Watcher   │     │     │
│   │              │         │  │   Server   │  │  (inotify)      │     │     │
│   └──────────────┘         │  └─────┬──────┘  └────────┬────────┘     │     │
│                            │        │                  │              │     │
│   ┌──────────────┐         │        ▼                  │              │     │
│   │   Browser    │         │  ┌────────────┐           │              │     │
│   │              │         │  │  Blocker   │ ◄─────────┘              │     │
│   │ youtube.com  │         │  │  Module    │  (re-apply if tampered)  │     │
│   │  = blocked!  │         │  └─────┬──────┘                          │     │
│   └──────┬───────┘         │        │                                 │     │
│          │                 └────────┼─────────────────────────────────┘     │
│          │                          │                                       │
│          │                          ▼                                       │
│          │                 ┌────────────────┐                               │
│          └────────────────►│  /etc/hosts    │                               │
│            DNS lookup      │                │                               │
│                            │ 127.0.0.1      │                               │
│                            │ youtube.com    │                               │
│                            └────────────────┘                               │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │                         systemd                                 │       │
│   │  blockmydough.service + watchdog = auto-restart if killed       │       │
│   └─────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What Happens When You Block a Domain

```
┌─────────┐      ┌─────────────┐      ┌──────────┐      ┌───────────┐
│  User   │      │     CLI     │      │  Daemon  │      │ /etc/hosts│
└────┬────┘      └──────┬──────┘      └────┬─────┘      └─────┬─────┘
     │                  │                  │                  │
     │  block --for 2h  │                  │                  │
     │─────────────────►│                  │                  │
     │                  │   Start block    │                  │
     │                  │─────────────────►│                  │
     │                  │                  │                  │
     │                  │                  │  Add entries     │
     │                  │                  │─────────────────►│
     │                  │                  │                  │
     │                  │                  │     127.0.0.1    │
     │                  │                  │     youtube.com  │
     │                  │                  │                  │
     │                  │      Success     │                  │
     │                  │◄─────────────────│                  │
     │    Blocking!     │                  │                  │
     │◄─────────────────│                  │                  │
     │                  │                  │                  │
```

### What Happens During Tampering

```
┌──────────┐      ┌───────────┐      ┌─────────┐      ┌──────────┐
│  Cheater │      │ /etc/hosts│      │ Watcher │      │  Daemon  │
└────┬─────┘      └─────┬─────┘      └────┬────┘      └────┬─────┘
     │                  │                 │                │
     │   sudo nano      │                 │                │
     │─────────────────►│                 │                │
     │                  │                 │                │
     │  delete blocks   │                 │                │
     │─────────────────►│                 │                │
     │                  │                 │                │
     │     save file    │  file changed!  │                │
     │─────────────────►│────────────────►│                │
     │                  │                 │                │
     │                  │                 │ blocks gone!   │
     │                  │                 │───────────────►│
     │                  │                 │                │
     │                  │    re-apply     │                │
     │                  │◄─────────────────────────────────│
     │                  │                 │                │
     │                  │  blocks back!   │                │
     │                  │                 │                │
     │                  │                 │                │
     │  tries youtube   │                 │                │
     │       ...        │                 │                │
     │  STILL BLOCKED!  │                 │                │
```

### Passphrase Protection Flow

<!-- CRITICAL: Added rate limiting to prevent brute force attacks on passphrase -->

```
                           ┌─────────────────────────────────┐
                           │   Protected Operations          │
                           │                                 │
                           │  • Stop daemon                  │
                           │  • Remove domain                │
                           │  • Cancel timer                 │
                           │  • Delete schedule              │
                           └────────────────┬────────────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │ Is block active?│
                                   └────────┬────────┘
                                            │
                        ┌───────────────────┼───────────────────┐
                        │ YES               │                NO │
                        ▼                   │                   ▼
               ┌─────────────────┐          │         ┌────────────────┐
               │ Check rate limit│          │         │ Allow operation│
               └───────┬─────────┘          │         └────────────────┘
                       │                    │
            ┌──────────┴──────────┐         │
            │                     │         │
        ALLOWED              LOCKED OUT     │
            │                     │         │
            ▼                     ▼         │
    ┌─────────────────┐  ┌──────────────┐   │
    │ Enter passphrase│  │ Wait X secs  │   │
    └───────┬─────────┘  │ (show timer) │   │
            │            └──────────────┘   │
            ▼                               │
    ┌────────────────┐                      │
    │ Verify hash    │                      │
    └───────┬────────┘                      │
            │                               │
    ┌───────┴───────┐                       │
    │               │                       │
 CORRECT          WRONG                     │
    │               │                       │
    ▼               ▼                       │
┌─────────┐  ┌─────────────────────┐        │
│ Allow   │  │ Increment fail count│        │
│ + reset │  │ + apply backoff     │        │
│ fails   │  └─────────────────────┘        │
└─────────┘                                 │
```

### Rate Limiting Specification

<!-- CRITICAL: Without rate limiting, passphrase can be brute-forced -->

The daemon tracks failed passphrase attempts and enforces exponential backoff.

> **Note:** Uses Unix epoch timestamps (`time.time()`) instead of `time.monotonic()`
> because `monotonic()` resets to zero on system reboot, which would allow an attacker
> to reboot and bypass rate limiting.

```python
# blockmydough/core/auth.py

from dataclasses import dataclass, field
from time import time

@dataclass
class RateLimitState:
    """
    Persisted in state.json under 'rate_limit' key.

    Uses Unix epoch timestamps for persistence across reboots.
    """
    failed_attempts: int = 0
    last_attempt_epoch: float = 0.0      # Unix timestamp
    lockout_until_epoch: float = 0.0     # Unix timestamp

class RateLimiter:
    """
    Exponential backoff for passphrase attempts.

    Backoff schedule:
      1 failure  → 2 second wait
      2 failures → 4 second wait
      3 failures → 8 second wait
      4 failures → 16 second wait
      5 failures → 32 second wait
      6+ failures → 60 second wait (capped)
    """

    BASE_DELAY_SECONDS = 2
    MAX_DELAY_SECONDS = 60
    RESET_AFTER_SECONDS = 300  # Reset counter after 5 min of no attempts

    def get_lockout_remaining(self, state: RateLimitState) -> float:
        """Returns seconds until next attempt allowed. 0 if allowed now."""
        now = time()
        if state.lockout_until_epoch > now:
            return state.lockout_until_epoch - now
        return 0.0

    def record_failure(self, state: RateLimitState) -> RateLimitState:
        """Record a failed attempt and calculate next lockout."""
        now = time()

        # Reset if enough time has passed
        if now - state.last_attempt_epoch > self.RESET_AFTER_SECONDS:
            state.failed_attempts = 0

        state.failed_attempts += 1
        state.last_attempt_epoch = now

        delay = min(
            self.BASE_DELAY_SECONDS * (2 ** (state.failed_attempts - 1)),
            self.MAX_DELAY_SECONDS
        )
        state.lockout_until_epoch = now + delay

        return state

    def record_success(self, state: RateLimitState) -> RateLimitState:
        """Reset rate limit state on successful auth."""
        return RateLimitState()  # Fresh state
```

---

## CLI Commands Reference

### Domain Management

| Command             | What It Does             | Example                              |
| ------------------- | ------------------------ | ------------------------------------ |
| `add <domain>`      | Add domain to block list | `blockmydough add youtube.com`       |
| `remove <domain>`   | Remove domain from list  | `blockmydough remove youtube.com` ⚠️ |
| `list`              | Show all blocked domains | `blockmydough list`                  |
| `preset list`       | Show available presets   | `blockmydough preset list`           |
| `preset add <name>` | Add preset to block list | `blockmydough preset add social`     |

⚠️ = Requires passphrase during active block

### Blocking Controls

| Command                | What It Does        | Example                            |
| ---------------------- | ------------------- | ---------------------------------- |
| `block --for <time>`   | Block for duration  | `blockmydough block --for 2h30m`   |
| `block --until <time>` | Block until time    | `blockmydough block --until 17:00` |
| `unblock`              | Cancel active block | `blockmydough unblock` ⚠️          |
| `status`               | Show current status | `blockmydough status`              |

### Schedule Management

| Command                 | What It Does        | Example                                       |
| ----------------------- | ------------------- | --------------------------------------------- |
| `schedule add`          | Create new schedule | See example above                             |
| `schedule list`         | List all schedules  | `blockmydough schedule list`                  |
| `schedule remove <id>`  | Delete a schedule   | `blockmydough schedule remove work-hours` ⚠️  |
| `schedule enable <id>`  | Enable a schedule   | `blockmydough schedule enable work-hours`     |
| `schedule disable <id>` | Disable temporarily | `blockmydough schedule disable work-hours` ⚠️ |

### Daemon Control

| Command   | What It Does     | Example                        |
| --------- | ---------------- | ------------------------------ |
| `start`   | Start the daemon | `sudo blockmydough start`      |
| `stop`    | Stop the daemon  | `sudo blockmydough stop` ⚠️    |
| `restart` | Restart daemon   | `sudo blockmydough restart` ⚠️ |

### Security

| Command             | What It Does          | Example                          |
| ------------------- | --------------------- | -------------------------------- |
| `passphrase set`    | Set/change passphrase | `blockmydough passphrase set`    |
| `passphrase verify` | Test your passphrase  | `blockmydough passphrase verify` |

---

## How /etc/hosts Blocking Works

When you block a domain, the daemon adds entries like this to `/etc/hosts`:

```
# Normal system entries
127.0.0.1   localhost
::1         localhost

# Start BlockMyDough Entries
127.0.0.1 youtube.com
::1       youtube.com
127.0.0.1 www.youtube.com
::1       www.youtube.com
127.0.0.1 facebook.com
::1       facebook.com
# End BlockMyDough Entries
```

**Why this works:**

-   When your browser asks "what is the IP for youtube.com?"
-   Linux checks `/etc/hosts` first before asking DNS
-   It finds `127.0.0.1` (localhost) for youtube.com
-   Browser tries to connect to localhost → nothing there → connection refused
-   You cannot access YouTube

### Immutable File Protection (chattr +i)

For stronger tamper protection, the daemon makes `/etc/hosts` immutable after applying blocks:

```python
# blockmydough/core/blocker.py

import subprocess

def set_immutable(path: str = "/etc/hosts") -> None:
    """Make file immutable - cannot be modified even by root."""
    subprocess.run(["chattr", "+i", path], check=True)

def clear_immutable(path: str = "/etc/hosts") -> None:
    """Remove immutable flag to allow modifications."""
    subprocess.run(["chattr", "-i", path], check=True)
```

**Flow when blocking:**

1. `chattr -i /etc/hosts` (remove immutable if set)
2. Write block entries to `/etc/hosts`
3. `chattr +i /etc/hosts` (make immutable again)

**Benefits:**

-   Even `sudo nano /etc/hosts` will fail with "Operation not permitted"
-   Attacker must know to run `chattr -i` first
-   inotify watcher still runs as backup (detects if someone removes immutable flag)

### Browser DNS Cache Warning

> ⚠️ **Important:** Changes to `/etc/hosts` may not take effect immediately due to
> browser DNS caching. If a site is still accessible after blocking:
>
> 1. **Close and reopen the browser** (fastest solution)
> 2. **Use private/incognito mode** (no cached DNS)
> 3. **Flush system DNS cache:** `sudo resolvectl flush-caches`
> 4. **Clear browser DNS cache:** `chrome://net-internals/#dns` → "Clear host cache"
>
> The daemon will display this warning when blocks are first applied.

---

## File Locations

| Path                                   | Purpose                                  | Permissions |
| -------------------------------------- | ---------------------------------------- | ----------- |
| `/usr/local/bin/blockmydough`          | CLI tool                                 | `0755`      |
| `/usr/local/bin/blockmydough-daemon`   | Background daemon                        | `0755`      |
| `/run/blockmydough/daemon.sock`        | Unix socket for CLI↔daemon communication | `0660`      |
| `/var/lib/blockmydough/state.json`     | Current state (timers, active blocks)    | `0600`      |
| `/var/lib/blockmydough/domains.txt`    | Your blocked domain list                 | `0644`      |
| `/var/lib/blockmydough/schedules.json` | Your saved schedules                     | `0600`      |
| `/var/lib/blockmydough/auth.key`       | Hashed passphrase (Argon2)               | `0600`      |
| `/var/log/blockmydough/daemon.log`     | Log file                                 | `0640`      |

**Note on permissions:**

-   `0600` = read/write for root only (sensitive files)
-   `0640` = read/write for root, read for group (logs)
-   `0644` = read/write for root, read for everyone (domain list is not sensitive)
-   `0660` = read/write for root and blockmydough group (socket access)

### State File Schema (state.json)

The daemon persists its runtime state to survive restarts:

```json
{
	"version": 1,
	"active_block": {
		"type": "timer",
		"started_at": "2025-01-15T10:00:00Z",
		"ends_at": "2025-01-15T12:00:00Z",
		"domains_count": 15,
		"triggered_by": "cli"
	},
	"rate_limit": {
		"failed_attempts": 2,
		"last_attempt_epoch": 1705320000.0,
		"lockout_until_epoch": 1705320004.0
	},
	"hosts_hash": "sha256:abc123...",
	"immutable_set": true
}
```

**Fields:**

| Field                        | Type                                | Description                                                |
| ---------------------------- | ----------------------------------- | ---------------------------------------------------------- |
| `version`                    | int                                 | Schema version for migrations                              |
| `active_block.type`          | `"timer"` \| `"schedule"` \| `null` | Current block type                                         |
| `active_block.started_at`    | ISO8601                             | When block started                                         |
| `active_block.ends_at`       | ISO8601 \| `null`                   | When block ends (null for schedule-based)                  |
| `active_block.domains_count` | int                                 | Number of domains currently blocked                        |
| `active_block.triggered_by`  | string                              | What started the block ("cli", schedule name)              |
| `rate_limit`                 | object                              | See RateLimitState above                                   |
| `hosts_hash`                 | string                              | SHA256 of expected /etc/hosts content for tamper detection |
| `immutable_set`              | bool                                | Whether chattr +i is currently applied                     |

---

## IPC Protocol (CLI ↔ Daemon)

Communication happens over a Unix domain socket using newline-delimited JSON messages.

### Wire Format

```
<JSON message>\n
```

Each message is a single JSON object followed by a newline. The connection is request-response: client sends one message, waits for one response.

### Message Types

```python
# blockmydough/ipc/messages.py

from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

# === Requests (CLI → Daemon) ===

class AddDomainRequest(BaseModel):
    type: Literal["add_domain"] = "add_domain"
    domain: str

class RemoveDomainRequest(BaseModel):
    type: Literal["remove_domain"] = "remove_domain"
    domain: str
    passphrase: Optional[str] = None  # Required if block active

class StartBlockRequest(BaseModel):
    type: Literal["start_block"] = "start_block"
    duration_seconds: Optional[int] = None  # --for
    until_time: Optional[str] = None        # --until (HH:MM)

class StopBlockRequest(BaseModel):
    type: Literal["stop_block"] = "stop_block"
    passphrase: str

class GetStatusRequest(BaseModel):
    type: Literal["get_status"] = "get_status"

class VerifyPassphraseRequest(BaseModel):
    type: Literal["verify_passphrase"] = "verify_passphrase"
    passphrase: str

# === Responses (Daemon → CLI) ===

class SuccessResponse(BaseModel):
    type: Literal["success"] = "success"
    message: str

class ErrorResponse(BaseModel):
    type: Literal["error"] = "error"
    code: str  # e.g., "PASSPHRASE_REQUIRED", "RATE_LIMITED", "INVALID_DOMAIN"
    message: str
    retry_after: Optional[float] = None  # Seconds until retry allowed

class StatusResponse(BaseModel):
    type: Literal["status"] = "status"
    blocking_active: bool
    block_type: Optional[str] = None  # "timer" | "schedule"
    ends_at: Optional[datetime] = None
    domains_count: int
    domains: list[str]
```

### Example Exchange

```
CLI → Daemon:
{"type": "start_block", "duration_seconds": 7200}

Daemon → CLI:
{"type": "success", "message": "Blocking 15 domains for 2 hours"}
```

```
CLI → Daemon:
{"type": "stop_block", "passphrase": "wrong-password"}

Daemon → CLI:
{"type": "error", "code": "INVALID_PASSPHRASE", "message": "Incorrect passphrase", "retry_after": 4.0}
```

---

## Emergency Recovery

If you forget your passphrase, you can recover the system by booting into recovery mode:

### Recovery Procedure

1. **Reboot into recovery mode**

    - Restart your computer
    - Hold `Shift` during boot to show GRUB menu (or press `Esc` on some systems)
    - Select "Advanced options" → "Recovery mode"
    - Choose "Drop to root shell"

2. **Remove BlockMyDough protection**

    ```bash
    # Remove immutable flag from hosts file
    chattr -i /etc/hosts

    # Remove BlockMyDough entries from hosts
    sed -i '/# Start BlockMyDough/,/# End BlockMyDough/d' /etc/hosts

    # Stop and disable the daemon
    systemctl disable blockmydough.service
    systemctl disable blockmydough-watchdog.service

    # Delete passphrase (forces re-setup)
    rm /var/lib/blockmydough/auth.key

    # Optionally, reset all state
    rm /var/lib/blockmydough/state.json
    ```

3. **Reboot normally**

    ```bash
    reboot
    ```

4. **Re-enable BlockMyDough with new passphrase**

    ```bash
    sudo systemctl enable blockmydough.service
    sudo blockmydough passphrase set
    sudo blockmydough start
    ```

### Alternative: Live USB

If you don't have recovery mode access:

1. Boot from a Linux live USB
2. Mount your root partition: `mount /dev/sda2 /mnt` (adjust device)
3. Run the same cleanup commands with paths prefixed: `chattr -i /mnt/etc/hosts`
4. Reboot into your normal system

> ⚠️ **Security Note:** This is intentionally difficult. The purpose of BlockMyDough
> is to prevent your impulsive self from bypassing blocks. The recovery process
> requires physical access and a reboot, giving you time to reconsider.

---

## Python Project Structure

Uses **uv** as the project manager and a **flat layout** (no `src/` wrapper) since this is a standalone CLI tool, not a library.

> **Current State vs Target:** The workspace currently has a legacy structure with
> `app/src/main.py`. Phase 1 of implementation will refactor this to the target
> structure shown below. The existing `app/pyproject.toml` and `app/uv.lock` files
> will be preserved.

### Why uv?

-   **Fast**: Written in Rust, installs packages 10-100x faster than pip
-   **Reproducible**: Creates `uv.lock` lockfile for consistent installs across machines
-   **Simple**: Replaces pip, pip-tools, virtualenv, and pyenv in one tool
-   **Standards-compliant**: Uses standard `pyproject.toml` for configuration

```
app/
├── pyproject.toml            # Project metadata and dependencies
├── uv.lock                   # Lockfile (commit to version control)
├── .python-version           # Python version constraint
├── .venv/                    # Virtual environment (auto-created, gitignored)
├── blockmydough/
│   ├── __init__.py
│   ├── constants.py              # Markers, paths, defaults
│   ├── exceptions.py             # Custom exceptions (PassphraseRequired, etc.)
│   │
│   ├── cli/                      # Command-line interface
│   │   ├── __init__.py
│   │   ├── app.py                # Typer app definition & entry point
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── domain.py         # add, remove, list
│   │       ├── block.py          # block, unblock, status
│   │       ├── schedule.py       # schedule add/remove/list
│   │       ├── preset.py         # preset list/add
│   │       ├── daemon.py         # start, stop, restart
│   │       └── passphrase.py     # passphrase set/verify
│   │
│   ├── daemon/                   # Background service
│   │   ├── __init__.py
│   │   ├── service.py            # Main daemon loop & entry point
│   │   ├── socket_server.py      # Unix socket handler
│   │   ├── watcher.py            # inotify /etc/hosts monitor
│   │   ├── scheduler.py          # Timer + schedule engine
│   │   └── notifier.py           # Desktop notifications via D-Bus
│   │
│   ├── core/                     # Shared business logic
│   │   ├── __init__.py
│   │   ├── blocker.py            # /etc/hosts manipulation
│   │   ├── domains.py            # Domain list management
│   │   ├── state.py              # State persistence (JSON)
│   │   ├── auth.py               # Argon2 passphrase hashing/verify
│   │   └── presets.py            # Built-in domain presets
│   │
│   └── ipc/                      # Inter-Process Communication
│       ├── __init__.py
│       ├── client.py             # CLI → Daemon requests
│       ├── messages.py           # Request/Response Pydantic models
│       └── handlers.py           # Daemon message handlers
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── test_blocker.py
│   ├── test_auth.py
│   └── test_domains.py
│
├── systemd/
│   ├── blockmydough.service      # Main daemon service
│   └── blockmydough-watchdog.service
│
└── scripts/
    ├── install.sh                # Installation script
    └── uninstall.sh
```

### Entry Points (in pyproject.toml)

```toml
[project.scripts]
blockmydough = "blockmydough.cli.app:main"
blockmydough-daemon = "blockmydough.daemon.service:main"
```

---

## Dependencies

```toml
[project]
dependencies = [
    "typer[all]>=0.9.0",     # CLI framework with rich support
    "rich>=13.0.0",          # Pretty terminal output
    "watchfiles>=0.21.0",    # Fast file watching with inotify
    "argon2-cffi>=23.1.0",   # Secure password hashing
    "pydantic>=2.5.0",       # Data validation
    "apscheduler>=3.10.0",   # Cron-like scheduling
    "sdnotify>=0.3.0",       # systemd integration
    "dbus-python>=1.3.2",    # Desktop notifications via D-Bus
]
```

---

## Desktop Notifications

The daemon will send desktop notifications for important events:

### Timer Expiry

```
┌─────────────────────────────────────────┐
│ 🔓 BlockMyDough                         │
│                                         │
│ Your 2-hour focus session has ended!    │
│ All 15 domains are now unblocked.       │
│                                         │
│ Great work staying focused! 🎉          │
└─────────────────────────────────────────┘
```

### Schedule Activation

```
┌─────────────────────────────────────────┐
│ 🔒 BlockMyDough                         │
│                                         │
│ Schedule 'work-hours' is now active.    │
│ 15 domains are blocked until 5:00 PM.   │
└─────────────────────────────────────────┘
```

### Tampering Detected

```
┌─────────────────────────────────────────┐
│ ⚠️ BlockMyDough                         │
│                                         │
│ Tampering detected!                     │
│ Someone tried to edit /etc/hosts.       │
│ Blocks have been re-applied.            │
│                                         │
│ Nice try 😏                             │
└─────────────────────────────────────────┘
```

Notifications use D-Bus to integrate with your desktop environment (GNOME, KDE, etc.)

---

## Implementation Plan

### Phase 1: Core Functionality

1. Refactor existing [`main.py`](app/src/main.py:1) into proper module structure
2. Implement domain storage (file-based, persistent)
3. Implement CLI with typer (add, remove, list, block, status)
4. Implement basic daemon with socket server

### Phase 2: Timer & Watcher

1. Implement duration-based blocking timer
2. Implement hosts file watcher with inotify
3. Implement automatic re-apply on tampering

### Phase 3: Security

1. Implement passphrase system with Argon2
2. Add passphrase requirement for protected operations
3. Implement systemd service with Restart=always

### Phase 4: Advanced Features

1. Implement schedule-based blocking
2. Implement watchdog helper process
3. Create install/uninstall scripts

### Phase 5: Polish

1. Add comprehensive logging
2. Add `--verbose` and `--quiet` flags
3. Write man page / documentation
4. Testing on Fedora

---

## Decisions Made

-   ✅ **Domain storage**: Simple text file (one domain per line)
-   ✅ **Default domains**: Empty list, but presets available to quickly add common sites
-   ✅ **Notifications**: All notifications enabled (timer expiry, schedule changes, tampering)
-   ✅ **IPC**: Unix socket-based communication
-   ✅ **Security**: Argon2 hashed passphrase, recovery requires boot to recovery mode
-   ✅ **Daemon protection**: systemd with Restart=always + watchdog helper
