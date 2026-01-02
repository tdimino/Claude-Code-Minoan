# PostgreSQL/Supabase Schema Design Best Practices

## Core Principles

1. **Use UUIDs for primary keys** - Prevents enumeration attacks, better for distributed systems
2. **Always specify ON DELETE actions** - Prevents orphaned records
3. **Add timestamps to all tables** - Essential for debugging and auditing
4. **Use CHECK constraints** - Enforce data integrity at database level
5. **Index foreign keys** - Critical for query performance

## Standard Table Template

```sql
create table public.table_name (
  -- Primary key (always UUID)
  id uuid primary key default gen_random_uuid(),

  -- Foreign keys with explicit actions
  user_id uuid references auth.users(id) on delete cascade not null,
  organization_id uuid references public.organizations(id) on delete cascade,

  -- Data columns with constraints
  name text not null check (char_length(name) >= 3),
  email text unique not null check (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
  status text not null check (status in ('active', 'inactive', 'pending')) default 'pending',
  metadata jsonb default '{}'::jsonb,

  -- Timestamps (standard pattern)
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Indexes for performance
create index idx_table_name_user_id on public.table_name(user_id);
create index idx_table_name_status on public.table_name(status) where status = 'active';
create index idx_table_name_created_at on public.table_name(created_at desc);

-- Trigger for updated_at
create trigger set_updated_at
before update on public.table_name
for each row execute function public.set_updated_at();

-- Enable RLS
alter table public.table_name enable row level security;
```

## Column Types Best Practices

### Primary Keys
```sql
-- ✅ RECOMMENDED: UUID
id uuid primary key default gen_random_uuid()

-- ❌ AVOID: Serial (predictable, not distributed-system friendly)
id serial primary key

-- ✅ ALTERNATIVE: Identity columns (PostgreSQL 10+)
id bigint generated always as identity primary key
```

### Text vs VARCHAR
```sql
-- ✅ RECOMMENDED: Use TEXT (no performance difference)
name text not null

-- ❌ AVOID: VARCHAR unless specific length requirement
name varchar(255) not null

-- ✅ OK: VARCHAR with business constraint
postal_code varchar(10) not null
```

### Numeric Types
```sql
-- Money/Currency (use numeric for precision)
price numeric(10,2) not null  -- 10 digits, 2 decimal places

-- Integers
small_number smallint  -- -32768 to 32767
normal_number integer  -- -2 billion to 2 billion
big_number bigint      -- Very large numbers

-- Floating point (avoid for money!)
measurement real       -- 6 decimal precision
precise_measurement double precision  -- 15 decimal precision
```

### Dates and Times
```sql
-- ✅ RECOMMENDED: Always use timestamptz (with timezone)
created_at timestamptz not null default now()

-- ❌ AVOID: timestamp without timezone
created_at timestamp default now()

-- Date only
birth_date date

-- Time only
opening_time time
```

### JSON Types
```sql
-- ✅ RECOMMENDED: JSONB (binary, indexable, faster)
settings jsonb not null default '{}'::jsonb

-- ❌ AVOID: JSON (text-based, slower)
settings json

-- JSONB indexing
create index idx_settings_gin on public.users using gin (settings);

-- JSONB querying
select * from users where settings->>'theme' = 'dark';
select * from users where settings @> '{"notifications": true}';
```

### Arrays
```sql
-- Array columns
tags text[] default array[]::text[]

-- Check constraint
check (cardinality(tags) <= 10)

-- Index for array contains
create index idx_tags_gin on public.posts using gin (tags);

-- Querying
select * from posts where 'postgresql' = any(tags);
select * from posts where tags @> array['postgresql', 'database'];
```

### Enums
```sql
-- Create enum type
create type public.user_status as enum ('active', 'inactive', 'suspended', 'deleted');

-- Use in table
create table public.users (
  id uuid primary key default gen_random_uuid(),
  status public.user_status not null default 'active'
);

-- ⚠️ Caution: Enums are hard to modify. Alternative: check constraint
status text not null check (status in ('active', 'inactive', 'suspended')) default 'active'
```

## Constraints

### NOT NULL Constraints
```sql
-- Always explicit about nullability
email text not null
phone text  -- Explicitly nullable
```

