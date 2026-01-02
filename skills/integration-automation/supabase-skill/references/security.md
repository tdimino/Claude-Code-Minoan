# Supabase Security & Row Level Security (RLS) Guide

## Core Security Principles

1. **Never trust the client** - All security must be enforced at database level
2. **RLS is mandatory** - Enable RLS on all public tables
3. **Principle of least privilege** - Grant minimum required permissions
4. **Defense in depth** - Multiple security layers
5. **Audit everything** - Log all sensitive operations

## Row Level Security (RLS) Fundamentals

### Enabling RLS

```sql
-- Enable RLS on table
alter table public.posts enable row level security;

-- Disable RLS (dangerous - only for fully public tables)
alter table public.posts disable row level security;
```

### RLS Policy Types

| Policy Type | When Applied | Use Case |
|------------|--------------|----------|
| `FOR SELECT` | Read operations | Control visibility |
| `FOR INSERT` | Create operations | Control who can create |
| `FOR UPDATE` | Modify operations | Control who can edit |
| `FOR DELETE` | Delete operations | Control who can remove |
| `FOR ALL` | All operations | Apply same rule to all |

### Basic RLS Pattern

```sql
-- Users can only see their own posts
create policy "Users view own posts"
on public.posts for select
using (auth.uid() = user_id);

-- Users can only create posts for themselves
create policy "Users create own posts"
on public.posts for insert
with check (auth.uid() = user_id);

-- Users can only update their own posts
create policy "Users update own posts"
on public.posts for update
using (auth.uid() = user_id);

-- Users can only delete their own posts
create policy "Users delete own posts"
on public.posts for delete
using (auth.uid() = user_id);
```

## Common RLS Patterns

### 1. User-Owned Resources

```sql
create table public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) not null,
  title text not null,
  content text,
  created_at timestamptz default now()
);

alter table public.documents enable row level security;

-- Own documents only
create policy "Users manage own documents"
on public.documents for all
using (auth.uid() = user_id);
```

### 2. Public Read, Authenticated Write

```sql
create table public.blog_posts (
  id uuid primary key default gen_random_uuid(),
  author_id uuid references auth.users(id) not null,
  title text not null,
  content text,
  published boolean default false,
  created_at timestamptz default now()
);

alter table public.blog_posts enable row level security;

-- Anyone can read published posts
create policy "Public can view published posts"
on public.blog_posts for select
using (published = true);

-- Authors can view their own posts (including drafts)
create policy "Authors view own posts"
on public.blog_posts for select
using (auth.uid() = author_id);

-- Only authors can insert/update/delete their posts
create policy "Authors manage own posts"
on public.blog_posts for all
using (auth.uid() = author_id);
```

### 3. Organization/Team-Based Access

```sql
create table public.organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz default now()
);

create table public.organization_members (
  organization_id uuid references public.organizations(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  role text not null check (role in ('owner', 'admin', 'member')),
  primary key (organization_id, user_id)
);

create table public.projects (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid references public.organizations(id) not null,
  name text not null,
  description text,
  created_at timestamptz default now()
);

-- Enable RLS
alter table public.organizations enable row level security;
alter table public.organization_members enable row level security;
alter table public.projects enable row level security;

-- Users see organizations they belong to
create policy "Members view organizations"
on public.organizations for select
using (
  exists (
    select 1 from public.organization_members
    where organization_id = organizations.id
      and user_id = auth.uid()
  )
);

-- Users see projects in their organizations
create policy "Members view org projects"
on public.projects for select
using (
  exists (
    select 1 from public.organization_members
    where organization_id = projects.organization_id
      and user_id = auth.uid()
  )
);

-- Only admins/owners can create projects
create policy "Admins create projects"
on public.projects for insert
with check (
  exists (
    select 1 from public.organization_members
    where organization_id = projects.organization_id
      and user_id = auth.uid()
      and role in ('owner', 'admin')
  )
);
```

### 4. Role-Based Access Control (RBAC)

```sql
-- Add role to user metadata
create table public.user_roles (
  user_id uuid references auth.users(id) primary key,
  role text not null check (role in ('user', 'moderator', 'admin')),
  created_at timestamptz default now()
);

create table public.sensitive_data (
  id uuid primary key default gen_random_uuid(),
  content text not null,
  created_at timestamptz default now()
);

alter table public.sensitive_data enable row level security;

-- Only admins can access
create policy "Admins only"
on public.sensitive_data for all
using (
  exists (
    select 1 from public.user_roles
    where user_id = auth.uid()
      and role = 'admin'
  )
);

-- Helper function
create or replace function public.is_admin()
returns boolean as $$
begin
  return exists (
    select 1 from public.user_roles
    where user_id = auth.uid()
      and role = 'admin'
  );
end;
$$ language plpgsql security definer;

-- Use helper function
create policy "Admins only (using function)"
on public.sensitive_data for all
using (public.is_admin());
```

### 5. Multi-Tenant Isolation

