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
           ┌─────────────────┐          │          ┌────────────────┐
           │ Enter passphrase│          │          │ Allow operation│
           └───────┬─────────┘          │          └────────────────┘
                   │                    │
                   ▼                    │
          ┌────────────────┐            │
          │ Verify hash    │            │
          └───────┬────────┘            │
                  │                     │
       ┌──────────┴──────────┐          │
       │                     │          │
    CORRECT                WRONG        │
       │                     │          │
       ▼                     ▼          │
┌────────────┐      ┌────────────┐      │
│   Allow    │      │    Deny    │      │
│ operation  │      │ operation  │      │
└────────────┘      └────────────┘      │
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

---

## File Locations

| Path                                   | Purpose                                  |
| -------------------------------------- | ---------------------------------------- |
| `/usr/local/bin/blockmydough`          | CLI tool                                 |
| `/usr/local/bin/blockmydough-daemon`   | Background daemon                        |
| `/run/blockmydough/daemon.sock`        | Unix socket for CLI↔daemon communication |
| `/var/lib/blockmydough/state.json`     | Current state (timers, active blocks)    |
| `/var/lib/blockmydough/domains.txt`    | Your blocked domain list                 |
| `/var/lib/blockmydough/schedules.json` | Your saved schedules                     |
| `/var/lib/blockmydough/auth.key`       | Hashed passphrase (Argon2)               |
| `/var/log/blockmydough/daemon.log`     | Log file                                 |

---

## Python Project Structure

```
app/
├── pyproject.toml
├── src/
│   └── blockmydough/
│       ├── __init__.py
│       │
│       ├── cli/                    # Command-line interface
│       │   ├── __init__.py
│       │   ├── main.py             # Entry point: typer app
│       │   └── commands/
│       │       ├── domain.py       # add, remove, list commands
│       │       ├── block.py        # block, unblock, status
│       │       ├── schedule.py     # schedule add/remove/list
│       │       ├── preset.py       # preset list/add commands
│       │       └── security.py     # passphrase set/verify
│       │
│       ├── daemon/                 # Background service
│       │   ├── __init__.py
│       │   ├── main.py             # Daemon entry point
│       │   ├── server.py           # Unix socket server
│       │   ├── watcher.py          # inotify hosts file monitor
│       │   ├── scheduler.py        # Timer + schedule engine
│       │   ├── notifier.py         # Desktop notifications via D-Bus
│       │   └── watchdog.py         # Watchdog helper process
│       │
│       ├── core/                   # Shared business logic
│       │   ├── blocker.py          # /etc/hosts manipulation
│       │   ├── state.py            # State persistence
│       │   ├── auth.py             # Passphrase hashing/verify
│       │   ├── presets.py          # Built-in domain presets
│       │   └── config.py           # Configuration
│       │
│       └── protocol/               # CLI↔Daemon communication
│           └── messages.py         # JSON message formats
│
├── systemd/
│   ├── blockmydough.service        # Main daemon service
│   └── blockmydough-watchdog.service
│
└── scripts/
    ├── install.sh                  # Installation script
    └── uninstall.sh
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
