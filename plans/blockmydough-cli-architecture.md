# BlockMyDough CLI Daemon Architecture

## What This Tool Does

BlockMyDough is a **self-control tool** that blocks distracting websites by modifying `/etc/hosts`. Key features include:

1. **Domain blocking** - Permanently block specified domains.
2. **Schedule-based blocking** - e.g., "Block social media Mon–Fri, 9 AM – 5 PM."
3. **Timer-based blocking** - e.g., "Block social media for 1 hour."
4. **Tamper protection** - If someone edits `/etc/hosts` to remove blocks, the daemon instantly re-applies them.
5. **Passphrase protection** - Prevents stopping the block or removing domains without a passphrase.

---

## CLI Commands Reference

Commands marked with **⚠️** require your passphrase if a block is currently active to prevent impulsive bypassing.

### 🌐 Domain Management

Manage your global list of blocked domains.

#### `domain add`

Add a new domain to your permanent block list.

-   **Usage**: `bmd domain add <domain>`
-   **Arguments**:
    -   `<domain>`: Comma-separated domains to block (e.g. `reddit.com,x.com` or `x.com`).
-   **Example**: `bmd domain add x.com`

#### `domain remove` **⚠️**

Remove a domain from your permanent block list.

-   **Usage**: `bmd domain remove <domain>`
-   **Arguments**:
    -   `<domain>`: Comma-separated domains to unblock (e.g. `reddit.com,x.com` or `x.com`).
-   **Example**: `bmd domain remove x.com`

#### `domain list`

Display all domains currently in your permanent block list.

-   **Usage**: `bmd domain list`

---

### 📋 Preset Management

Manage groups of domains (e.g., "social", "gaming") for quick blocking.

#### `preset list`

Show all available built-in and custom presets.

-   **Usage**: `bmd preset list`

#### `preset create`

Create a new empty preset.

-   **Usage**: `bmd preset create <name>`
-   **Arguments**:
-   `<name>`: Unique name for the new preset.
-   **Example**: `bmd preset create deep-work`

#### `preset add`

Add domain(s) to preset

-   **Usage**: `bmd preset add --preset <preset> --domain <domain>`
-   **Flags**:
    -   `-p`,`--preset`: [Required]: Selected preset (e.g. `deep-work`).
    -   `-d`,`--domain`: [Required]: Comma-separated days (e.g., `youtube.com,x.com` or `youtube.com`).
-   **Example**: `bmd preset add -p deep-work -d youtube.com,x.com`

---

### ⏳ Block Timer

Start or manage temporary blocking sessions.

#### `block`

Start a timed block session for a specific preset.

-   **Usage**: `bmd block <preset> [--dur <minutes>]`
-   **Arguments**:
    -   `<preset>`: The name of the preset to block.
-   **Flags**:
    -   `-d`, `--dur` [Optional]: Duration in minutes (Default: `20`).
-   **Example**: `bmd block social --dur 60` (Starts a 1-hour block)

#### `block stop` **⚠️**

Immediately end an active timed block session.

-   **Usage**: `bmd block stop`
-   **Example**: `bmd block stop`

---

### 📅 Schedule Management

Configure recurring blocking windows (e.g., "Work Hours").

#### `schedule add`

Create a new recurring schedule for a preset.

-   **Usage**: `bmd schedule add <preset> --name <name> --days <days> --from <start> --to <end>`
-   **Arguments**:
    -   `<preset>`: The preset to apply during this schedule.
-   **Flags**:
    -   `-n`, `--name` [Required]: A descriptive name (e.g., `work-hours`).
    -   `-dy`, `--days` [Required]: Comma-separated days (e.g., `mon,tue,wed` or `mon`).
    -   `-f`, `--from` [Required]: Start time in 24h format (e.g., `09:00`).
    -   `-t`, `--to` [Required]: End time in 24h format (e.g., `17:00`).
-   **Example**: `bmd schedule add social --name focus-morning --days mon,wed,fri --from 08:30 --to 11:30`

#### `schedule list`

List all active and configured schedules.

-   **Usage**: `bmd schedule list`
-   **Example**: `bmd schedule list`

#### `schedule remove` **⚠️**

Delete a specific schedule.

-   **Usage**: `bmd schedule remove <id_or_name>`
-   **Arguments**:
    -   `<id_or_name>`: The ID or name of the schedule to delete.
-   **Example**: `bmd schedule remove focus-morning`

---

### ⚙️ Daemon Control

Manage the background service that enforces the blocks.

#### `start`

Start the BlockMyDough daemon.

-   **Usage**: `sudo bmd start`
-   **Example**: `sudo bmd start`

#### `stop` **⚠️**

Gracefully stop the background daemon.

-   **Usage**: `sudo bmd stop`
-   **Example**: `sudo bmd stop`

---

### 🔒 Security

Manage your protection passphrase.

#### `passphrase set`

Create or update your security passphrase.

-   **Usage**: `bmd passphrase set`
-   **Example**: `bmd passphrase set`

#### `passphrase verify`

Test your currently set passphrase.

-   **Usage**: `bmd passphrase verify`
-   **Example**: `bmd passphrase verify`

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

---

## How /etc/hosts Blocking Works

