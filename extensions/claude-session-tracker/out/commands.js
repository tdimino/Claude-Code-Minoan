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
exports.registerCommands = registerCommands;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const readline = __importStar(require("readline"));
const utils_1 = require("./utils");
/**
 * Register all extension commands
 */
function registerCommands(context, storage, watcher) {
    // Focus active Claude terminal
    context.subscriptions.push(vscode.commands.registerCommand('claude-tracker.focusTerminal', async () => {
        const activeTerminals = watcher.getActiveTerminals();
        if (activeTerminals.length === 0) {
            vscode.window.showInformationMessage('No active Claude terminals');
            return;
        }
        if (activeTerminals.length === 1) {
            // Single terminal - focus it directly
            activeTerminals[0].show();
            return;
        }
        // Multiple terminals - show picker
        const items = activeTerminals.map((terminal, index) => ({
            label: terminal.name,
            description: `Terminal ${index + 1}`,
            terminal,
        }));
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select Claude terminal to focus',
        });
        if (selected) {
            selected.terminal.show();
        }
    }));
    // Show all terminals in this VS Code window
    context.subscriptions.push(vscode.commands.registerCommand('claude-tracker.showAllTerminals', async () => {
        const allTerminals = vscode.window.terminals;
        const claudeTerminals = watcher.getActiveTerminals();
        if (allTerminals.length === 0) {
            vscode.window.showInformationMessage('No terminals open in this window');
            return;
        }
        const items = allTerminals.map((terminal) => {
            const isClaude = claudeTerminals.includes(terminal);
            return {
                label: `${isClaude ? '$(terminal-tmux) ' : '$(terminal) '}${terminal.name}`,
                description: isClaude ? 'Claude Code' : '',
                detail: `PID: ${terminal.processId || 'unknown'}`,
                terminal,
            };
        });
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: `${allTerminals.length} terminals in this window (${claudeTerminals.length} Claude)`,
            matchOnDescription: true,
        });
        if (selected) {
            selected.terminal.show();
        }
    }));
    // Show sessions across all projects
    context.subscriptions.push(vscode.commands.registerCommand('claude-tracker.showAllSessions', async () => {
        const sessions = await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Loading Claude sessions across all projects...',
            cancellable: false,
        }, () => parseAllClaudeSessions());
        if (sessions.length === 0) {
            vscode.window.showInformationMessage('No Claude sessions found');
            return;
        }
        // Group by project for better readability
        const items = sessions.map(s => ({
            label: (0, utils_1.truncate)(s.firstMessage, 60),
            description: `$(folder) ${path.basename(s.projectPath)}`,
            detail: `${s.gitBranch ? `$(git-branch) ${s.gitBranch} · ` : ''}${(0, utils_1.formatRelativeTime)(s.timestamp)}`,
            sessionId: s.id,
            projectPath: s.projectPath,
        }));
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: `${sessions.length} recent sessions across all projects`,
            matchOnDescription: true,
            matchOnDetail: true,
        });
        if (selected) {
            try {
                const terminal = (0, utils_1.createResumedTerminal)(selected.projectPath);
                (0, utils_1.sendSafeCommand)(terminal, 'claude --resume', selected.sessionId);
            }
            catch (err) {
                console.error('Failed to resume session:', err);
                vscode.window.showErrorMessage(`Failed to resume session: ${err}`);
            }
        }
    }));
    // Resume last session - supports multi-root workspaces
    context.subscriptions.push(vscode.commands.registerCommand('claude-tracker.resumeLast', async () => {
        // Find all workspaces with resumable sessions
        const resumableWorkspaces = (0, utils_1.getAllWorkspacePaths)()
            .filter(path => storage.getResumableForProject(path));
        let targetWorkspace;
        if (resumableWorkspaces.length === 0) {
            // No resumable sessions in any workspace, use first workspace
            targetWorkspace = (0, utils_1.getCurrentWorkspacePath)();
            if (!targetWorkspace) {
                vscode.window.showWarningMessage('No workspace folder open');
                return;
            }
        }
        else if (resumableWorkspaces.length === 1) {
            // Single resumable workspace - use it directly
            targetWorkspace = resumableWorkspaces[0];
        }
        else {
            // Multiple workspaces have resumable sessions - show picker
            const items = resumableWorkspaces.map(workspacePath => ({
                label: path.basename(workspacePath),
                description: workspacePath,
                workspacePath,
            }));
            const selected = await vscode.window.showQuickPick(items, {
                placeHolder: 'Select workspace to resume Claude session',
            });
            if (!selected)
                return;
            targetWorkspace = selected.workspacePath;
        }
        try {
            const terminal = (0, utils_1.createResumedTerminal)(targetWorkspace);
            (0, utils_1.sendSafeCommand)(terminal, 'claude --continue');
            // Only clear resumable status after successful terminal creation
            await storage.clearResumable(targetWorkspace);
        }
        catch (err) {
            console.error('Failed to resume Claude session:', err);
            vscode.window.showErrorMessage(`Failed to resume Claude session: ${err}`);
        }
    }));
    // Pick from recent sessions
    context.subscriptions.push(vscode.commands.registerCommand('claude-tracker.pickSession', async () => {
        const cwd = (0, utils_1.getCurrentWorkspacePath)();
        if (!cwd) {
            vscode.window.showWarningMessage('No workspace folder open');
            return;
        }
        // Show loading
        const sessions = await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Loading Claude sessions...',
            cancellable: false,
        }, () => parseClaudeSessions(cwd));
        if (sessions.length === 0) {
            vscode.window.showInformationMessage('No Claude sessions found for this workspace');
            return;
        }
        // Create quick pick items
        const items = sessions.map(s => ({
            label: (0, utils_1.truncate)(s.firstMessage, 60),
            description: s.gitBranch
                ? `$(git-branch) ${s.gitBranch}`
                : '$(circle-slash) No branch',
            detail: (0, utils_1.formatRelativeTime)(s.timestamp),
            sessionId: s.id,
        }));
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a session to resume',
            matchOnDescription: true,
            matchOnDetail: true,
        });
        if (selected) {
            try {
                const terminal = (0, utils_1.createResumedTerminal)(cwd);
                (0, utils_1.sendSafeCommand)(terminal, 'claude --resume', selected.sessionId);
            }
            catch (err) {
                console.error('Failed to resume session:', err);
                vscode.window.showErrorMessage(`Failed to resume session: ${err}`);
            }
        }
    }));
    // Show recent sessions - alias for pickSession
    // Note: Could be extended to show a read-only list view in future
    context.subscriptions.push(vscode.commands.registerCommand('claude-tracker.showSessions', () => {
        vscode.commands.executeCommand('claude-tracker.pickSession');
    }));
}
/**
 * Parse Claude session files for current workspace
 * Uses async file operations to avoid blocking the extension host
 */
