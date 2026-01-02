# Row Level Security (RLS) - Official Supabase Documentation

**Source**: Supabase Official Docs + Exa Code Context

## Overview

Row Level Security (RLS) is PostgreSQL's built-in authorization system that provides granular, row-level access control. In Supabase, RLS is the primary mechanism for securing data access from client applications.

## Core Concepts

### What is RLS?

RLS allows you to define policies that determine which rows in a table users can:
- **SELECT** (read)
- **INSERT** (create)
- **UPDATE** (modify)
- **DELETE** (remove)

Think of RLS policies as automatically adding `WHERE` clauses to every query based on the current user's context.

### Why RLS in Supabase?

- **Defense in Depth**: Protects data even if accessed through third-party tools
- **Client-Side Security**: Enables safe direct browser-to-database access
- **Integration with Auth**: Works seamlessly with Supabase Auth (`auth.uid()`)
- **Flexible Rules**: Supports complex business logic in SQL
- **Performance**: Evaluated at the database level (faster than application-layer checks)

##

 Enabling RLS

### Basic Enablement

```sql
-- Enable RLS on a table
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;
```

### Critical Rule

**ALWAYS enable RLS on tables in exposed schemas** (especially `public` schema).

- Tables created in Dashboard Table Editor → RLS enabled by default
- Tables created via SQL Editor → **You must enable RLS manually**

### Behavior When RLS is Enabled

Once RLS is enabled without policies:
- **No data is accessible** via the API using the `anon` key
- You must create at least one policy to allow access
- This "deny by default" behavior prevents accidental data exposure

## Creating Policies

### Basic Policy Structure

```sql
CREATE POLICY "policy_name"
ON table_name
FOR operation  -- SELECT, INSERT, UPDATE, DELETE, or ALL
TO role       -- authenticated, anon, service_role, or specific role
USING (condition)      -- Read check (who can see this row?)
WITH CHECK (condition) -- Write check (can this row be created/updated?)
```

### Common Policy Patterns

#### 1. User-Owned Data (Most Common)

```sql
-- Allow users to read their own data
CREATE POLICY "Users can view own data"
ON profiles
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- Allow users to insert their own data
CREATE POLICY "Users can insert own data"
ON profiles
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Allow users to update their own data
CREATE POLICY "Users can update own data"
ON profiles
FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Allow users to delete their own data
CREATE POLICY "Users can delete own data"
ON profiles
FOR DELETE
TO authenticated
USING (auth.uid() = user_id);
```

#### 2. Public Read, Authenticated Write

```sql
-- Anyone can read
CREATE POLICY "Public profiles are viewable by everyone"
ON profiles
FOR SELECT
USING (true);

-- Only authenticated users can insert
CREATE POLICY "Authenticated users can create profiles"
ON profiles
FOR INSERT
TO authenticated
WITH CHECK (true);
```

#### 3. Role-Based Access (RBAC)

```sql
-- Use security definer function for role checks
CREATE FUNCTION private.get_user_role(user_id uuid, org_id bigint)
RETURNS text
LANGUAGE sql
SECURITY DEFINER
SET search_path = ''
AS $$
  SELECT role FROM org_members
  WHERE user_id = $1 AND org_id = $2;
$$;

-- Policy using role check
CREATE POLICY "Admins and owners can manage posts"
ON posts
FOR ALL
USING (
  private.get_user_role(auth.uid(), org_id) IN ('owner', 'admin')
);
```

#### 4. Multi-Tenant with Organization Membership

```sql
-- Users can only see data from their organizations
CREATE POLICY "Users can view own organization data"
ON documents
FOR SELECT
TO authenticated
USING (
  org_id IN (
    SELECT organization_id
    FROM org_members
    WHERE user_id = auth.uid()
  )
);
```

#### 5. Complex Business Logic

```sql
-- Posts visible based on status and premium access
CREATE POLICY "Complex post visibility"
ON posts
FOR SELECT
USING (
  -- Published non-premium posts visible to all
  (status = 'published' AND NOT is_premium)
  OR
  -- Premium posts visible to org members only
  (status = 'published' AND is_premium AND
   EXISTS (
     SELECT 1 FROM org_members
     WHERE org_id = posts.org_id
     AND user_id = auth.uid()
   ))
  OR
  -- All posts visible to editors and above
  private.get_user_role(auth.uid(), org_id) IN ('owner', 'admin', 'editor')
);
```

## Policy Types

### PERMISSIVE vs RESTRICTIVE

```sql
-- PERMISSIVE (default): Policies are OR'd together
CREATE POLICY "policy1" ON table
AS PERMISSIVE
FOR SELECT
USING (condition1);  -- Access granted if ANY permissive policy passes

-- RESTRICTIVE: Policies are AND'd together
CREATE POLICY "policy2" ON table
AS RESTRICTIVE
FOR SELECT
USING (condition2);  -- Access denied if ANY restrictive policy fails
```

**Use Case for RESTRICTIVE**: Enforce mandatory checks that must always pass (e.g., MFA requirement)

```sql
-- Require MFA for sensitive data
CREATE POLICY "Require MFA for private posts"
ON private_posts
AS RESTRICTIVE
FOR SELECT
TO authenticated
USING ((auth.jwt()->>'aal') = 'aal2');  -- Must have MFA
```

## Important Patterns & Gotchas