When you block a domain, the daemon adds entries like this to `/etc/hosts`:

```
# Normal system entries
127.0.0.1   localhost
::1         localhost

# Permanent Blocks - BlockMyDough
# <perm>
127.0.0.1 youtube.com
::1       youtube.com
127.0.0.1 www.youtube.com
::1       www.youtube.com
127.0.0.1 facebook.com
::1       facebook.com
# </perm>

# Schedule Blocks - BlockMyDough
# <schedule>
127.0.0.1 netflix.com
::1       netflix.com
127.0.0.1 www.netflix.com
::1       www.netflix.com
127.0.0.1 amazon.com
::1       amazon.com
# </schedule>

# Timer Blocks - BlockMyDough
# <timer>
127.0.0.1 netflix.com
::1       netflix.com
127.0.0.1 www.netflix.com
::1       www.netflix.com
127.0.0.1 amazon.com
::1       amazon.com
# </timer>
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

### Phase 1: Project Skeleton & Basic CLI

_Goal: Establish the project structure and manage the domain list._

1. **Project Structure**:
    - Refactor `app/` to flat layout with `blockmydough/` package.
    - Initialize `core`, `cli`, `daemon`, `ipc` subpackages.
    - Update `pyproject.toml` with dependencies (`typer`, `rich`, `pydantic`).
2. **Core Logic**:
    - Implement `core/domains.py` for file-based domain storage (`domains.txt`).
    - Implement `core/presets.py` for predefined lists.
3. **CLI (Part 1)**:
    - Implement `cli/app.py` entry point.
    - Implement `cli/commands/domain.py` (`add`, `remove`, `list`).
    - Implement `cli/commands/preset.py`.

### Phase 2: Daemon Infrastructure & IPC

_Goal: Get the daemon running and communicating with the CLI._

1. **State Management**:
    - Implement `core/state.py` handling `state.json` with Pydantic.
    - Ensure thread-safe state updates.
2. **IPC Protocol**:
    - Define request/response models in `ipc/messages.py` (`StartBlockRequest`, `StatusResponse`, etc.).
3. **Daemon Socket Server**:
    - Implement `daemon/socket_server.py` (asyncio Unix socket server).
    - Implement `ipc/client.py` for CLI communication.
4. **Daemon Control**:
    - Implement `daemon/service.py` main loop.
    - Implement `cli/commands/daemon.py` (`start`, `stop`, `restart`, `status`).

### Phase 3: Blocking Engine & Tamper Protection

_Goal: Implement the actual blocking capability and ensure it stays._

1. **Blocker Module**:
    - Implement `core/blocker.py` to modify `/etc/hosts`.
    - Implement `chattr +i` toggle for immutable protection.
2. **File Watcher**:
    - Implement `daemon/watcher.py` using `watchfiles` (inotify).
    - Detect external modifications to `/etc/hosts`.
3. **Auto-Healing**:
    - Wire watcher to `core/blocker.py` to re-apply blocks instantly upon tampering detection.
4. **Timer System**:
    - Implement duration-based blocking in `daemon/service.py` (or `scheduler.py`).
    - Implement CLI `block --for` command.

### Phase 4: Security & Authentication

_Goal: Lock down the system so it can't be bypassed lightly._

1. **Passphrase Core**:
    - Implement `core/auth.py` using `argon2-cffi`.
    - Implement `cli/commands/passphrase.py` (`set`, `verify`).
2. **Rate Limiting**:
    - Implement exponential backoff logic in `core/auth.py`.
    - Persist lockout state in `state.json`.
3. **Enforcement**:
    - Update `ipc/handlers.py` to enforce authentication for restricted actions (stop, remove domain, etc.).
    - Verify rate limits before verifying passphrases.

### Phase 5: Advanced Features & Polish

_Goal: Schedules, notifications, and system integration._

1. **Scheduler**:
    - Implement `daemon/scheduler.py` using `apscheduler` for recurring blocks.
    - Implement `cli/commands/schedule.py`.
2. **Notifications**:
    - Implement `daemon/notifier.py` using `dbus-python`.
    - Send alerts for timer expiry and tampering events.
3. **Systemd Integration**:
    - Refine `blockmydough.service` (Restart=always).
    - Implement `sdnotify` keep-alive.
    - Create `blockmydough-watchdog.service`.
4. **Install/Uninstall**:
    - Finalize `scripts/install.sh` (permissions, groups, systemd enablement).

### Phase 6: Testing & Cleanup

_Goal: Final verification._

1. **Logging**: Ensure consistent structured logging across the daemon.
2. **Documentation**: Update README and help texts.
3. **End-to-End Testing**:
    - Verify tamper protection with `chattr` active.
    - Verify rate limiting persistence across restarts.
    - Verify browser cache warning display.

---

## Decisions Made

-   ✅ **Domain storage**: Simple text file (one domain per line)
-   ✅ **Default domains**: Empty list, but presets available to quickly add common sites
-   ✅ **Notifications**: All notifications enabled (timer expiry, schedule changes, tampering)
-   ✅ **IPC**: Unix socket-based communication
-   ✅ **Security**: Argon2 hashed passphrase, recovery requires boot to recovery mode
-   ✅ **Daemon protection**: systemd with Restart=always + watchdog helper
