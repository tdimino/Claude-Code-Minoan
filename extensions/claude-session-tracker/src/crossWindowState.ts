import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

/**
 * Shared state file format for cross-window terminal tracking
 */
interface WindowState {
  windowId: string;
  pid: number;
  lastUpdate: number;
  terminals: {
    name: string;
    workspacePath: string;
  }[];
}

interface CrossWindowState {
  windows: Record<string, WindowState>;
}

const STATE_FILE = path.join(os.homedir(), '.claude', 'vscode-tracker-state.json');
const STALE_WINDOW_MS = 30000; // 30 seconds - consider window dead if no update

/**
 * Manages cross-window terminal state via shared file
 */
export class CrossWindowStateManager {
  private windowId: string;
  private fileWatcher: fs.FSWatcher | null = null;
  private updateCallback: ((totalCount: number) => void) | null = null;
  private currentTerminals: { name: string; workspacePath: string }[] = [];

  constructor() {
    // Generate unique window ID using process ID and timestamp
    this.windowId = `${process.pid}-${Date.now()}`;
  }

  /**
   * Start tracking and watching for changes
   */
  activate(onUpdate: (totalCount: number) => void): void {
    this.updateCallback = onUpdate;

    // Ensure .claude directory exists
    const claudeDir = path.dirname(STATE_FILE);
    if (!fs.existsSync(claudeDir)) {
      fs.mkdirSync(claudeDir, { recursive: true });
    }

    // Watch for file changes from other windows
    this.startWatching();

    // Clean up stale windows and broadcast initial state
    this.updateState();
  }

  /**
   * Stop watching and clean up our window's state
   */
  deactivate(): void {
    if (this.fileWatcher) {
      this.fileWatcher.close();
      this.fileWatcher = null;
    }

    // Remove our window from state
    try {
      const state = this.readState();
      delete state.windows[this.windowId];
      this.writeState(state);
    } catch {
      // Ignore errors during cleanup
    }
  }

  /**
   * Update our window's terminal list
   */
  updateTerminals(terminals: { name: string; workspacePath: string }[]): void {
    this.currentTerminals = terminals;
    this.updateState();
  }

  /**
   * Get total terminal count across all windows
   */
  getTotalCount(): number {
    const state = this.readState();
    const now = Date.now();
    let total = 0;

    for (const [windowId, windowState] of Object.entries(state.windows)) {
      // Skip stale windows (hasn't updated in 30 seconds)
      if (now - windowState.lastUpdate > STALE_WINDOW_MS) {
        continue;
      }
      total += windowState.terminals.length;
    }

    return total;
  }

  /**
   * Get all terminals across all windows
   */
  getAllTerminals(): { name: string; workspacePath: string; windowId: string }[] {
    const state = this.readState();
    const now = Date.now();
    const terminals: { name: string; workspacePath: string; windowId: string }[] = [];

    for (const [windowId, windowState] of Object.entries(state.windows)) {
      if (now - windowState.lastUpdate > STALE_WINDOW_MS) {
        continue;
      }
      for (const terminal of windowState.terminals) {
        terminals.push({ ...terminal, windowId });
      }
    }

    return terminals;
  }

  private startWatching(): void {
    try {
      // Create file if it doesn't exist
      if (!fs.existsSync(STATE_FILE)) {
        this.writeState({ windows: {} });
      }

      this.fileWatcher = fs.watch(STATE_FILE, (eventType) => {
        if (eventType === 'change') {
          // Debounce to avoid rapid updates
          setTimeout(() => {
            const total = this.getTotalCount();
            this.updateCallback?.(total);
          }, 100);
        }
      });
    } catch (err) {
      console.warn('Failed to watch cross-window state file:', err);
    }
  }

  private updateState(): void {
    try {
      const state = this.readState();
      const now = Date.now();

      // Clean up stale windows
      for (const [windowId, windowState] of Object.entries(state.windows)) {
        if (now - windowState.lastUpdate > STALE_WINDOW_MS && windowId !== this.windowId) {
          delete state.windows[windowId];
        }
      }

      // Update our window's state
      state.windows[this.windowId] = {
        windowId: this.windowId,
        pid: process.pid,
        lastUpdate: now,
        terminals: this.currentTerminals,
      };

      this.writeState(state);

      // Notify callback of new total
      const total = this.getTotalCount();
      this.updateCallback?.(total);
    } catch (err) {
      console.warn('Failed to update cross-window state:', err);
    }
  }

  private readState(): CrossWindowState {
    try {
      if (fs.existsSync(STATE_FILE)) {
        const content = fs.readFileSync(STATE_FILE, 'utf8');
        return JSON.parse(content) as CrossWindowState;
      }
    } catch {
      // Ignore parse errors
    }
    return { windows: {} };
  }

  private writeState(state: CrossWindowState): void {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
  }

  /**
   * Send periodic heartbeat to keep our window marked as alive
   */
  startHeartbeat(): vscode.Disposable {
    const interval = setInterval(() => {
      this.updateState();
    }, 10000); // Every 10 seconds

    return {
      dispose: () => clearInterval(interval),
    };
  }
}
