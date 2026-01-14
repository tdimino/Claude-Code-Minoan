"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SessionStorage = void 0;
const utils_1 = require("./utils");
const STORAGE_KEY = 'claudeSessions';
const MAX_SESSIONS = 50;
/**
 * Manages persistence of tracked Claude Code sessions
 */
class SessionStorage {
    constructor(context) {
        this.context = context;
    }
    /**
     * Get all tracked sessions, sorted by most recent first
     */
    getRecentSessions() {
        const sessions = this.context.globalState.get(STORAGE_KEY, []);
        return sessions.sort((a, b) => new Date(b.startedAt).getTime() - new Date(a.startedAt).getTime());
    }
    /**
     * Get resumable sessions for a specific project
     */
    getResumableForProject(projectPath) {
        const sessions = this.getRecentSessions();
        return sessions.find(s => s.projectPath === projectPath && s.isResumable);
    }
    /**
     * Track a new Claude Code session
     */
    async trackSession(session) {
        const sessions = this.getRecentSessions();
        const newSession = {
            ...session,
            startedAt: new Date().toISOString(),
            isResumable: true,
        };
        // Remove any existing session for this project path
        const filtered = sessions.filter(s => s.projectPath !== session.projectPath);
        // Add new session at the front
        const updated = [newSession, ...filtered].slice(0, MAX_SESSIONS);
        await this.context.globalState.update(STORAGE_KEY, updated);
    }
    /**
     * Update a session by project path
     */
    async updateSession(projectPath, updates) {
        const sessions = this.getRecentSessions();
        const updated = sessions.map(s => s.projectPath === projectPath ? { ...s, ...updates } : s);
        await this.context.globalState.update(STORAGE_KEY, updated);
    }
    /**
     * Mark a session as closed (still resumable)
     */
    async markClosed(projectPath) {
        await this.updateSession(projectPath, {
            closedAt: new Date().toISOString(),
            isResumable: true,
        });
    }
    /**
     * Mark a session as no longer resumable (e.g., after successful resume)
     */
    async clearResumable(projectPath) {
        await this.updateSession(projectPath, { isResumable: false });
    }
    /**
     * Check if any resumable session exists for current workspace
     */
    hasResumableSession() {
        const workspacePath = (0, utils_1.getCurrentWorkspacePath)();
        if (!workspacePath)
            return false;
        return this.getResumableForProject(workspacePath) !== undefined;
    }
}
exports.SessionStorage = SessionStorage;
//# sourceMappingURL=sessionStorage.js.map