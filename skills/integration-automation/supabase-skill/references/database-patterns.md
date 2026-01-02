# Database Design Patterns for Supabase

## Overview

This guide covers modern database design patterns for building scalable, maintainable, and future-proof applications with Supabase and PostgreSQL. These patterns have been battle-tested across thousands of production applications.

## Foundational Principles

### The Four Pillars of Future-Proof Architecture

**1. Decoupled & Portable Business Logic**
- Separate business rules from storage technology
- Use database functions and triggers for reusable logic
- Avoid hard-coding platform-specific dependencies

**2. Automated Construction & Lifecycle Management**
- Leverage migrations for all schema changes
- Use version control for database schemas
- Implement CI/CD for database deployments

**3. Natively Integrated Governance & Quality**
- Build security (RLS) into the schema from day one
- Implement audit trails as part of the architecture
- Enforce data quality through constraints and triggers

**4. Unified Metadata Framework**
- Document schema changes comprehensively
- Maintain data dictionaries and lineage
- Use Supabase's automatic API generation

## Architectural Patterns

### 1. The Data Lakehouse Pattern

**When to Use:**
- Need to support both transactional and analytical workloads
- Want to avoid maintaining separate OLTP and OLAP systems
- Require flexible schema evolution

**Implementation in Supabase:**
```sql
-- Transactional tables for real-time operations
create table public.orders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id),
  total numeric(10,2) not null,
  status text check (status in ('pending', 'completed', 'cancelled')),
  created_at timestamptz default now()
);

-- Materialized view for analytics
create materialized view public.orders_analytics as
select
  date_trunc('day', created_at) as order_date,
  count(*) as total_orders,
  sum(total) as revenue,
  avg(total) as avg_order_value
from public.orders
where status = 'completed'
group by date_trunc('day', created_at);

-- Refresh periodically
create or replace function refresh_analytics()
returns void as $$
begin
  refresh materialized view public.orders_analytics;
end;
$$ language plpgsql;

-- Schedule refresh (using pg_cron extension)
select cron.schedule('refresh-analytics', '0 * * * *', 'select refresh_analytics()');
```

**Benefits:**
- Single source of truth for all data
- No ETL between systems
- Consistent governance and security
- Cost-effective storage

### 2. The Microservices Pattern (Database per Service)

**When to Use:**
- Building microservices architecture
- Need independent deployment of services
- Want to scale services independently

**Implementation:**
```sql
-- Service 1: User Service (separate Supabase project)
create table users_service.users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  name text,
  created_at timestamptz default now()
);

-- Service 2: Order Service (separate Supabase project)
create table orders_service.orders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,  -- Foreign key to users_service (via API)
  total numeric(10,2),
  created_at timestamptz default now()
);

-- Use Edge Functions to coordinate across services
create or replace function orders_service.create_order_with_user(
  p_user_id uuid,
  p_total numeric
)
returns uuid as $$
declare
  v_order_id uuid;
begin
  -- Call User Service API to verify user exists
  -- (implementation via Edge Function with Supabase-to-Supabase auth)

  -- Create order
  insert into orders_service.orders (user_id, total)
  values (p_user_id, p_total)
  returning id into v_order_id;

  return v_order_id;
end;
$$ language plpgsql security definer;
```

**Trade-offs:**
- ✅ Independent scaling and deployment
- ✅ Technology flexibility per service
- ❌ Distributed transaction complexity
- ❌ Cross-service query challenges

**Solution: Event-Driven Communication**
```sql
-- Publish events using pg_notify
create or replace function orders_service.notify_order_created()
returns trigger as $$
begin
  perform pg_notify(
    'order_created',
    json_build_object(
      'order_id', NEW.id,
      'user_id', NEW.user_id,
      'total', NEW.total
    )::text
  );
  return NEW;
end;
$$ language plpgsql;

create trigger order_created_trigger
after insert on orders_service.orders
for each row execute function orders_service.notify_order_created();
```

### 3. The Event Sourcing Pattern

**When to Use:**
- Need complete audit trail of all changes
- Want to reconstruct state at any point in time
- Require event replay for debugging or analytics

