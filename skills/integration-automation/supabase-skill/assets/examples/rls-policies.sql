-- Row Level Security (RLS) Policy Examples
-- Source: Production patterns from Supabase documentation and Twilio-Aldea

-- ========================================
-- 1. USER-OWNED DATA (Most Common Pattern)
-- ========================================

-- Enable RLS on profiles table
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "Users can view own profile"
ON profiles
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- Users can insert their own data
CREATE POLICY "Users can insert own profile"
ON profiles
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Users can update their own data
CREATE POLICY "Users can update own profile"
ON profiles
FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- ========================================
-- 2. PUBLIC READ, AUTHENTICATED WRITE
-- ========================================

-- Anyone can read profiles
CREATE POLICY "Public profiles are viewable by everyone"
ON profiles
FOR SELECT
USING (true);

-- Only authenticated users can create posts
CREATE POLICY "Authenticated users can create posts"
ON posts
FOR INSERT
TO authenticated
WITH CHECK (true);

-- ========================================
-- 3. ROLE-BASED ACCESS (RBAC)
-- ========================================

-- Create helper function (security definer to avoid RLS recursion)
CREATE SCHEMA IF NOT EXISTS private;

CREATE OR REPLACE FUNCTION private.get_user_org_role(org_id bigint, user_id uuid)
RETURNS text
LANGUAGE sql
SECURITY DEFINER
SET search_path = ''
AS $$
  SELECT role FROM org_members
  WHERE org_id = $1 AND user_id = $2;
$$;

-- Policy using role check
CREATE POLICY "Admins and owners can manage posts"
ON posts
FOR ALL
USING (
  private.get_user_org_role(org_id, auth.uid()) IN ('owner', 'admin')
);

-- ========================================
-- 4. MULTI-TENANT WITH ORGANIZATION
-- ========================================

-- Users can only see their organization's data
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

-- ========================================
-- 5. COMPLEX BUSINESS LOGIC
-- ========================================

-- Posts visible based on status, premium, and role
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
  private.get_user_org_role(org_id, auth.uid()) IN ('owner', 'admin', 'editor')
);

-- ========================================
-- 6. RESTRICTIVE POLICIES (MFA Requirement)
-- ========================================

-- Require MFA for sensitive data
CREATE POLICY "Require MFA for private posts"
ON private_posts
AS RESTRICTIVE
FOR SELECT
TO authenticated
USING ((auth.jwt()->>'aal') = 'aal2');

-- ========================================
-- 7. TIME-BASED ACCESS
-- ========================================

-- Only show active subscriptions
CREATE POLICY "Active subscriptions only"
ON subscriptions
FOR SELECT
USING (
  status = 'active'
  AND expires_at > now()
  AND user_id = auth.uid()
);

-- ========================================
-- 8. REALTIME AUTHORIZATION
-- ========================================

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

CREATE POLICY "Users can send to their room"
ON realtime.messages
FOR INSERT
TO authenticated
WITH CHECK (
  EXISTS (
    SELECT 1 FROM rooms_users
    WHERE user_id = auth.uid()
    AND room_topic = realtime.topic()
  )
);

-- ========================================
-- 9. SERVICE ROLE BYPASS
-- ========================================

-- Allow service role to bypass RLS for admin operations
CREATE POLICY "Service role can manage all users"
ON users
FOR ALL
USING (
  current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
);

-- ========================================
-- 10. CONDITIONAL INSERT WITH LIMITS
-- ========================================

-- Check organization post limits before allowing insert
CREATE POLICY "Respect post limits"
ON posts
FOR INSERT
WITH CHECK (
  -- Free plan check
  (SELECT plan_type FROM organizations WHERE id = org_id) != 'free'
  OR
  -- Within limits
  (SELECT count(*) FROM posts WHERE org_id = posts.org_id) <
  (SELECT max_posts FROM organizations WHERE id = posts.org_id)
);