async function parseClaudeSessions(workspacePath) {
    const claudeDir = path.join(os.homedir(), '.claude', 'projects');
    // Encode the workspace path the way Claude does
    // Claude replaces path separators with hyphens
    const encodedPath = (0, utils_1.encodeWorkspacePath)(workspacePath);
    const projectDir = path.join(claudeDir, encodedPath);
    // Check if directory exists (async)
    try {
        await fs.promises.access(projectDir);
    }
    catch {
        return [];
    }
    let files;
    try {
        // Read directory async
        const dirEntries = await fs.promises.readdir(projectDir);
        const jsonlFiles = dirEntries.filter(f => f.endsWith('.jsonl'));
        // Stat all files in parallel
        const fileStats = await Promise.all(jsonlFiles.map(async (f) => {
            const filePath = path.join(projectDir, f);
            try {
                const stat = await fs.promises.stat(filePath);
                return { name: f, path: filePath, stat };
            }
            catch {
                return null; // File may have been deleted
            }
        }));
        files = fileStats
            .filter((f) => f !== null && f.stat.size > 0)
            .sort((a, b) => b.stat.mtime.getTime() - a.stat.mtime.getTime())
            .slice(0, utils_1.MAX_RECENT_SESSIONS);
    }
    catch (err) {
        console.error('Failed to read sessions directory:', err);
        return [];
    }
    const sessions = [];
    for (const file of files) {
        try {
            const summary = await parseSessionFile(file.path);
            if (summary) {
                sessions.push(summary);
            }
        }
        catch (err) {
            // Skip corrupt files but log for debugging
            console.warn(`Failed to parse session file ${file.path}:`, err);
        }
    }
    return sessions;
}
/**
 * Parse a single session file to extract summary
 * Properly handles stream cleanup to prevent file handle leaks
 */
