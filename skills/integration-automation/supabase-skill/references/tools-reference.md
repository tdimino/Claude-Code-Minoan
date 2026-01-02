# Supabase MCP Tools Reference

## Overview

The Supabase MCP server provides 20+ tools for interacting with your Supabase projects through natural language. This reference documents all available tools, their parameters, and usage examples.

## Tool Categories

1. **SQL Operations** - Direct database queries and schema introspection
2. **Migrations** - Schema changes and version management
3. **Project Management** - Project configuration and operations
4. **Authentication** - User management (future)
5. **Storage** - File operations (future)
6. **Logs** - Debugging and monitoring
7. **Branching** - Development environments (experimental)

## SQL Operations

### execute_sql

Execute arbitrary SQL queries on your database.

**Parameters:**
- `query` (string, required) - SQL query to execute
- `project_ref` (string, optional) - Target project reference

**Example:**
```
Ask Claude: "Show me all users who signed up in the last 7 days"

Generated query:
select * from auth.users
where created_at > now() - interval '7 days'
order by created_at desc;
```

**Use Cases:**
- Data exploration and analysis
- Complex queries with joins
- Aggregations and reports
- Administrative operations

**Security:**
- Respects RLS policies (with anon key)
- Bypasses RLS (with service role key)
- Always requires manual approval in clients

### list_tables

List all tables in the database with metadata.

**Parameters:**
- `schema` (string, optional, default: 'public') - Database schema to list
- `project_ref` (string, optional) - Target project

**Example:**
```
Ask Claude: "What tables exist in my database?"

Response:
- users (auth schema)
- profiles (public schema)
- posts (public schema)
- comments (public schema)
```

**Returns:**
- Table names
- Schema location
- Row counts (approximate)
- Size on disk

### describe_table

Get detailed information about a specific table.

**Parameters:**
- `table_name` (string, required) - Name of the table
- `schema` (string, optional, default: 'public') - Schema name
- `project_ref` (string, optional) - Target project

**Example:**
```
Ask Claude: "Describe the posts table structure"

Response:
Table: public.posts
Columns:
  - id: uuid (primary key)
  - title: text (not null)
  - content: text
  - author_id: uuid (foreign key -> auth.users)
  - created_at: timestamptz (default: now())

Indexes:
  - posts_pkey (PRIMARY KEY on id)
  - idx_posts_author (BTREE on author_id)

Foreign Keys:
  - posts_author_id_fkey -> auth.users(id)
```

**Returns:**
- Column definitions (name, type, nullable, default)
- Indexes and their types
- Foreign key relationships
- Check constraints
- RLS policies (if enabled)

### list_functions

List all database functions and stored procedures.

**Parameters:**
- `schema` (string, optional, default: 'public')
- `project_ref` (string, optional)

**Example:**
```
Ask Claude: "What custom functions are defined?"

Response:
- set_updated_at() - trigger function for timestamps
- is_admin() - check if user has admin role
- get_user_posts(user_id uuid) - fetch posts for user
```

### describe_function

Get details about a specific function.

**Parameters:**
- `function_name` (string, required)
- `schema` (string, optional, default: 'public')
- `project_ref` (string, optional)

**Example:**
```
Ask Claude: "Show me the is_admin function definition"

Response:
Function: public.is_admin()
Returns: boolean
Language: plpgsql
Security: DEFINER

Definition:
begin
  return exists (
    select 1 from public.user_roles
    where user_id = auth.uid()
    and role = 'admin'
  );
end;
```

## Migration Tools

### list_migrations

List all database migrations and their status.

**Parameters:**
- `project_ref` (string, optional)

**Example:**
```
Ask Claude: "Show me all database migrations"

Response:
✅ 20231015_create_users_table.sql (applied)
✅ 20231016_add_posts_table.sql (applied)
✅ 20231017_add_rls_policies.sql (applied)
❌ 20231018_add_comments_table.sql (pending)
```

**Returns:**
- Migration filename
- Applied timestamp
- Status (applied/pending)
- Checksum for integrity

### generate_migration

Generate a new migration based on natural language description.

**Parameters:**
- `description` (string, required) - What the migration should do
- `project_ref` (string, optional)

**Example:**
```
Ask Claude: "Generate a migration to add a 'status' column to posts table"

Generated migration (20250123_add_status_to_posts.sql):
-- Add status column
alter table public.posts
add column status text
check (status in ('draft', 'published', 'archived'))
default 'draft';

-- Create index
create index idx_posts_status
on public.posts(status);

-- Backfill existing rows
update public.posts
set status = 'published'
where status is null;

-- Make not null after backfill
alter table public.posts
alter column status set not null;
```

**Use Cases:**
- Add/remove columns
- Create/drop tables
- Add indexes
- Modify constraints
- Create RLS policies