### UNIQUE Constraints
```sql
-- Single column
email text unique not null

-- Multiple columns (composite)
unique (organization_id, slug)

-- With custom name
constraint unique_email unique (email)
```

### CHECK Constraints
```sql
-- Value ranges
age integer check (age >= 0 and age <= 150)

-- String patterns
email text check (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

-- Length constraints
username text check (char_length(username) between 3 and 20)

-- Enum-like behavior
status text check (status in ('draft', 'published', 'archived'))

-- Complex logic
check (
  (type = 'product' and price is not null) or
  (type = 'service' and hourly_rate is not null)
)
```

### Foreign Key Constraints
```sql
-- With ON DELETE CASCADE
organization_id uuid references public.organizations(id) on delete cascade

-- With ON DELETE SET NULL
manager_id uuid references public.users(id) on delete set null

-- With ON DELETE RESTRICT (default - prevents deletion)
category_id uuid references public.categories(id) on delete restrict

-- With ON UPDATE CASCADE
parent_id uuid references public.folders(id) on update cascade on delete cascade
```

## Indexes

### When to Index
- ✅ Foreign keys (always)
- ✅ Columns in WHERE clauses
- ✅ Columns in JOIN conditions
- ✅ Columns in ORDER BY
- ✅ Columns in GROUP BY
- ❌ Small tables (<1000 rows)
- ❌ Columns with low cardinality (few distinct values)

### B-tree Indexes (Default)
```sql
-- Single column
create index idx_users_email on public.users(email);

-- Composite (order matters!)
create index idx_posts_user_status on public.posts(user_id, status);

-- Partial index (filtered)
create index idx_active_users on public.users(created_at) where status = 'active';

-- Expression index
create index idx_users_lower_email on public.users(lower(email));
```

### GIN Indexes (for arrays, JSONB, full-text)
```sql
-- JSONB
create index idx_metadata_gin on public.products using gin (metadata);

-- Arrays
create index idx_tags_gin on public.posts using gin (tags);

-- Full-text search
create index idx_content_fts on public.documents using gin (to_tsvector('english', content));
```

### GiST Indexes (for geometric, full-text)
```sql
-- Full-text search (alternative to GIN)
create index idx_content_gist on public.documents using gist (to_tsvector('english', content));

-- PostGIS (geometric data)
create index idx_location_gist on public.places using gist (location);
```

### Monitoring Indexes
```sql
-- Unused indexes
select
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch,
  pg_size_pretty(pg_relation_size(indexrelid)) as index_size
from pg_stat_user_indexes
where idx_scan = 0
  and schemaname = 'public'
order by pg_relation_size(indexrelid) desc;

-- Missing indexes on foreign keys
select
  c.conrelid::regclass as table_name,
  string_agg(a.attname, ', ') as column_names
from pg_constraint c
join pg_attribute a on a.attnum = any(c.conkey) and a.attrelid = c.conrelid
where c.contype = 'f'
  and not exists (
    select 1 from pg_index i
    where i.indrelid = c.conrelid
      and c.conkey::integer[] <@ i.indkey::integer[]
  )
group by c.conrelid;
```

## Triggers and Functions

### Auto-Update Timestamp
```sql
-- Function
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- Apply to tables
create trigger set_updated_at
before update on public.users
for each row execute function public.set_updated_at();
```

### Auto-Create Profile on User Signup
```sql
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email, full_name)
  values (
    new.id,
    new.email,
    new.raw_user_meta_data->>'full_name'
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();
```

### Prevent Updates to Certain Columns
```sql
create or replace function public.prevent_id_update()
returns trigger as $$
begin
  if new.id != old.id then
    raise exception 'Cannot update id column';
  end if;
  return new;
end;
$$ language plpgsql;

create trigger prevent_id_update
before update on public.users
for each row execute function public.prevent_id_update();
```

## Normalization

### First Normal Form (1NF)
- Atomic values only (no arrays/nested structures)
- Each row is unique

```sql
-- ❌ NOT 1NF: Multiple values in one column
create table orders (
  id uuid primary key,
  products text  -- 'product1, product2, product3'
);

-- ✅ 1NF: Separate rows
create table order_items (
  id uuid primary key,
  order_id uuid references orders(id),
  product_id uuid references products(id)
);
```