**Implementation:**
```sql
-- Event store table
create table public.events (
  id bigint generated always as identity primary key,
  aggregate_id uuid not null,
  aggregate_type text not null,
  event_type text not null,
  event_data jsonb not null,
  event_metadata jsonb,
  user_id uuid references auth.users(id),
  created_at timestamptz default now() not null,

  -- Indexing for queries
  index idx_events_aggregate on events(aggregate_type, aggregate_id),
  index idx_events_type on events(event_type),
  index idx_events_created on events(created_at)
);

-- Example: Order events
create or replace function create_order_event(
  p_order_id uuid,
  p_event_type text,
  p_event_data jsonb
)
returns bigint as $$
declare
  v_event_id bigint;
begin
  insert into public.events (
    aggregate_id,
    aggregate_type,
    event_type,
    event_data,
    user_id
  ) values (
    p_order_id,
    'order',
    p_event_type,
    p_event_data,
    auth.uid()
  )
  returning id into v_event_id;

  return v_event_id;
end;
$$ language plpgsql security definer;

-- Materialized view for current state
create materialized view public.orders_current_state as
select
  aggregate_id as order_id,
  (event_data->>'user_id')::uuid as user_id,
  (event_data->>'total')::numeric as total,
  (event_data->>'status')::text as status,
  max(created_at) as last_updated
from public.events
where aggregate_type = 'order'
  and event_type = 'order_created' or event_type = 'order_updated'
group by aggregate_id, event_data;

-- Function to reconstruct state at any point
create or replace function get_order_state_at(
  p_order_id uuid,
  p_at_time timestamptz
)
returns jsonb as $$
declare
  v_state jsonb := '{}';
  r record;
begin
  for r in
    select event_type, event_data
    from public.events
    where aggregate_id = p_order_id
      and aggregate_type = 'order'
      and created_at <= p_at_time
    order by created_at
  loop
    v_state := v_state || r.event_data;
  end loop;

  return v_state;
end;
$$ language plpgsql;
```

**Benefits:**
- Complete audit trail automatically
- Time travel queries
- Event replay for debugging
- Natural fit for CQRS pattern

### 4. CQRS (Command Query Responsibility Segregation)

**When to Use:**
- Read and write patterns are significantly different
- Need to optimize reads and writes independently
- Want to scale read and write workloads separately

**Implementation:**
```sql
-- WRITE MODEL: Normalized for data integrity
create table public.products (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  category_id uuid references public.categories(id),
  base_price numeric(10,2) not null,
  created_at timestamptz default now()
);

create table public.product_attributes (
  id uuid primary key default gen_random_uuid(),
  product_id uuid references public.products(id) on delete cascade,
  attribute_name text not null,
  attribute_value text not null,
  unique(product_id, attribute_name)
);

-- READ MODEL: Denormalized for query performance
create table public.products_read_model (
  id uuid primary key,
  name text not null,
  category_name text not null,
  category_slug text not null,
  base_price numeric(10,2) not null,
  attributes jsonb not null,  -- All attributes denormalized
  search_vector tsvector,     -- Full-text search
  created_at timestamptz not null,
  updated_at timestamptz not null
);

-- Sync write model to read model
create or replace function sync_product_to_read_model()
returns trigger as $$
begin
  -- Delete old read model entry
  delete from public.products_read_model where id = NEW.id;

  -- Insert updated read model
  insert into public.products_read_model
  select
    p.id,
    p.name,
    c.name as category_name,
    c.slug as category_slug,
    p.base_price,
    (
      select jsonb_object_agg(attribute_name, attribute_value)
      from public.product_attributes
      where product_id = p.id
    ) as attributes,
    to_tsvector('english', p.name || ' ' || c.name) as search_vector,
    p.created_at,
    now() as updated_at
  from public.products p
  join public.categories c on c.id = p.category_id
  where p.id = NEW.id;

  return NEW;
end;
$$ language plpgsql;

create trigger product_write_trigger
after insert or update on public.products
for each row execute function sync_product_to_read_model();
```

**Benefits:**
- Optimized queries without joins
- Independent scaling of reads/writes
- Complex queries simplified

**Trade-offs:**
- Eventual consistency between models
- More complex maintenance
- Storage duplication

## Data Modeling Patterns

### 5. Single Table Inheritance

**When to Use:**
- Multiple entity types share most attributes
- Differences are minor variations

**Implementation:**
```sql
create table public.people (
  id uuid primary key default gen_random_uuid(),
  type text not null check (type in ('employee', 'customer', 'vendor')),

  -- Common attributes
  name text not null,
  email text unique not null,
  phone text,
  address jsonb,

  -- Employee-specific (nullable)
  employee_id text unique,
  department text,
  salary numeric(10,2),
  hire_date date,

  -- Customer-specific (nullable)
  customer_since date,
  loyalty_points integer,

  -- Vendor-specific (nullable)
  vendor_code text unique,
  payment_terms text,

  created_at timestamptz default now()
);

-- Type-specific views
create view public.employees as
select
  id,
  name,
  email,
  phone,
  employee_id,
  department,
  salary,
  hire_date,
  created_at
from public.people
where type = 'employee';

create view public.customers as
select
  id,
  name,
  email,
  phone,
  customer_since,
  loyalty_points,
  created_at
from public.people
where type = 'customer';
```

