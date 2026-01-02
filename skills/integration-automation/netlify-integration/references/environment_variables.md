# Environment Variables Management

Guide to managing environment variables in Netlify for Next.js applications.

## Environment Variable Scopes

Netlify supports multiple deployment contexts:

1. **Production** - Main branch deployments
2. **Deploy Previews** - Pull request deployments
3. **Branch Deploys** - Non-main branch deployments
4. **All** - Applies to all contexts

## Setting Environment Variables

### Via Netlify Dashboard

1. Go to Site settings → Environment variables
2. Click "Add a variable"
3. Enter key and value
4. Select scopes (Production, Deploy previews, Branch deploys)
5. Click "Create variable"

### Via Netlify CLI

```bash
# Set single variable
netlify env:set VARIABLE_NAME value

# Set with specific scope
netlify env:set VARIABLE_NAME value --context production

# Import from .env file
netlify env:import .env.production

# List all variables
netlify env:list

# Get specific variable
netlify env:get VARIABLE_NAME

# Delete variable
netlify env:unset VARIABLE_NAME
```

### Bulk Import

Create `.env.production` file:
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...
TELNYX_API_KEY=KEY019A...
```

Import:
```bash
netlify env:import .env.production
```

## Next.js Environment Variables

### Server-Side Variables

Available only in API routes and serverless functions:

```typescript
// .env
DATABASE_URL=postgresql://...
API_SECRET_KEY=secret123

// Usage in API route
export default async function handler(req, res) {
  const dbUrl = process.env.DATABASE_URL;
  const apiKey = process.env.API_SECRET_KEY;
  // Only available server-side
}
```

### Client-Side Variables

Must be prefixed with `NEXT_PUBLIC_`:

```typescript
// .env
NEXT_PUBLIC_APP_URL=https://myapp.com
NEXT_PUBLIC_ANALYTICS_ID=GA-123456

// Usage in components
export default function Component() {
  const appUrl = process.env.NEXT_PUBLIC_APP_URL;
  const analyticsId = process.env.NEXT_PUBLIC_ANALYTICS_ID;
  // Available client-side
}
```

## Required Variables for Twilio-Aldea

### Database
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### SMS Provider (Telnyx)
```bash
SMS_PROVIDER=telnyx
TELNYX_API_KEY=KEY019A080F468AAFD4AF4F6888D7795244_xxx
TELNYX_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----\nMIIBIj...
```

### SMS Provider (Twilio - Alternative)
```bash
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Application
```bash
NEXT_PUBLIC_APP_URL=https://your-site.netlify.app
NEXTAUTH_SECRET=random-secret-string-min-32-chars
NODE_ENV=production
```

### LLM/AI
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Build-Time vs Runtime Variables

### Build-Time Variables

Set in `netlify.toml` or Netlify Dashboard, available during build:

```toml
[build.environment]
  NODE_VERSION = "18"
  NEXT_TELEMETRY_DISABLED = "1"
```

### Runtime Variables

Set in Netlify Dashboard, available at runtime in functions:

```bash
# These are NOT in netlify.toml (security)
SUPABASE_SERVICE_KEY=...
TELNYX_API_KEY=...
```

## Security Best Practices

### Never Commit Secrets
```bash
# .gitignore
.env
.env.local
.env.production
.env.*.local
```

### Use .env.example
```bash
# .env.example (commit this)
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_service_key_here
TELNYX_API_KEY=your_telnyx_key_here
NEXT_PUBLIC_APP_URL=your_app_url_here
```

### Rotate Secrets Regularly
1. Generate new key/secret
2. Update in Netlify Dashboard
3. Deploy to apply changes
4. Invalidate old key/secret

### Use Different Keys Per Environment
```bash
# Production
TELNYX_API_KEY=KEY_PROD_xxx

# Staging (deploy previews)
TELNYX_API_KEY=KEY_STAGING_xxx

# Development (branch deploys)
TELNYX_API_KEY=KEY_DEV_xxx
```

## Context-Specific Variables

Set different values per deployment context:

### Via Dashboard
1. Site settings → Environment variables
2. Add variable
3. Select specific scopes:
   - ✅ Production deployments
   - ✅ Deploy previews
   - ✅ Branch deploys

### Via netlify.toml
```toml
[context.production.environment]
  API_URL = "https://api.production.com"
  LOG_LEVEL = "error"

[context.deploy-preview.environment]
  API_URL = "https://api.staging.com"
  LOG_LEVEL = "debug"

[context.branch-deploy.environment]
  API_URL = "https://api.dev.com"
  LOG_LEVEL = "debug"
```

## Local Development

### Setup Local Environment

1. Copy example file:
```bash
cp .env.example .env.local
```

2. Fill in local values:
```bash
# .env.local
SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_KEY=your_local_key
TELNYX_API_KEY=test_key
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

3. Run with Netlify Dev:
```bash
netlify dev
# Automatically loads .env files
```

### Testing with Production Variables

```bash
# Link to Netlify site
netlify link

# Pull environment variables from production
netlify env:clone --from production

# Creates .env file with production values
```

## Troubleshooting

### Variables Not Available in Functions

**Symptom:** `process.env.VARIABLE_NAME` returns `undefined`

**Solutions:**
1. Verify variable is set in Netlify Dashboard
2. Check variable scope includes your deployment context
3. Redeploy site to pick up new variables
4. Check spelling and casing (case-sensitive)

### Variables Not Available in Build

**Symptom:** Build fails with missing environment variable

**Solutions:**
1. Add to `netlify.toml` build.environment section
2. Or set in Netlify Dashboard with build scope
3. Ensure not using `NEXT_PUBLIC_` prefix for server-only vars

### Client-Side Variables Not Working

**Symptom:** `process.env.NEXT_PUBLIC_VAR` is `undefined` in browser

**Solutions:**
1. Ensure variable starts with `NEXT_PUBLIC_`
2. Rebuild application (client vars are embedded at build time)
3. Check browser console for any build warnings

### Variable Value Appears Incorrect

**Solutions:**
1. Check for trailing spaces in value
2. Verify correct deployment context
3. Clear and redeploy
4. Check if variable was recently updated (requires redeploy)

## Helper Script

Use the included helper script for bulk setup:

```bash
scripts/setup_env_vars.sh
```

Interactive prompts for all required variables, automatically sets in Netlify.

## Resources

- [Netlify Environment Variables Docs](https://docs.netlify.com/environment-variables/overview/)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)
- [Netlify CLI Environment Commands](https://cli.netlify.com/commands/env/)