### Second Normal Form (2NF)
- Must be in 1NF
- No partial dependencies (all non-key columns depend on entire primary key)

```sql
-- ❌ NOT 2NF: product_name depends only on product_id, not both PKs
create table order_items (
  order_id uuid,
  product_id uuid,
  product_name text,
  quantity integer,
  primary key (order_id, product_id)
);

-- ✅ 2NF: product_name in products table
create table products (
  id uuid primary key,
  name text
);

create table order_items (
  order_id uuid references orders(id),
  product_id uuid references products(id),
  quantity integer,
  primary key (order_id, product_id)
);
```

### Third Normal Form (3NF)
- Must be in 2NF
- No transitive dependencies (non-key columns depend only on primary key)

```sql
-- ❌ NOT 3NF: author_email depends on author_id
create table books (
  id uuid primary key,
  title text,
  author_id uuid,
  author_email text
);

-- ✅ 3NF: author_email in authors table
create table authors (
  id uuid primary key,
  email text
);

create table books (
  id uuid primary key,
  title text,
  author_id uuid references authors(id)
);
```

## Denormalization (Strategic)

When to denormalize:
- ✅ Heavy read workload (10:1 read/write ratio)
- ✅ Complex joins impacting performance
- ✅ Data rarely changes
- ❌ Heavy write workload
- ❌ Data changes frequently

### Example: Denormalizing for Performance
```sql
-- Normalized (many joins for display)
select
  p.title,
  a.name as author_name,
  c.name as category_name,
  count(r.id) as review_count,
  avg(r.rating) as avg_rating
from posts p
join authors a on a.id = p.author_id
join categories c on c.id = p.category_id
left join reviews r on r.post_id = p.id
group by p.id, a.name, c.name;

-- Denormalized (single table query)
create table posts_denormalized (
  id uuid primary key,
  title text,
  author_name text,      -- Denormalized
  category_name text,    -- Denormalized
  review_count integer,  -- Denormalized
  avg_rating numeric     -- Denormalized
);

-- Keep in sync with triggers or materialized views
```

## Common Patterns

### Soft Deletes
```sql
alter table public.posts add column deleted_at timestamptz;
alter table public.posts add column deleted_by uuid references auth.users(id);

-- View for active records
create view public.active_posts as
select * from public.posts where deleted_at is null;
```

### Audit Logging
```sql
create table public.audit_logs (
  id bigint generated always as identity primary key,
  table_name text not null,
  record_id uuid not null,
  action text not null,
  old_data jsonb,
  new_data jsonb,
  user_id uuid references auth.users(id),
  created_at timestamptz default now()
);
```

### Hierarchical Data (Adjacency List)
```sql
create table public.categories (
  id uuid primary key default gen_random_uuid(),
  parent_id uuid references public.categories(id),
  name text not null
);

-- Query with recursive CTE
with recursive category_tree as (
  -- Base case: root categories
  select id, parent_id, name, 1 as level
  from public.categories
  where parent_id is null

  union all

  -- Recursive case: child categories
  select c.id, c.parent_id, c.name, ct.level + 1
  from public.categories c
  join category_tree ct on ct.id = c.parent_id
)
select * from category_tree;
```

## Migration Best Practices

1. **Always reversible** - Write both up and down migrations
2. **Small, focused changes** - One logical change per migration
3. **Test on dev/staging** - Never run untested migrations in production
4. **Backward compatible** - Old code should work during deployment
5. **Use transactions** - Wrap in BEGIN/COMMIT for atomicity

### Safe Migration Example
```sql
-- Add column (nullable first, then add NOT NULL after data backfill)
alter table public.users add column phone text;

-- Backfill data
update public.users set phone = '' where phone is null;

-- Make NOT NULL in separate migration after verifying backfill
alter table public.users alter column phone set not null;
```

## Tools and Extensions

### Useful PostgreSQL Extensions
```sql
-- UUID generation
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";  -- gen_random_uuid()

-- Full-text search
create extension if not exists "pg_trgm";

-- PostGIS (geographic data)
create extension if not exists "postgis";

-- TimescaleDB (time-series data)
create extension if not exists "timescaledb";
```

## Next Steps

- Review **security.md** for RLS implementation
- Study **database-patterns.md** for advanced designs
- Explore **tools-reference.md** for MCP operations
