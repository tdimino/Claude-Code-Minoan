# Supabase MCP Skill

A comprehensive Claude AI skill for working with Supabase through the Model Context Protocol (MCP). This skill enables AI-powered database operations, modern schema design, and production-ready database architectures.

## What's Included

### Core Skill File
- **SKILL.md** - Main skill file with comprehensive guidance on using Supabase MCP, including setup, common workflows, and best practices

### Reference Documentation (5 files)

1. **mcp-setup.md** (14.5 KB)
   - Complete MCP server setup guide
   - Remote (hosted) and local (self-hosted) configurations
   - Authentication methods (OAuth & PAT)
   - Security best practices and risk mitigation
   - Architecture and performance optimization
   - Troubleshooting guide

2. **database-patterns.md** (20.5 KB)
   - Modern database design patterns
   - Data Lakehouse, Microservices, Event Sourcing, CQRS
   - Inheritance patterns (Single Table, Class Table)
   - Polymorphic associations
   - Temporal data (SCD Type 2)
   - Multi-tenancy patterns (3 approaches)
   - Soft delete pattern
   - Decision matrix for pattern selection

3. **schema-design.md** (13.8 KB)
   - PostgreSQL/Supabase best practices
   - Column type recommendations
   - Constraint patterns (NOT NULL, UNIQUE, CHECK, FK)
   - Indexing strategies (B-tree, GIN, GiST)
   - Triggers and functions
   - Normalization (1NF, 2NF, 3NF)
   - Strategic denormalization
   - Migration best practices

4. **security.md** (17.0 KB)
   - Row Level Security (RLS) fundamentals
   - Common RLS patterns (user-owned, public read, org-based)
   - Role-Based Access Control (RBAC)
   - Multi-tenant isolation
   - Advanced patterns (time-based, ABAC, hierarchical)
   - Security functions (auth.uid(), auth.email())
   - Data encryption (column-level, password hashing)
   - Audit logging implementation
   - Security vulnerability mitigation

5. **tools-reference.md** (14.6 KB)
   - Complete MCP tools documentation
   - SQL operations (execute_sql, list_tables, describe_table)
   - Migration tools (list, generate, apply, rollback)
   - Project management (list, create, pause, restore)
   - Branching tools (create, list, merge)
   - Log tools (list, search)
   - Type generation (TypeScript)
   - Natural language query examples
   - Best practices and tool combinations

## Total Content

- **6 comprehensive markdown files**
- **92 KB of expert knowledge**
- **Covers**: Setup, Patterns, Schema Design, Security, and Tools
- **Production-ready**: Battle-tested patterns and best practices

## Installation

### Option 1: Upload to Claude.ai

1. Go to https://claude.ai/skills
2. Click "Upload Skill"
3. Select the packaged `.zip` file
4. Skill is ready to use!

### Option 2: Use with Claude Code CLI

1. Place this directory in your Claude Code skills folder
2. Claude Code will automatically detect it

## Usage Examples

Once installed, you can ask Claude:

**Setup:**
- "How do I configure Supabase MCP for Cursor?"
- "Walk me through setting up local MCP server"

**Schema Design:**
- "Design a multi-tenant SaaS database schema"
- "What's the best way to model hierarchical data?"
- "Should I use UUID or serial for primary keys?"

**Security:**
- "Implement RLS for organization-based access"
- "Show me how to audit all changes to sensitive tables"
- "Create a role-based permission system"

**Database Patterns:**
- "When should I use Event Sourcing vs CQRS?"
- "How do I implement soft deletes?"
- "Design a temporal data model for price history"

**MCP Tools:**
- "Show me all users who signed up last week"
- "Generate a migration to add an email_verified column"
- "Create a development branch for testing schema changes"

## Skill Features

### Progressive Disclosure
The skill uses a three-level loading system:
1. **Metadata** (always loaded) - ~100 tokens
2. **Instructions** (when triggered) - ~5k tokens
3. **References** (as needed) - Loaded on demand

### Comprehensive Coverage
- ✅ MCP server configuration (remote & local)
- ✅ 10+ database design patterns
- ✅ PostgreSQL schema best practices
- ✅ Production-grade security (RLS, encryption, auditing)
- ✅ 20+ MCP tools documented
- ✅ Natural language query examples
- ✅ Migration workflows
- ✅ Performance optimization

### Best Practices Built-In
- Security-first approach
- Future-proof architecture principles
- Industry-standard patterns
- Real-world examples
- Error handling and troubleshooting

## When to Use This Skill

Use this skill when:
- Setting up Supabase MCP servers
- Designing database schemas
- Implementing Row Level Security
- Managing database migrations
- Building modular, scalable architectures
- Querying databases with natural language
- Optimizing database performance
- Implementing multi-tenancy

## Architecture

Based on research from:
- Official Supabase MCP documentation
- Modern data architecture principles
- PostgreSQL best practices
- Battle-tested design patterns
- Security industry standards

## Version History

- **v1.0** (2025-10-23) - Initial release
  - Comprehensive MCP setup guide
  - 10+ database design patterns
  - Complete schema design reference
  - Production-grade security patterns
  - Full MCP tools documentation
  - 92 KB of expert knowledge

## Created With

- **Research Sources**: Supabase MCP docs, Exa AI research, database architecture guides
- **Framework**: Claude Code Skill Builder
- **Tools**: Exa MCP for research, Skill_Seekers patterns for structure
- **Quality**: Production-ready, comprehensive, well-documented

## File Structure

```
supabase-skill/
├── SKILL.md                          # Main skill file
├── README.md                         # This file
├── references/
│   ├── mcp-setup.md                 # MCP configuration
│   ├── database-patterns.md         # Design patterns
│   ├── schema-design.md             # Schema best practices
│   ├── security.md                  # RLS and security
│   └── tools-reference.md           # MCP tools docs
├── scripts/                          # (empty - for user scripts)
└── assets/                           # (empty - for user assets)
```

## Support

For issues or questions:
- Review the comprehensive reference documentation
- Check troubleshooting sections in each reference
- Consult official Supabase documentation: https://supabase.com/docs
- Join Supabase Discord community: https://discord.supabase.com

## License

This skill is provided as-is for use with Claude AI. The knowledge contained is based on publicly available documentation and best practices.

---

**Ready to use!** This skill provides comprehensive guidance for Supabase development with MCP integration.
