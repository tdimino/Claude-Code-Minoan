"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.CrossWindowStateManager = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const STATE_FILE = path.join(os.homedir(), '.claude', 'vscode-tracker-state.json');
const STALE_WINDOW_MS = 30000; // 30 seconds - consider window dead if no update
/**
 * Manages cross-window terminal state via shared file
 */
class CrossWindowStateManager {
    constructor() {
        this.fileWatcher = null;
        this.updateCallback = null;
        this.currentTerminals = [];
        // Generate unique window ID using process ID and timestamp
        this.windowId = `${process.pid}-${Date.now()}`;
    }
    /**
     * Start tracking and watching for changes
     */
    activate(onUpdate) {
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
    deactivate() {
        if (this.fileWatcher) {
            this.fileWatcher.close();
            this.fileWatcher = null;
        }
        // Remove our window from state
        try {
            const state = this.readState();
            delete state.windows[this.windowId];
            this.writeState(state);
        }
        catch {
            // Ignore errors during cleanup
        }
    }
    /**
     * Update our window's terminal list
     */
    updateTerminals(terminals) {
        this.currentTerminals = terminals;
        this.updateState();
    }
    /**
     * Get total terminal count across all windows
     */
    getTotalCount() {
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
    getAllTerminals() {
        const state = this.readState();
        const now = Date.now();
        const terminals = [];
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
    startWatching() {
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
        }
        catch (err) {
            console.warn('Failed to watch cross-window state file:', err);
        }
    }
    updateState() {
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
        }
        catch (err) {
            console.warn('Failed to update cross-window state:', err);
        }
    }
    readState() {
        try {
            if (fs.existsSync(STATE_FILE)) {
                const content = fs.readFileSync(STATE_FILE, 'utf8');
                return JSON.parse(content);
            }
        }
        catch {
            // Ignore parse errors
        }
        return { windows: {} };
    }
    writeState(state) {
        fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
    }
    /**
     * Send periodic heartbeat to keep our window marked as alive
     */
    startHeartbeat() {
        const interval = setInterval(() => {
            this.updateState();
        }, 10000); // Every 10 seconds
        return {
            dispose: () => clearInterval(interval),
        };
    }
}
exports.CrossWindowStateManager = CrossWindowStateManager;
//# sourceMappingURL=crossWindowState.js.map