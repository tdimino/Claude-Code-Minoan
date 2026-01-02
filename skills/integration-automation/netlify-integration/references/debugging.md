# Debugging and Troubleshooting Guide

Comprehensive guide for debugging Netlify deployments and functions.

## Build Failures

### TypeScript Errors

**Symptom:** Build fails with TypeScript compilation errors

**Debug Steps:**
```bash
# Run build locally
npm run build

# Check TypeScript errors
npx tsc --noEmit

# Fix errors in source files
# Then commit and redeploy
```

### Dependency Issues

**Symptom:** `Module not found` or dependency errors

**Debug Steps:**
```bash
# Verify package.json
cat package.json

# Clear lock file and reinstall
rm package-lock.json
npm install

# Set NPM flags in netlify.toml
[build.environment]
  NPM_FLAGS = "--legacy-peer-deps"
```

### Node Version Mismatch

**Symptom:** Build works locally but fails on Netlify

**Debug Steps:**
```bash
# Check local Node version
node --version

# Set in netlify.toml
[build.environment]
  NODE_VERSION = "18"  # Match your local version
```

## Function Errors

### Function Timeout

**Symptom:** Function returns 504 Gateway Timeout

**Causes:**
- Function execution exceeds timeout (10s default)
- Long database queries
- External API calls taking too long
- Cold start delays

**Solutions:**

1. **Increase timeout:**
```toml
# netlify.toml
[[functions."slow-function"]]
  timeout = 26  # Max 26s for Pro, 10s for free
```

2. **Return response immediately, process async:**
```typescript
export const handler: Handler = async (event, context) => {
  // Return 200 immediately
  const response = { statusCode: 200, body: JSON.stringify({ received: true }) };

  // Process async
  processAsync(event).catch(console.error);

  return response;
};
```

3. **Optimize database queries:**
```sql
-- Add indexes
CREATE INDEX idx_messages_phone ON messages(from_number);

-- Limit result set
SELECT * FROM messages WHERE from_number = $1 LIMIT 10;
```

### Function 404 Not Found

**Symptom:** Calling function returns 404

**Debug Steps:**

1. **Verify function exists:**
```bash
netlify functions:list
```

2. **Check redirects in netlify.toml:**
```toml
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
  force = true
```

3. **Verify function file structure:**
```
.netlify/
  functions/
    webhook.ts  ✅ Correct
    webhook/index.ts  ✅ Also correct
```

4. **Check function export:**
```typescript
// ❌ Wrong
export default async function handler() {}

// ✅ Correct
export const handler: Handler = async () => {}
```

### Function 500 Internal Server Error

**Debug Steps:**

1. **View function logs:**
```bash
netlify functions:log function-name
```

2. **Add comprehensive logging:**
```typescript
export const handler: Handler = async (event, context) => {
  console.log("Function invoked:", {
    httpMethod: event.httpMethod,
    path: event.path,
    headers: event.headers,
    body: event.body,
  });

  try {
    // Your code
  } catch (error) {
    console.error("Error details:", {
      message: error instanceof Error ? error.message : "Unknown",
      stack: error instanceof Error ? error.stack : undefined,
    });
    throw error;
  }
};
```

3. **Check environment variables:**
```bash
netlify env:list
# Verify all required variables are set
```

## Webhook Issues

### Webhook Timeouts (Critical for Twilio-Aldea)

**Symptom:** 60% message loss, webhook timeout errors

**Root Causes:**
1. Function execution time > 10 seconds
2. Database operations taking too long
3. Not returning response before async processing
4. Cold start delays

**Solutions:**

**1. Immediate Response Pattern:**
```typescript
export const handler: Handler = async (event, context) => {
  // Log receipt
  console.log("Webhook received");

  // Validate signature quickly
  const isValid = validateSignature(event);
  if (!isValid) {
    return { statusCode: 401, body: "Unauthorized" };
  }

  // Return 200 IMMEDIATELY (< 1s)
  const response = {
    statusCode: 200,
    body: JSON.stringify({ received: true }),
  };

  // Don't await - process async
  processWebhook(event)
    .catch(error => console.error("Processing error:", error));

  return response;
};
```

**2. Increase Timeout:**
```toml
[[functions."webhook"]]
  timeout = 26
```

**3. Optimize Database Operations:**
```typescript
// ❌ Slow - multiple queries
const user = await db.from("users").select("*").eq("phone", phone).single();
const messages = await db.from("messages").select("*").eq("user_id", user.id);
const session = await db.from("sessions").select("*").eq("user_id", user.id).single();

// ✅ Fast - single query
const { data } = await db
  .from("users")
  .select(`
    *,
    messages(*),
    sessions(*)
  `)
  .eq("phone", phone)
  .single();
```

### Webhook Signature Validation Failures

**Symptom:** Webhook returns 401 Unauthorized

**Debug Steps:**

1. **Log signature details:**
```typescript
console.log("Signature validation:", {
  signature: event.headers["telnyx-signature-ed25519"],
  timestamp: event.headers["telnyx-timestamp"],
  body: event.body,
  publicKey: process.env.TELNYX_PUBLIC_KEY,
});
```

2. **Verify public key format:**
```bash
# Should include newlines
TELNYX_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nMIIBIj...\n-----END PUBLIC KEY-----"
```