```sql
create table public.tenants (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz default now()
);

create table public.user_tenants (
  user_id uuid references auth.users(id),
  tenant_id uuid references public.tenants(id),
  primary key (user_id, tenant_id)
);

create table public.tenant_data (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references public.tenants(id) not null,
  content text not null,
  created_at timestamptz default now()
);

alter table public.tenant_data enable row level security;

-- Users only see data from their tenants
create policy "Users see own tenant data"
on public.tenant_data for select
using (
  tenant_id in (
    select tenant_id
    from public.user_tenants
    where user_id = auth.uid()
  )
);

-- Users can only insert data for their tenants
create policy "Users insert own tenant data"
on public.tenant_data for insert
with check (
  tenant_id in (
    select tenant_id
    from public.user_tenants
    where user_id = auth.uid()
  )
);
```

## Advanced RLS Patterns

### Time-Based Access

```sql
create table public.scheduled_posts (
  id uuid primary key default gen_random_uuid(),
  author_id uuid references auth.users(id),
  content text not null,
  publish_at timestamptz not null,
  created_at timestamptz default now()
);

alter table public.scheduled_posts enable row level security;

-- Public can only see published posts
create policy "View published posts"
on public.scheduled_posts for select
using (publish_at <= now());

-- Authors see all their posts
create policy "Authors view own posts"
on public.scheduled_posts for select
using (auth.uid() = author_id);
```

### Attribute-Based Access Control (ABAC)

```sql
create table public.files (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid references auth.users(id),
  visibility text check (visibility in ('private', 'team', 'public')),
  department text,
  created_at timestamptz default now()
);

alter table public.files enable row level security;

-- Complex access rules
create policy "Complex visibility rules"
on public.files for select
using (
  -- Own files
  auth.uid() = owner_id
  or
  -- Public files
  visibility = 'public'
  or
  -- Team files in same department
  (
    visibility = 'team'
    and department = (
      select department
      from public.user_profiles
      where user_id = auth.uid()
    )
  )
);
```

### Hierarchical Permissions

```sql
-- Folder structure with inheritance
create table public.folders (
  id uuid primary key default gen_random_uuid(),
  parent_id uuid references public.folders(id),
  owner_id uuid references auth.users(id),
  name text not null
);

create table public.folder_permissions (
  folder_id uuid references public.folders(id),
  user_id uuid references auth.users(id),
  permission text check (permission in ('read', 'write', 'admin')),
  inherited boolean default false,
  primary key (folder_id, user_id)
);

alter table public.folders enable row level security;

-- Check permissions with recursion
create or replace function has_folder_access(
  p_folder_id uuid,
  p_permission text
)
returns boolean as $$
begin
  return exists (
    with recursive folder_tree as (
      -- Start with target folder
      select id, parent_id from public.folders where id = p_folder_id
      union all
      -- Traverse up to parents
      select f.id, f.parent_id
      from public.folders f
      join folder_tree ft on ft.parent_id = f.id
    )
    select 1
    from public.folder_permissions fp
    join folder_tree ft on ft.id = fp.folder_id
    where fp.user_id = auth.uid()
      and (
        fp.permission = p_permission
        or fp.permission = 'admin'
      )
  );
end;
$$ language plpgsql security definer;

create policy "Users access folders with permission"
on public.folders for select
using (has_folder_access(id, 'read'));
```

## Security Functions

### Get Current User ID

```sql
-- Built-in Supabase function
select auth.uid();  -- Returns current user's UUID or NULL

-- Check if user is authenticated
select auth.uid() is not null;
```

### Get User Email

```sql
-- Built-in Supabase function
select auth.email();  -- Returns current user's email
```

### Get User JWT Claims

```sql
-- Access custom JWT claims
select auth.jwt() -> 'app_metadata' ->> 'role';
```

### Security Definer Functions

```sql
-- Function runs with owner's privileges, not caller's
create or replace function public.admin_delete_user(p_user_id uuid)
returns void as $$
begin
  -- Check if caller is admin
  if not public.is_admin() then
    raise exception 'Unauthorized';
  end if;

  -- Perform privileged operation
  delete from auth.users where id = p_user_id;
end;
$$ language plpgsql security definer;
```

## Bypassing RLS

### Service Role Key

- Bypasses ALL RLS policies
- Use ONLY in trusted server environments
- Never expose to clients
- Required for administrative operations

```javascript
// Server-side only!
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY  // ⚠️ Server-side only!
)

// This query bypasses RLS
const { data } = await supabase.from('users').select('*')
```

### SECURITY DEFINER Functions

```sql
-- Function bypasses RLS when marked security definer
create or replace function get_all_users()
returns setof public.users as $$
begin
  return query select * from public.users;
end;
$$ language plpgsql security definer;

-- Add additional access control within function
create or replace function get_all_users_admin_only()
returns setof public.users as $$
begin
  if not public.is_admin() then
    raise exception 'Admin access required';
  end if;

  return query select * from public.users;
end;
$$ language plpgsql security definer;
```

## Testing RLS Policies

### Manual Testing

```sql
-- Test as specific user
set request.jwt.claim.sub = 'user-uuid-here';

-- Test queries
select * from public.posts;  -- Should only show that user's posts

-- Reset
reset request.jwt.claim.sub;
```