### apply_migration

Apply a pending migration to the database.

**Parameters:**
- `migration_name` (string, required)
- `project_ref` (string, optional)
- `dry_run` (boolean, optional, default: false)

**Example:**
```
Ask Claude: "Apply the add_status_to_posts migration"

Response:
Running migration: 20250123_add_status_to_posts.sql
✅ alter table public.posts add column status...
✅ create index idx_posts_status...
✅ update public.posts set status...
✅ alter table public.posts alter column status...

Migration applied successfully in 1.2 seconds
```

**Safety Features:**
- Dry run mode to preview changes
- Automatic rollback on error
- Backup before applying (if configured)

### rollback_migration

Rollback the last applied migration.

**Parameters:**
- `steps` (integer, optional, default: 1) - Number of migrations to rollback
- `project_ref` (string, optional)

**Example:**
```
Ask Claude: "Rollback the last migration"

Response:
Rolling back: 20250123_add_status_to_posts.sql
✅ alter table public.posts drop column status...
✅ drop index idx_posts_status...

Migration rolled back successfully
```

## Project Management

### list_projects

List all Supabase projects in your organization.

**Parameters:** None

**Example:**
```
Ask Claude: "List my Supabase projects"

Response:
- production-app (abcdefgh) - Active
- staging-app (ijklmnop) - Active
- dev-app (qrstuvwx) - Paused
```

**Returns:**
- Project name
- Project reference ID
- Region
- Status (active/paused)
- Database version

### get_project_config

Get configuration details for a project.

**Parameters:**
- `project_ref` (string, required)

**Example:**
```
Ask Claude: "Show me the config for my production project"

Response:
Project: production-app (abcdefgh)

Database:
  - Version: PostgreSQL 15.1
  - Size: 2.4 GB
  - Connection string: postgres://...

API:
  - URL: https://abcdefgh.supabase.co
  - Anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  - Service role key: [REDACTED]

Storage:
  - Used: 543 MB
  - Limit: 1 GB

Auth:
  - Providers: Email, Google, GitHub
  - Users: 1,247
```

### create_project

Create a new Supabase project.

**Parameters:**
- `name` (string, required)
- `organization_id` (string, required)
- `region` (string, optional, default: 'us-east-1')
- `db_password` (string, required)

**Example:**
```
Ask Claude: "Create a new project called 'test-app' in us-west-1"

Response:
Creating project...
✅ Project created: test-app (yzabcdef)
✅ Database initialized
✅ APIs generated

Project URL: https://yzabcdef.supabase.co
Anon key: eyJhbGciOiJIUzI1...
Service role key: [Check dashboard]

Ready to use in ~2 minutes
```

### pause_project

Pause a project to save costs.

**Parameters:**
- `project_ref` (string, required)

**Example:**
```
Ask Claude: "Pause the dev-app project"

Response:
Pausing project: dev-app (qrstuvwx)
✅ Connections closed
✅ Database paused
✅ APIs disabled

Project paused. Resume anytime with no data loss.
```

### restore_project

Resume a paused project.

**Parameters:**
- `project_ref` (string, required)

**Example:**
```
Ask Claude: "Resume the dev-app project"

Response:
Restoring project: dev-app (qrstuvwx)
✅ Database started
✅ APIs enabled
✅ Connections available

Project restored and ready (startup time: 45s)
```

## Branching Tools (Experimental)

### create_branch

Create a development branch from production.

**Parameters:**
- `branch_name` (string, required)
- `from_project_ref` (string, required)

**Example:**
```
Ask Claude: "Create a dev branch from production"

Response:
Creating branch: dev
✅ Database snapshot created
✅ Branch database started
✅ Schema copied
✅ Data seeded (optional)

Branch URL: https://dev-abcdefgh.supabase.co
Branch ref: dev-abcdefgh

Test changes safely in isolation!
```

**Use Cases:**
- Test migrations before production
- Experiment with schema changes
- Preview feature branches
- Isolated development environments

### list_branches

List all branches for a project.

**Parameters:**
- `project_ref` (string, required)

**Example:**
```
Ask Claude: "List all branches for production"

Response:
Branches for production-app:
- main (production) - abcdefgh
- feature-auth - feat-auth-1234
- bugfix-posts - bugfix-5678
```

### merge_branch

Merge a branch back to production (via migration).

**Parameters:**
- `branch_ref` (string, required)
- `target_ref` (string, required)

**Example:**
```
Ask Claude: "Merge feature-auth branch to main"

Response:
Generating migration from branch changes...
✅ Schema diff calculated
✅ Migration created: 20250123_merge_feature_auth.sql

Apply migration to complete merge? (y/n)
```

## Log Tools

### list_logs

Fetch recent logs from your project.