3. **Check timestamp freshness:**
```typescript
const timestamp = event.headers["telnyx-timestamp"];
const now = Math.floor(Date.now() / 1000);

if (Math.abs(now - parseInt(timestamp)) > 300) {
  // Timestamp too old (>5 minutes)
  return { statusCode: 401, body: "Timestamp expired" };
}
```

## Environment Variable Issues

### Variable Not Available

**Symptom:** `process.env.VARIABLE_NAME` returns `undefined`

**Debug Steps:**

1. **List all variables:**
```bash
netlify env:list
```

2. **Check variable scope:**
   - Verify variable includes your deployment context
   - Production deploy needs "Production" scope checked

3. **Verify spelling:**
```typescript
// ❌ Wrong casing
process.env.telnyx_api_key

// ✅ Correct
process.env.TELNYX_API_KEY
```

4. **Check if recently added:**
   - New variables require redeploy
   - Trigger new deployment: `netlify deploy --prod`

5. **Log available variables (debugging only):**
```typescript
console.log("Available env vars:", Object.keys(process.env));
```

## Deployment Issues

### Deploy Stuck in "Building"

**Solutions:**

1. **Check build logs:**
```bash
netlify logs:build
```

2. **Cancel and retry:**
   - In Dashboard: Cancel deploy → Retry deploy

3. **Check for infinite loops in build:**
```json
// package.json
{
  "scripts": {
    "build": "next build"  // ✅ Correct
    // ❌ "build": "npm run build"  // Infinite loop
  }
}
```

### Deploy Succeeds But Site Shows Error

**Debug Steps:**

1. **Check function logs:**
```bash
netlify logs:functions
```

2. **Verify publish directory:**
```toml
[build]
  publish = ".next"  # For Next.js
```

3. **Check redirects:**
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

## Database Connection Issues

### Supabase Connection Failures

**Symptom:** Database queries fail or timeout

**Debug Steps:**

1. **Verify credentials:**
```bash
# Test connection
curl https://YOUR_SUPABASE_URL/rest/v1/ \
  -H "apikey: YOUR_SERVICE_KEY"
```

2. **Check RLS policies:**
```sql
-- Verify service role bypasses RLS
SELECT * FROM messages;  -- Should work with service key
```

3. **Connection pooling:**
```typescript
// Reuse client across invocations
let supabase: any = null;

function getSupabase() {
  if (!supabase) {
    supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  }
  return supabase;
}
```

## Monitoring and Debugging Tools

### Real-Time Function Logs

```bash
# Follow logs for specific function
netlify functions:log webhook --stream

# View last 100 lines
netlify functions:log webhook --lines 100
```

### Structured Logging

```typescript
function log(level: "info" | "warn" | "error", message: string, context?: any) {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    message,
    context,
    requestId: context?.requestId,
  }));
}

export const handler: Handler = async (event, context) => {
  log("info", "Function started", { requestId: context.requestId });

  try {
    // Process
    log("info", "Processing complete", { requestId: context.requestId });
  } catch (error) {
    log("error", "Processing failed", {
      requestId: context.requestId,
      error: error instanceof Error ? error.message : "Unknown",
      stack: error instanceof Error ? error.stack : undefined,
    });
    throw error;
  }
};
```

### Performance Monitoring

```typescript
async function measureDuration<T>(label: string, fn: () => Promise<T>): Promise<T> {
  const start = Date.now();
  try {
    return await fn();
  } finally {
    console.log(JSON.stringify({
      metric: "duration",
      label,
      duration_ms: Date.now() - start,
    }));
  }
}

export const handler: Handler = async (event, context) => {
  return measureDuration("handler", async () => {
    const dbResult = await measureDuration("db_query", () => queryDatabase());
    const apiResult = await measureDuration("api_call", () => callAPI());

    return { statusCode: 200, body: JSON.stringify({ dbResult, apiResult }) };
  });
};
```

## Common Error Messages

### "Function bundling failed"

**Cause:** TypeScript errors or missing dependencies

**Solution:**
```bash
npm run build  # Test locally
npx tsc --noEmit  # Check TypeScript
```

### "Missing environment variable"

**Solution:**
```bash
netlify env:set VARIABLE_NAME value
netlify deploy --prod  # Redeploy
```

### "Cannot find module"

**Cause:** Dependency not in package.json

**Solution:**
```bash
npm install missing-package
git add package.json package-lock.json
git commit -m "Add missing dependency"
git push
```

### "CORS error"

**Solution:**
```toml
[[headers]]
  for = "/api/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Methods = "GET, POST, OPTIONS"
    Access-Control-Allow-Headers = "Content-Type"
```

## Emergency Debugging Checklist

When everything is broken:

- [ ] Check build logs: `netlify logs:build`
- [ ] Check function logs: `netlify logs:functions`
- [ ] Verify environment variables: `netlify env:list`
- [ ] Check recent commits: `git log -5`
- [ ] Rollback to last working deploy (Netlify Dashboard)
- [ ] Test locally: `netlify dev`
- [ ] Check Netlify status: https://www.netlifystatus.com/

## Resources

- [Netlify Debug Guide](https://docs.netlify.com/configure-builds/troubleshooting-tips/)
- [Function Logs](https://docs.netlify.com/functions/logs/)
- [Build Troubleshooting](https://docs.netlify.com/configure-builds/troubleshooting-tips/)
