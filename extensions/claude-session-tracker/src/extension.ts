import * as vscode from 'vscode';
import { SessionStorage } from './sessionStorage';
import { StatusBarManager } from './statusBar';
import { TerminalWatcher } from './terminalWatcher';
import { registerCommands } from './commands';
import { isAutoResumeEnabled } from './utils';

/**
 * Claude Session Tracker Extension
 *
 * Tracks VS Code terminals running Claude Code and enables easy session
 * resumption after crashes or disconnections.
 *
 * Features:
 * - Detects Claude Code terminals automatically
 * - Shows status bar indicator when sessions are active/resumable
 * - Cmd+Shift+C to quickly resume last session
 * - Session picker to choose from recent sessions
 */
export function activate(context: vscode.ExtensionContext): void {
  console.log('Claude Session Tracker activating...');

  // Initialize components
  const storage = new SessionStorage(context);
  const statusBar = new StatusBarManager(context);
  const watcher = new TerminalWatcher(context, storage, statusBar);

  // Start watching terminals first (so watcher has terminals tracked)
  watcher.activate();

  // Register commands (pass watcher for focusTerminal)
  registerCommands(context, storage, watcher);

  // Check for auto-resume on activation
  if (isAutoResumeEnabled() && storage.hasResumableSession()) {
    vscode.window.showInformationMessage(
      'A previous Claude session can be resumed.',
      'Resume',
      'Dismiss'
    ).then(
      action => {
        if (action === 'Resume') {
          vscode.commands.executeCommand('claude-tracker.resumeLast')
            .then(undefined, err => {
              console.error('Failed to auto-resume session:', err);
              vscode.window.showErrorMessage('Failed to resume Claude session');
            });
        }
        // action is undefined if user dismissed (Escape/click outside)
      },
      err => {
        // Actual API error (rare) - not user dismissal
        console.error('Auto-resume notification API error:', err);
      }
    );
  }

  // Update status bar on activation
  if (storage.hasResumableSession()) {
    statusBar.showResumable();
  }

  console.log('Claude Session Tracker activated');
}

export function deactivate(): void {
  console.log('Claude Session Tracker deactivated');
}