**Benefits:**
- Simple queries across all types
- Easy to add shared attributes
- Minimal joins

**Trade-offs:**
- Many nullable columns
- Less type safety
- Possible data integrity issues

### 6. Class Table Inheritance

**When to Use:**
- Entity types have significantly different attributes
- Need strong type enforcement
- Willing to accept join overhead

**Implementation:**
```sql
-- Base table
create table public.people (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text unique not null,
  phone text,
  created_at timestamptz default now()
);

-- Specialized tables
create table public.employees (
  id uuid primary key references public.people(id) on delete cascade,
  employee_id text unique not null,
  department text not null,
  salary numeric(10,2) not null,
  hire_date date not null
);

create table public.customers (
  id uuid primary key references public.people(id) on delete cascade,
  customer_since date not null default current_date,
  loyalty_points integer not null default 0,
  credit_limit numeric(10,2)
);

-- Unified view
create view public.all_people as
select
  p.*,
  'employee' as type,
  e.employee_id,
  e.department,
  e.salary,
  null::date as customer_since,
  null::integer as loyalty_points
from public.people p
join public.employees e on e.id = p.id

union all

select
  p.*,
  'customer' as type,
  null::text as employee_id,
  null::text as department,
  null::numeric as salary,
  c.customer_since,
  c.loyalty_points
from public.people p
join public.customers c on c.id = p.id;
```

**Benefits:**
- Type safety
- No nullable columns
- Clear separation of concerns

**Trade-offs:**
- More complex queries (joins)
- Additional tables to maintain

### 7. Polymorphic Associations

**When to Use:**
- One entity can relate to multiple different entity types
- Need flexibility in relationships

**Implementation:**
```sql
-- Comments can belong to posts, photos, or videos
create table public.comments (
  id uuid primary key default gen_random_uuid(),
  commentable_type text not null check (commentable_type in ('post', 'photo', 'video')),
  commentable_id uuid not null,
  user_id uuid references auth.users(id) not null,
  content text not null,
  created_at timestamptz default now(),

  -- Composite index for polymorphic lookups
  index idx_commentable on comments(commentable_type, commentable_id)
);

-- Helper function for type-safe access
create or replace function get_comments_for(
  p_type text,
  p_id uuid
)
returns setof public.comments as $$
begin
  return query
  select * from public.comments
  where commentable_type = p_type
    and commentable_id = p_id
  order by created_at desc;
end;
$$ language plpgsql;

-- Usage
select * from get_comments_for('post', '123e4567-e89b-12d3-a456-426614174000');
```

**Alternative: Junction Tables (More Type-Safe)**
```sql
-- Separate junction tables per type
create table public.post_comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid references public.posts(id) on delete cascade,
  user_id uuid references auth.users(id),
  content text not null,
  created_at timestamptz default now()
);

create table public.photo_comments (
  id uuid primary key default gen_random_uuid(),
  photo_id uuid references public.photos(id) on delete cascade,
  user_id uuid references auth.users(id),
  content text not null,
  created_at timestamptz default now()
);

-- Unified view
create view public.all_comments as
select id, 'post' as type, post_id as item_id, user_id, content, created_at
from public.post_comments
union all
select id, 'photo' as type, photo_id as item_id, user_id, content, created_at
from public.photo_comments;
```

### 8. Temporal Data Pattern (SCD Type 2)

**When to Use:**
- Need to track historical changes
- Require point-in-time queries
- Must audit all modifications

**Implementation:**
```sql
create table public.products_history (
  id uuid not null,
  name text not null,
  price numeric(10,2) not null,
  description text,

  -- Temporal columns
  valid_from timestamptz not null default now(),
  valid_to timestamptz,  -- null means current version

  -- Audit columns
  changed_by uuid references auth.users(id),
  change_reason text,

  primary key (id, valid_from)
);

-- Current products view
create view public.products as
select id, name, price, description
from public.products_history
where valid_to is null;

-- Function to update product (creates new version)
create or replace function update_product(
  p_id uuid,
  p_name text,
  p_price numeric,
  p_description text,
  p_change_reason text
)
returns void as $$
begin
  -- Close current version
  update public.products_history
  set valid_to = now()
  where id = p_id and valid_to is null;

  -- Insert new version
  insert into public.products_history (
    id, name, price, description, changed_by, change_reason
  ) values (
    p_id, p_name, p_price, p_description, auth.uid(), p_change_reason
  );
end;
$$ language plpgsql security definer;

-- Query product at specific time
create or replace function get_product_at(
  p_id uuid,
  p_at_time timestamptz
)
returns public.products_history as $$
begin
  return query
  select *
  from public.products_history
  where id = p_id
    and valid_from <= p_at_time
    and (valid_to is null or valid_to > p_at_time);
end;
$$ language plpgsql;
```