**Parameters:**
- `project_ref` (string, required)
- `level` (string, optional) - Filter by level (error/warning/info)
- `limit` (integer, optional, default: 100)
- `source` (string, optional) - Filter by source (postgres/api/auth/realtime)

**Example:**
```
Ask Claude: "Show me recent errors from the API"

Response:
[2025-10-23 10:42:15] ERROR (api) - RLS policy violation
  Query: SELECT * FROM posts WHERE id = '...'
  User: user-123
  Details: No policy allows SELECT for user

[2025-10-23 10:38:22] ERROR (postgres) - Duplicate key violation
  Table: users
  Constraint: users_email_key
  Value: 'test@example.com'

[2025-10-23 10:35:01] ERROR (auth) - Invalid JWT token
  Reason: Token expired
  IP: 192.168.1.1
```

### search_logs

Search logs with text query.

**Parameters:**
- `project_ref` (string, required)
- `query` (string, required)
- `from_time` (timestamp, optional)
- `to_time` (timestamp, optional)

**Example:**
```
Ask Claude: "Search logs for 'timeout' errors in the last hour"

Response:
Found 3 matches:

[2025-10-23 10:55:12] ERROR - Query timeout
  Query: SELECT * FROM posts JOIN...
  Duration: 30.1s (exceeded limit)

[2025-10-23 10:48:33] WARN - Connection timeout
  Details: Client connection idle for 5 minutes

[2025-10-23 10:42:09] ERROR - Lock timeout
  Table: posts
  Wait time: 15s
```

## Type Generation

### generate_types

Generate TypeScript types from your database schema.

**Parameters:**
- `project_ref` (string, required)
- `schema` (string, optional, default: 'public')
- `output_format` (string, optional) - 'typescript' or 'json-schema'

**Example:**
```
Ask Claude: "Generate TypeScript types for my database"

Generated (types/supabase.ts):
export interface Database {
  public: {
    Tables: {
      posts: {
        Row: {
          id: string
          title: string
          content: string | null
          author_id: string
          created_at: string
        }
        Insert: {
          id?: string
          title: string
          content?: string | null
          author_id: string
          created_at?: string
        }
        Update: {
          id?: string
          title?: string
          content?: string | null
          author_id?: string
          created_at?: string
        }
      }
      // ... more tables
    }
  }
}
```

## Best Practices

### Natural Language Queries

**Good Examples:**
- ✅ "Show me all users who haven't logged in for 30 days"
- ✅ "Create a migration to add an email_verified column"
- ✅ "What's the schema of the posts table?"
- ✅ "Generate a report of post counts by author"

**Avoid:**
- ❌ "Do SQL" (too vague)
- ❌ "Fix the database" (unclear intent)
- ❌ "Make it faster" (needs context)

### Safety Guidelines

1. **Always review generated SQL** - Don't blindly execute
2. **Test on branches first** - Use branching for risky changes
3. **Use dry run mode** - Preview migration effects
4. **Enable manual approval** - Keep client tool confirmation enabled
5. **Monitor logs** - Check for unexpected behavior

### Performance Tips

1. **Be specific** - "users where status='active'" not "users"
2. **Use limits** - Add LIMIT to exploratory queries
3. **Index awareness** - Ask about indexes if queries are slow
4. **Batch operations** - Group related changes together

## Tool Combinations

### Schema Design Workflow

```
1. "Describe the current users table"
2. "Generate a migration to add a role column with enum values"
3. "Show me the migration file"
4. "Apply the migration in dry run mode first"
5. "Apply the migration for real"
6. "Generate updated TypeScript types"
```

### Debugging Workflow

```
1. "Show me recent errors from the API logs"
2. "Describe the posts table to check RLS policies"
3. "Execute this query to test: SELECT * FROM posts WHERE id='...'"
4. "Check if there are missing indexes on the posts table"
```

### Migration Workflow

```
1. "Create a branch called 'add-comments-feature'"
2. "Generate a migration for a comments table with foreign key to posts"
3. "Apply migration to the branch"
4. "Test the schema with: SELECT * FROM comments LIMIT 5"
5. "Merge branch to production"
```

## Error Handling

Common errors and solutions:

**"RLS policy violation"**
- Review policies on the table
- Check if user has proper permissions
- Verify auth.uid() is set correctly

**"Permission denied for table"**
- Service role key may be required
- Check database user permissions
- Verify MCP configuration

**"Relation does not exist"**
- Table name may be incorrect
- Schema not specified (default: public)
- Migration not applied yet

**"Query timeout"**
- Add LIMIT to reduce result set
- Check for missing indexes
- Optimize query with EXPLAIN ANALYZE

## Next Steps

- Practice with **mcp-setup.md** for installation
- Design schemas using **schema-design.md** patterns
- Implement security with **security.md** guidelines
- Study **database-patterns.md** for advanced architectures