async function parseSessionFile(filePath) {
    return new Promise((resolve) => {
        const sessionId = path.basename(filePath, '.jsonl');
        let firstUserMessage = '';
        let timestamp = '';
        let gitBranch;
        // Store stream reference for proper cleanup
        const stream = fs.createReadStream(filePath);
        const rl = readline.createInterface({
            input: stream,
            crlfDelay: Infinity,
        });
        let lineCount = 0;
        const cleanup = () => {
            rl.close();
            stream.destroy(); // Explicitly destroy stream to prevent leaks
        };
        rl.on('line', (line) => {
            lineCount++;
            // Only parse first N lines to find metadata
            if (lineCount > utils_1.MAX_LINES_FOR_SUMMARY) {
                cleanup();
                return;
            }
            try {
                const data = JSON.parse(line);
                if (!timestamp && data.timestamp) {
                    timestamp = data.timestamp;
                }
                if (!gitBranch && data.gitBranch) {
                    gitBranch = data.gitBranch;
                }
                if (!firstUserMessage && data.type === 'user' && data.message?.content) {
                    // Extract just the actual user message, not system prompts
                    const content = data.message.content;
                    // Filter out memory agent observations
                    if (!content.includes('<observed_from_primary_session>') &&
                        !content.includes('MEMORY PROCESSING') &&
                        content.length < 500) { // Skip very long system messages
                        firstUserMessage = content;
                    }
                }
            }
            catch {
                // Skip malformed JSON lines
            }
        });
        rl.on('close', () => {
            stream.destroy(); // Ensure stream is destroyed
            if (timestamp && firstUserMessage) {
                resolve({
                    id: sessionId,
                    projectPath: filePath,
                    firstMessage: firstUserMessage,
                    timestamp,
                    gitBranch,
                });
            }
            else {
                resolve(null);
            }
        });
        rl.on('error', (err) => {
            console.warn(`Error reading session file ${filePath}:`, err);
            cleanup();
            resolve(null);
        });
        stream.on('error', (err) => {
            console.warn(`Stream error for ${filePath}:`, err);
            cleanup();
            resolve(null);
        });
    });
}
/**
 * Parse Claude sessions from ALL projects
 * Returns the most recent sessions across all project directories
 */
async function parseAllClaudeSessions() {
    const claudeDir = path.join(os.homedir(), '.claude', 'projects');
    // Check if projects directory exists
    try {
        await fs.promises.access(claudeDir);
    }
    catch {
        return [];
    }
    let projectDirs;
    try {
        const entries = await fs.promises.readdir(claudeDir, { withFileTypes: true });
        projectDirs = entries
            .filter(e => e.isDirectory())
            .map(e => path.join(claudeDir, e.name));
    }
    catch {
        return [];
    }
    // Collect all session files from all projects
    const allFiles = [];
    await Promise.all(projectDirs.map(async (projectDir) => {
        try {
            const dirEntries = await fs.promises.readdir(projectDir);
            const jsonlFiles = dirEntries.filter(f => f.endsWith('.jsonl'));
            await Promise.all(jsonlFiles.map(async (f) => {
                const filePath = path.join(projectDir, f);
                try {
                    const stat = await fs.promises.stat(filePath);
                    if (stat.size > 0) {
                        allFiles.push({ name: f, path: filePath, stat, projectDir });
                    }
                }
                catch {
                    // File may have been deleted
                }
            }));
        }
        catch {
            // Skip inaccessible project directories
        }
    }));
    // Sort by modification time and take most recent
    const sortedFiles = allFiles
        .sort((a, b) => b.stat.mtime.getTime() - a.stat.mtime.getTime())
        .slice(0, utils_1.MAX_RECENT_SESSIONS * 2); // Get more since we're across all projects
    const sessions = [];
    for (const file of sortedFiles) {
        try {
            const summary = await parseSessionFile(file.path);
            if (summary) {
                sessions.push({
                    ...summary,
                    projectPath: decodeProjectPath(file.projectDir),
                });
            }
        }
        catch (err) {
            console.warn(`Failed to parse session file ${file.path}:`, err);
        }
    }
    return sessions;
}
/**
 * Decode a project directory name back to the original path
 */
function decodeProjectPath(projectDir) {
    // Claude encodes paths by replacing separators with hyphens
    // e.g., "-Users-tomdimino-Desktop-Project" -> "/Users/tomdimino/Desktop/Project"
    const encoded = path.basename(projectDir);
    // Replace leading hyphen with / and all other hyphens with /
    return encoded.replace(/^-/, '/').replace(/-/g, '/');
}
//# sourceMappingURL=commands.js.map