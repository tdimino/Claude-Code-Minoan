import * as vscode from 'vscode';
import type { TrackedSession } from './types';
import { getCurrentWorkspacePath } from './utils';

const STORAGE_KEY = 'claudeSessions';
const MAX_SESSIONS = 50;

/**
 * Manages persistence of tracked Claude Code sessions
 */
export class SessionStorage {
  constructor(private context: vscode.ExtensionContext) {}

  /**
   * Get all tracked sessions, sorted by most recent first
   */
  getRecentSessions(): TrackedSession[] {
    const sessions = this.context.globalState.get<TrackedSession[]>(STORAGE_KEY, []);
    return sessions.sort((a, b) =>
      new Date(b.startedAt).getTime() - new Date(a.startedAt).getTime()
    );
  }

  /**
   * Get resumable sessions for a specific project
   */
  getResumableForProject(projectPath: string): TrackedSession | undefined {
    const sessions = this.getRecentSessions();
    return sessions.find(s => s.projectPath === projectPath && s.isResumable);
  }

  /**
   * Track a new Claude Code session
   */
  async trackSession(session: Omit<TrackedSession, 'startedAt' | 'isResumable'>): Promise<void> {
    const sessions = this.getRecentSessions();

    const newSession: TrackedSession = {
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
  private async updateSession(
    projectPath: string,
    updates: Partial<TrackedSession>
  ): Promise<void> {
    const sessions = this.getRecentSessions();
    const updated = sessions.map(s =>
      s.projectPath === projectPath ? { ...s, ...updates } : s
    );
    await this.context.globalState.update(STORAGE_KEY, updated);
  }

  /**
   * Mark a session as closed (still resumable)
   */
  async markClosed(projectPath: string): Promise<void> {
    await this.updateSession(projectPath, {
      closedAt: new Date().toISOString(),
      isResumable: true,
    });
  }

  /**
   * Mark a session as no longer resumable (e.g., after successful resume)
   */
  async clearResumable(projectPath: string): Promise<void> {
    await this.updateSession(projectPath, { isResumable: false });
  }

  /**
   * Check if any resumable session exists for current workspace
   */
  hasResumableSession(): boolean {
    const workspacePath = getCurrentWorkspacePath();
    if (!workspacePath) return false;

    return this.getResumableForProject(workspacePath) !== undefined;
  }
}
