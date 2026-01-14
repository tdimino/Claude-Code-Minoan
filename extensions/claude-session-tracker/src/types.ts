/**
 * Tracked Claude Code session metadata
 */
export interface TrackedSession {
  /** Absolute path to the project directory */
  projectPath: string;
  /** Terminal name when session was active */
  terminalName: string;
  /** ISO timestamp when session started */
  startedAt: string;
  /** ISO timestamp when terminal was closed (if applicable) */
  closedAt?: string;
  /** Whether this session can be resumed */
  isResumable: boolean;
  /** Git branch at time of session (if available) */
  gitBranch?: string;
}

/**
 * Session data parsed from Claude's JSONL files
 */
export interface ClaudeSessionFile {
  sessionId: string;
  cwd: string;
  gitBranch?: string;
  version: string;
  timestamp: string;
  type: 'user' | 'assistant';
  message?: {
    role: string;
    content: string;
  };
}

/**
 * Session summary for quick pick display
 */
export interface SessionSummary {
  id: string;
  projectPath: string;
  firstMessage: string;
  timestamp: string;
  gitBranch?: string;
}
