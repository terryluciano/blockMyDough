# BlockMyDough

BlockMyDough is a simple, humorous productivity tool designed to help you stay focused by blocking distracting websites. It works by modifying your system's hosts file to prevent access to specified domains, while delivering "motivational" (read: snarky) messages to keep you in check.

## Features

-   **Website Blocking**: Blocks access to a configurable list of distracting websites (e.g., social media, entertainment sites).
-   **Safety First**: Automatically creates a backup of your original `/etc/hosts` file before making any changes.
-   **"Motivational" Messages**: Displays random, humorous, and slightly insulting messages to discourage procrastination and remind you to get back to work.

## Requirements

-   [uv](https://github.com/astral-sh/uv) project manager
-   Python 3.14 or higher (managed automatically by uv)
-   Root/Administrator privileges (required to modify `/etc/hosts`)
-   Linux/Unix environment (currently designed for `/etc/hosts`)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/terryluciano/blockMyDough.git
    cd blockMyDough
    ```

2. Sync the project dependencies:

    ```bash
    uv sync
    ```

## Usage

To run the blocker, execute the script using `uv` with root privileges:

```bash
sudo uv run main.py
```

The script will:

1. Display a random message to question your life choices.
2. Backup your current `/etc/hosts` file to `data/hosts.backup`.
3. Apply the blocking rules (implementation in progress).

## Disclaimer

This tool modifies system files (`/etc/hosts`). While it creates a backup, please use it with caution. The author is not responsible for any lost data or broken internet configurations.