### Automated Testing (pgTAP)

```sql
begin;
select plan(3);

-- Set test user
set request.jwt.claim.sub = '123e4567-e89b-12d3-a456-426614174000';

-- Test can see own posts
select is(
  (select count(*) from public.posts where user_id = '123e4567-e89b-12d3-a456-426614174000'),
  1::bigint,
  'User can see own posts'
);

-- Test cannot see other user's posts
select is(
  (select count(*) from public.posts where user_id != '123e4567-e89b-12d3-a456-426614174000'),
  0::bigint,
  'User cannot see other users'' posts'
);

-- Test cannot insert for other users
select throws_ok(
  $$insert into public.posts (user_id, title) values ('other-user-id', 'Test')$$,
  'User can only insert own posts'
);

select * from finish();
rollback;
```

## Common Security Vulnerabilities

### 1. Missing RLS Policies

```sql
-- ❌ VULNERABLE: RLS enabled but no policies
alter table public.sensitive_data enable row level security;
-- No policies defined = no one can access (even legitimate users)

-- ✅ SECURE: Define policies
create policy "Allow authenticated users"
on public.sensitive_data for select
using (auth.uid() is not null);
```

### 2. Overly Permissive Policies

```sql
-- ❌ VULNERABLE: Too permissive
create policy "All authenticated users"
on public.private_messages for all
using (auth.uid() is not null);  -- Any user can see/modify ANY message!

-- ✅ SECURE: Properly scoped
create policy "Users see own messages"
on public.private_messages for select
using (auth.uid() in (sender_id, recipient_id));
```

### 3. SQL Injection in Dynamic SQL

```sql
-- ❌ VULNERABLE: SQL injection
create or replace function search_users(p_name text)
returns setof public.users as $$
begin
  -- Never do this!
  return query execute 'select * from public.users where name = ''' || p_name || '''';
end;
$$ language plpgsql;

-- ✅ SECURE: Use parameterized queries
create or replace function search_users(p_name text)
returns setof public.users as $$
begin
  return query select * from public.users where name = p_name;
end;
$$ language plpgsql;
```

### 4. Exposing Sensitive Data in JWTs

```sql
-- ❌ VULNERABLE: Sensitive data in JWT
-- Don't store SSN, passwords, or sensitive PII in JWT claims

-- ✅ SECURE: Store only necessary identifiers
-- JWT should contain: user_id, email, role
-- Fetch sensitive data from database with RLS
```

## Data Encryption

### Column-Level Encryption

```sql
-- Install pgcrypto extension
create extension if not exists pgcrypto;

-- Encrypt sensitive data
create table public.user_secrets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id),
  encrypted_ssn bytea not null,  -- Encrypted field
  created_at timestamptz default now()
);

-- Insert encrypted data
insert into public.user_secrets (user_id, encrypted_ssn)
values (
  auth.uid(),
  pgp_sym_encrypt('123-45-6789', 'encryption-key')
);

-- Decrypt data (server-side only!)
select
  user_id,
  pgp_sym_decrypt(encrypted_ssn, 'encryption-key') as ssn
from public.user_secrets
where user_id = auth.uid();
```

### Hashing Passwords (if not using Supabase Auth)

```sql
-- Hash password
create or replace function hash_password(password text)
returns text as $$
begin
  return crypt(password, gen_salt('bf'));  -- Blowfish
end;
$$ language plpgsql;

-- Verify password
create or replace function verify_password(password text, hash text)
returns boolean as $$
begin
  return hash = crypt(password, hash);
end;
$$ language plpgsql;
```

## Audit Logging

```sql
create table public.audit_log (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users(id),
  action text not null,
  table_name text not null,
  record_id uuid,
  old_data jsonb,
  new_data jsonb,
  ip_address inet,
  created_at timestamptz default now()
);

-- Audit trigger function
create or replace function audit_trigger()
returns trigger as $$
begin
  insert into public.audit_log (
    user_id,
    action,
    table_name,
    record_id,
    old_data,
    new_data
  ) values (
    auth.uid(),
    TG_OP,
    TG_TABLE_NAME,
    coalesce(NEW.id, OLD.id),
    to_jsonb(OLD),
    to_jsonb(NEW)
  );

  return coalesce(NEW, OLD);
end;
$$ language plpgsql security definer;

-- Apply to tables
create trigger audit_users
after insert or update or delete on public.users
for each row execute function audit_trigger();
```

## Security Checklist

- [ ] RLS enabled on all public tables
- [ ] Policies defined for all CRUD operations
- [ ] Service role key stored securely (server-side only)
- [ ] JWT claims validated in policies
- [ ] Sensitive data encrypted at rest
- [ ] Audit logging for sensitive operations
- [ ] Input validation and sanitization
- [ ] Rate limiting on authentication endpoints
- [ ] Regular security audits of policies
- [ ] Monitoring for suspicious activity

## Next Steps

- Review **schema-design.md** for secure schema patterns
- Study **database-patterns.md** for multi-tenancy architectures
- Explore **tools-reference.md** for MCP security operations