### 9. Multi-Tenancy Patterns

**Pattern A: Shared Schema with Tenant Column**
```sql
-- All tenants share same tables
create table public.documents (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id),
  title text not null,
  content text,
  created_at timestamptz default now(),

  -- Index for tenant queries
  index idx_documents_tenant on documents(tenant_id)
);

-- RLS for automatic tenant isolation
alter table public.documents enable row level security;

create policy "Users can only see own tenant documents"
on public.documents for select
using (
  tenant_id in (
    select tenant_id
    from public.user_tenants
    where user_id = auth.uid()
  )
);
```

**Pattern B: Schema per Tenant**
```sql
-- Create schema for each tenant
create schema tenant_acme;
create schema tenant_globex;

-- Tables in each schema
create table tenant_acme.documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  content text
);

create table tenant_globex.documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  content text
);

-- Set search path based on tenant
create or replace function set_tenant_context(p_tenant_id uuid)
returns void as $$
declare
  v_schema_name text;
begin
  select schema_name into v_schema_name
  from public.tenants
  where id = p_tenant_id;

  execute format('SET search_path TO %I, public', v_schema_name);
end;
$$ language plpgsql;
```

**Pattern C: Database per Tenant (Separate Supabase Projects)**
- Most isolated
- Highest security
- Independent scaling
- Separate backups

### 10. Soft Delete Pattern

**Implementation:**
```sql
create table public.posts (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  content text,
  author_id uuid references auth.users(id),

  -- Soft delete columns
  deleted_at timestamptz,
  deleted_by uuid references auth.users(id),

  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Active posts view
create view public.active_posts as
select *
from public.posts
where deleted_at is null;

-- Function for soft delete
create or replace function soft_delete_post(p_id uuid)
returns void as $$
begin
  update public.posts
  set
    deleted_at = now(),
    deleted_by = auth.uid()
  where id = p_id
    and deleted_at is null;
end;
$$ language plpgsql security definer;

-- Function for hard delete (permanent)
create or replace function hard_delete_old_posts(p_days integer)
returns integer as $$
declare
  v_deleted integer;
begin
  delete from public.posts
  where deleted_at < now() - (p_days || ' days')::interval;

  get diagnostics v_deleted = row_count;
  return v_deleted;
end;
$$ language plpgsql;
```

## Choosing the Right Pattern

### Decision Matrix

| Use Case | Recommended Pattern | Reason |
|----------|-------------------|--------|
| E-commerce platform | CQRS + Event Sourcing | Complex queries, audit requirements |
| SaaS application | Multi-tenancy (Shared Schema) | Cost-effective, easy maintenance |
| Microservices | Database per Service | Independent scaling, deployment |
| Content management | Temporal Data | Version history, publishing workflows |
| Social network | Polymorphic Associations | Flexible relationships (likes, comments) |
| Enterprise system | Class Table Inheritance | Strong typing, complex hierarchies |

### Pattern Selection Criteria

**Consider these factors:**

1. **Data Volume** - Affects storage strategy
2. **Query Patterns** - Influences denormalization decisions
3. **Consistency Requirements** - Determines transaction boundaries
4. **Scalability Needs** - Guides partitioning and sharding
5. **Team Size/Skill** - Impacts pattern complexity choices
6. **Compliance Requirements** - Mandates audit and encryption patterns

## Anti-Patterns to Avoid

### 1. God Table
**Problem:** Single table with 50+ columns storing everything

**Solution:** Decompose into logical entities with proper relationships

### 2. Premature Optimization
**Problem:** Complex denormalization before understanding query patterns

**Solution:** Start normalized, optimize based on real usage data

### 3. No Primary Keys
**Problem:** Tables without primary keys, using composite natural keys

**Solution:** Always use surrogate keys (UUID or serial)

### 4. Ignoring Indexes
**Problem:** Slow queries due to missing indexes

**Solution:** Index foreign keys, frequently queried columns

### 5. Application-Only Security
**Problem:** Relying solely on application logic for access control

**Solution:** Implement RLS at database level

## Next Steps

- Review **schema-design.md** for implementation details
- Study **security.md** for RLS patterns
- Explore **tools-reference.md** for MCP operations on these patterns
