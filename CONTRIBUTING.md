# Contributing to Aldea Claude Code Configuration

Thank you for contributing to the Aldea team's Claude Code setup! This guide will help you add new skills, slash commands, and MCP servers.

## 📋 Table of Contents

- [Contributing Skills](#contributing-skills)
- [Contributing Slash Commands](#contributing-slash-commands)
- [Contributing MCP Servers](#contributing-mcp-servers)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)

## 🎯 Contributing Skills

### Skill Structure

A skill must follow this directory structure:

```
skills/
└── your-skill-name/
    ├── skill.md          # Required: Main skill definition
    ├── README.md         # Optional: Documentation
    └── examples/         # Optional: Example usage
        └── example.md
```

### Creating a New Skill

1. **Use the skill template**:

```bash
mkdir -p skills/your-skill-name
cp skills/.template/skill.md skills/your-skill-name/skill.md
```

2. **Edit `skill.md`** with this structure:

```markdown
---
description: Brief one-line description of what the skill does
---

# Skill Name

Detailed description of the skill's purpose and when to use it.

## Usage

Explain how and when this skill should be invoked.

## Examples

Provide concrete examples of the skill in action.

## Configuration

If the skill requires any configuration, document it here.

## Dependencies

List any MCP servers, tools, or other skills this depends on.
```

3. **Test the skill**:

```bash
# Copy to your local skills directory
cp -r skills/your-skill-name ~/.claude/skills/

# Test in Claude Code
# The skill should appear automatically and can be invoked
```

4. **Create documentation**:

```bash
# Add README.md with detailed usage instructions
cat > skills/your-skill-name/README.md << EOF
# Your Skill Name

## Purpose
What problem does this skill solve?

## When to Use
Describe scenarios where this skill is most useful.

## Usage Examples
[Provide 2-3 concrete examples]

## Troubleshooting
Common issues and solutions.
EOF
```

5. **Submit PR** (see Pull Request Process below)

### Skill Best Practices

✅ **Do**:
- Keep skills focused on a single purpose
- Provide clear, concise documentation
- Include usage examples
- Test thoroughly across different projects
- Document any dependencies
- Use descriptive names (kebab-case)

❌ **Don't**:
- Create overly broad skills
- Include API keys or secrets
- Duplicate existing skill functionality
- Skip documentation

## ⚡ Contributing Slash Commands

### Command Structure

Slash commands are Markdown files in the `commands/` directory:

```
commands/
└── command-name.md
```

### Creating a New Command

1. **Create the command file**:

```bash
cat > commands/your-command.md << 'EOF'
---
description: Brief description of what this command does
argument-hint: [required-arg] [optional-arg]
allowed-tools: Read, Write, Edit, Bash
model: claude-sonnet-4
---

Your detailed prompt template here.

Use $1, $2, etc. for arguments if using argument-hint.

## Example
If user runs: /your-command myfile.ts
Then $1 = myfile.ts
EOF
```

2. **Test the command**:

```bash
# Copy to your local commands
cp commands/your-command.md ~/.claude/commands/

# Test in Claude Code
/your-command
```

3. **Document in README**:

Add your command to the "Popular Slash Commands" section in README.md.

### Command Best Practices

✅ **Do**:
- Use frontmatter for metadata
- Keep commands single-purpose
- Provide argument hints if applicable
- Use clear, descriptive names
- Include examples in comments

❌ **Don't**:
- Create overly complex commands
- Duplicate existing commands
- Use unclear abbreviations
- Skip the description field

### Command Naming Conventions

- Use kebab-case: `my-command.md`
- Be descriptive: `security-scan.md` not `scan.md`
- Avoid abbreviations unless common: `refactor.md` not `rfctr.md`

## 🔧 Contributing MCP Servers

### Adding a New MCP Server

1. **Test the server locally**:

```bash
# Add server to your local config first
claude mcp add server-name -c command -a "args" -s user

# Verify it works
claude mcp list
claude mcp get server-name
```

2. **Document in .mcp.json**:

```json
{
  "mcpServers": {
    "your-server-name": {
      "description": "Clear description of what this server provides",
      "type": "stdio" or "http",
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": {
        "API_KEY": "PLACEHOLDER_FOR_ACTUAL_KEY"
      },
      "setup": {
        "instructions": [
          "Step 1: Install dependencies",
          "Step 2: Get API key from...",
          "Step 3: Replace PLACEHOLDER_FOR_ACTUAL_KEY"
        ]
      }
    }
  }
}
```

3. **Update README.md**:

Add the server to the "Available MCP Servers" section with:
- Server name
- Brief description
- Category (AI & Search, Development Tools, etc.)

### MCP Server Best Practices

✅ **Do**:
- Test thoroughly before adding
- Document all environment variables
- Use placeholders for API keys
- Include troubleshooting steps
- Specify recommended scope (user/project/local)
- Document system dependencies

❌ **Don't**:
- Commit actual API keys
- Add untested servers
- Skip setup instructions
- Assume dependencies are installed

### Security Requirements

⚠️ **Critical**: Never commit actual API keys or secrets

Use placeholders:
- `YOUR_API_KEY_HERE`
- `REPLACE_WITH_YOUR_TOKEN`
- `YOUR_PROJECT_ID_HERE`

## 🔄 Pull Request Process

### Before Submitting

- [ ] Test your contribution locally
- [ ] Update README.md if applicable
- [ ] Update CONTRIBUTING.md if adding new patterns
- [ ] Ensure no API keys or secrets are included
- [ ] Run spell check on documentation
- [ ] Verify all links work

### PR Template

```markdown
## Description
Brief description of what this PR adds/changes.

## Type of Change
- [ ] New skill
- [ ] New slash command
- [ ] New MCP server
- [ ] Documentation update
- [ ] Bug fix

## Checklist
- [ ] Tested locally
- [ ] Documentation updated
- [ ] No secrets committed
- [ ] Examples provided (if applicable)

## Usage Example
Show how to use the new feature:
```

### PR Title Format

- **Skills**: `feat(skills): add [skill-name]`
- **Commands**: `feat(commands): add /command-name`
- **MCP**: `feat(mcp): add [server-name] integration`
- **Docs**: `docs: update [section] documentation`
- **Fix**: `fix: resolve [issue description]`

## 👀 Code Review Guidelines

### What Reviewers Look For

1. **Functionality**
   - Does it work as described?
   - Are there edge cases?

2. **Documentation**
   - Is the purpose clear?
   - Are examples provided?
   - Are setup instructions complete?

3. **Security**
   - No API keys committed?
   - No sensitive data exposed?

4. **Quality**
   - Follows naming conventions?
   - Fits the existing structure?
   - Well-tested?

### Review Process

1. Reviewer tests the contribution locally
2. Checks documentation completeness
3. Verifies no secrets are committed
4. Approves or requests changes
5. Maintainer merges approved PRs

## 🏷️ Versioning

We use semantic versioning for this repository:

- **Major** (1.0.0): Breaking changes to structure
- **Minor** (0.1.0): New skills, commands, or servers
- **Patch** (0.0.1): Bug fixes, documentation updates

## 📝 Commit Message Format

Use conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types**:
- `feat`: New feature (skill, command, server)
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(skills): add open-souls-paradigm skill
fix(mcp): correct perplexity server configuration
docs: update README with new MCP server setup
```

## 🆘 Getting Help

- Review existing skills/commands for examples
- Check [Claude Code docs](https://docs.claude.com/en/docs/claude-code)
- Ask in team chat
- Create an issue for discussion

## 📄 License

All contributions are internal to Aldea and follow company guidelines.

---

Thank you for contributing! 🎉