### 1. `auth.uid()` Returns `null` When Unauthenticated

```sql
-- ❌ BAD: Silent failure for unauthenticated users
USING (auth.uid() = user_id)

-- ✅ GOOD: Explicit authentication check
USING (auth.uid() IS NOT NULL AND auth.uid() = user_id)
```

### 2. Security Definer Functions Prevent RLS Recursion

```sql
-- ✅ Use SECURITY DEFINER to bypass RLS in helper functions
CREATE FUNCTION private.check_permission(org_id bigint)
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER  -- Runs with definer's permissions
SET search_path = ''  -- Security: prevent search_path attacks
AS $$
  SELECT EXISTS (
    SELECT 1 FROM org_members
    WHERE org_id = $1 AND user_id = auth.uid()
  );
$$;
```

### 3. Use `TO` Clause to Specify Roles

```sql
-- ✅ ALWAYS specify role explicitly
CREATE POLICY "name" ON table
FOR SELECT
TO authenticated  -- Explicit role
USING (condition);

-- ❌ AVOID: Implicit role (harder to reason about)
CREATE POLICY "name" ON table
FOR SELECT
USING (condition);
```

### 4. Separate Policies for Different Operations

```sql
-- ✅ GOOD: Separate policies for clarity
CREATE POLICY "SELECT" ON table FOR SELECT USING (...);
CREATE POLICY "INSERT" ON table FOR INSERT WITH CHECK (...);
CREATE POLICY "UPDATE" ON table FOR UPDATE USING (...) WITH CHECK (...);
CREATE POLICY "DELETE" ON table FOR DELETE USING (...);

-- ❌ AVOID: Single FOR ALL policy (harder to debug)
CREATE POLICY "all" ON table FOR ALL USING (...);
```

## Roles in Supabase

Supabase automatically maps requests to PostgreSQL roles:

| Request Type | Role | Use Case |
|-------------|------|----------|
| Unauthenticated | `anon` | Public API requests without auth token |
| Authenticated user | `authenticated` | Logged-in users via Supabase Auth |
| Service role key | `service_role` | Backend services, admin operations |

### Checking Current Role

```sql
-- In a policy, check the role
CREATE POLICY "Service role bypass"
ON table
FOR ALL
USING (
  current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
);
```

## Advanced Patterns

### 1. Time-Based Access

```sql
-- Only show active subscriptions
CREATE POLICY "Active subscriptions only"
ON subscriptions
FOR SELECT
USING (
  status = 'active'
  AND expires_at > now()
  AND user_id = auth.uid()
);
```

### 2. Conditional Insert Based on Limits

```sql
-- Check organization post limits before allowing insert
CREATE POLICY "Respect post limits"
ON posts
FOR INSERT
WITH CHECK (
  (SELECT plan_type FROM organizations WHERE id = org_id) != 'free'
  OR
  (SELECT count(*) FROM posts WHERE org_id = posts.org_id) <
  (SELECT max_posts FROM organizations WHERE id = posts.org_id)
);
```

### 3. Realtime Authorization

```sql
-- Control access to Realtime messages
CREATE POLICY "Users can listen to their room"
ON realtime.messages
FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM rooms_users
    WHERE user_id = auth.uid()
    AND room_topic = realtime.topic()
  )
);
```

## Testing RLS Policies

### Test as Different Users

```sql
-- Set JWT claims to test as specific user
SELECT set_config(
  'request.jwt.claims',
  '{"sub":"user-uuid-here","role":"authenticated"}',
  TRUE
);

-- Run your query
SELECT * FROM your_table;

-- Reset
SELECT set_config('request.jwt.claims', '', TRUE);
```

### Test with Different Roles

```sql
-- Test as anon
SET ROLE anon;
SELECT * FROM your_table;

-- Test as authenticated
SET ROLE authenticated;
SELECT * FROM your_table;

-- Reset
RESET ROLE;
```

## Performance Considerations

### 1. Index Columns Used in Policies

```sql
-- If policy uses user_id
CREATE INDEX idx_table_user_id ON table(user_id);

-- If policy uses org_id
CREATE INDEX idx_table_org_id ON table(org_id);
```

### 2. Avoid Complex Subqueries

```sql
-- ❌ SLOW: Subquery executed for every row
USING (
  org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid())
)

-- ✅ FASTER: Use security definer function (evaluated once)
USING (private.is_org_member(auth.uid(), org_id))
```

### 3. Monitor Slow Queries

```sql
-- Log slow RLS queries
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Query slow statements
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query LIKE '%your_table%'
ORDER BY mean_exec_time DESC;
```

## Common Mistakes to Avoid

1. **❌ Forgetting to enable RLS** on new tables
2. **❌ Not specifying `TO` role** in policies
3. **❌ Using `FOR ALL`** instead of separate policies
4. **❌ Not testing with actual user contexts**
5. **❌ Not indexing columns** used in policy conditions
6. **❌ Using application-level security only** without RLS
7. **❌ Not using `SECURITY DEFINER`** for helper functions
8. **❌ Ignoring `auth.uid() = null`** for unauthenticated users

## Resources

- **Official Docs**: https://supabase.com/docs/guides/database/postgres/row-level-security
- **PostgreSQL RLS**: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- **Testing Guide**: https://supabase.com/docs/guides/local-development/testing/pgtap-extended
