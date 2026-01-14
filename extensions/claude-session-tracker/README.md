# Claude Session Tracker

VS Code extension to track and resume Claude Code sessions after crashes or disconnections.

## Features

- **Cross-Window Tracking**: See total Claude sessions across ALL VS Code windows (e.g., "Claude Active (7)")
- **Automatic Detection**: Recognizes terminals running Claude Code via name matching and process inspection
- **Multi-Root Workspace Support**: Tracks sessions for all workspace folders, not just the first
- **Status Bar Indicator**: Shows when Claude is active or resumable with count across all windows
- **Quick Resume**: `Cmd+Shift+C` to instantly resume your last session
- **Session Picker**: Browse and resume from recent sessions with git branch info
- **Global Session Browser**: Browse sessions across ALL projects, not just current workspace
- **Crash Recovery**: Easily resume work after VS Code crashes or restarts
- **Robust Git Branch Detection**: Handles detached HEAD, timeouts, and non-git directories

## Commands

| Command | Keybinding | Description |
|---------|------------|-------------|
| Resume Last Claude Session | `Cmd+Shift+C` | Resume the most recent session for this workspace |
| Pick Claude Session | — | Browse recent sessions and choose one to resume |
| Show Recent Claude Sessions | — | Same as Pick Session |
| Focus Active Claude Terminal | — | Focus or pick from active Claude terminals in this window |
| Show All Terminals | — | List all terminals in the current VS Code window |
| Browse All Claude Sessions | — | Browse recent sessions across ALL projects |

## How It Works

1. When you run `claude` in a VS Code terminal, the extension detects it
2. **Cross-window state** is shared via `~/.claude/vscode-tracker-state.json`
3. Status bar shows total Claude sessions across ALL VS Code windows
4. If VS Code closes or crashes, the session is marked as "resumable"
5. When you reopen VS Code, the status bar shows "Resume Claude"
6. Press `Cmd+Shift+C` or click the status bar to resume where you left off

### Cross-Window Tracking

Each VS Code window runs its own extension instance, but they communicate via a shared state file:

- **State File**: `~/.claude/vscode-tracker-state.json`
- **Heartbeat**: Every 10 seconds, each window updates its status
- **Stale Cleanup**: Windows that don't update for 30 seconds are considered closed
- **Tooltip Info**: Hover over status bar to see distribution (e.g., "4 in this window, 3 in other window(s)")

Under the hood, this uses Claude Code's built-in `--continue` and `--resume` flags:
- `claude --continue` — Resume most recent session for current directory
- `claude --resume <sessionId>` — Resume a specific session

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `claudeTracker.autoResume` | `false` | Prompt to resume on workspace open |
| `claudeTracker.showStatusBar` | `true` | Show Claude status in status bar |

## Session Storage

Claude Code stores sessions in `~/.claude/projects/` as JSONL files. Each workspace has its own folder with session UUIDs. This extension reads (but never writes to) these files to show session previews.

## Known Limitations

- **Windows Support**: Process detection for custom terminal names is limited on Windows (uses WMIC which may be deprecated)
- **Process Detection Timing**: Claude must be running when the terminal is detected; if started later, may not be tracked until next poll

## Requirements

- VS Code 1.85.0+
- Claude Code CLI installed and in PATH

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode
npm run watch

# Package extension
npx vsce package
```

## License

MIT
