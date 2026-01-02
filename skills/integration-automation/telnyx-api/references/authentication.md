# Telnyx Authentication & Security

## API Keys

Telnyx uses API keys (Bearer tokens) for authentication. All API requests must include an `Authorization` header with your API key.

### API Key Types

1. **API Keys (v2)** - Full access to all Telnyx APIs
   - Format: `KEY019A...` (starts with "KEY")
   - Use for server-side applications
   - Never expose in client-side code

2. **Public Keys** - Used for webhook signature verification
   - Used to verify webhook authenticity
   - Can be shared in client-side code for verification

### Creating API Keys

1. Log in to [Mission Control Portal](https://portal.telnyx.com/)
2. Navigate to **Auth** → **API Keys**
3. Click **Create API Key**
4. Name your key (e.g., "Production App")
5. Set permissions (full or read-only)
6. Copy and securely store the key (shown only once)

### API Key Best Practices

✅ **DO:**
- Store API keys in environment variables
- Use different keys for dev/staging/production
- Rotate keys regularly (every 90 days)
- Use read-only keys where possible
- Monitor key usage in Mission Control

❌ **DON'T:**
- Hardcode keys in source code
- Commit keys to version control
- Share keys via email or chat
- Use production keys in development
- Expose keys in client-side JavaScript

## Using API Keys

### HTTP Header Format
```
Authorization: Bearer YOUR_API_KEY
```

### cURL Example
```bash
curl -X POST https://api.telnyx.com/v2/messages \
  -H "Authorization: Bearer KEY019A080F468AAFD4AF4F6888D7795244_xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+18445550001",
    "to": "+18665550001",
    "text": "Hello!"
  }'
```

### Node.js Example
```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'https://api.telnyx.com/v2',
  headers: {
    'Authorization': `Bearer ${process.env.TELNYX_API_KEY}`,
    'Content-Type': 'application/json'
  }
});

// Use the client
await client.post('/messages', {
  from: '+18445550001',
  to: '+18665550001',
  text: 'Hello!'
});
```

### Python Example
```python
import os
import requests

headers = {
    'Authorization': f"Bearer {os.environ['TELNYX_API_KEY']}",
    'Content-Type': 'application/json'
}

response = requests.post(
    'https://api.telnyx.com/v2/messages',
    headers=headers,
    json={
        'from': '+18445550001',
        'to': '+18665550001',
        'text': 'Hello!'
    }
)
```

## Environment Variables

### Setting Up Environment Variables

#### .env File (Node.js)
```bash
# .env
TELNYX_API_KEY=KEY019A080F468AAFD4AF4F6888D7795244_xxx
TELNYX_PUBLIC_KEY=your_public_key_here
TELNYX_MESSAGING_PROFILE_ID=abc85f64-5717-4562-b3fc-2c9600000000
```

Load with `dotenv`:
```javascript
require('dotenv').config();
const apiKey = process.env.TELNYX_API_KEY;
```

#### System Environment Variables

**macOS/Linux:**
```bash
export TELNYX_API_KEY="KEY019A..."
export TELNYX_PUBLIC_KEY="your_public_key"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export TELNYX_API_KEY="KEY019A..."' >> ~/.zshrc
```

**Windows (Command Prompt):**
```cmd
set TELNYX_API_KEY=KEY019A...
```

**Windows (PowerShell):**
```powershell
$env:TELNYX_API_KEY = "KEY019A..."
```

#### Docker
```dockerfile
# Dockerfile
ENV TELNYX_API_KEY=${TELNYX_API_KEY}
```

```bash
# docker-compose.yml
services:
  app:
    environment:
      - TELNYX_API_KEY=${TELNYX_API_KEY}
```

#### Kubernetes
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: telnyx-secrets
type: Opaque
stringData:
  api-key: KEY019A...
```

```yaml
# deployment.yaml
env:
  - name: TELNYX_API_KEY
    valueFrom:
      secretKeyRef:
        name: telnyx-secrets
        key: api-key
```

## Error Responses

### 401 Unauthorized
Invalid or missing API key.

```json
{
  "errors": [{
    "code": "40100",
    "title": "Unauthorized",
    "detail": "Authentication failed. Please check your API key."
  }]
}
```

**Solutions:**
- Verify API key is correct
- Check `Authorization` header format
- Ensure key hasn't been revoked

### 403 Forbidden
Valid key but insufficient permissions.

```json
{
  "errors": [{
    "code": "40300",
    "title": "Forbidden",
    "detail": "You do not have permission to access this resource."
  }]
}
```

**Solutions:**
- Check API key permissions in Mission Control
- Upgrade to full-access key if needed

## Security Best Practices

### 1. Environment-Specific Keys

```javascript
// config.js
const config = {
  development: {
    apiKey: process.env.TELNYX_DEV_API_KEY,
    webhookUrl: 'https://dev.example.com/webhooks'
  },
  production: {
    apiKey: process.env.TELNYX_PROD_API_KEY,
    webhookUrl: 'https://api.example.com/webhooks'
  }
};

const env = process.env.NODE_ENV || 'development';
module.exports = config[env];
```

### 2. Key Rotation

```javascript
// Support multiple valid keys during rotation
const validKeys = [
  process.env.TELNYX_API_KEY_CURRENT,
  process.env.TELNYX_API_KEY_OLD  // Keep old key valid for 24h during rotation
];

function authenticateRequest(req) {
  const providedKey = req.headers['authorization']?.replace('Bearer ', '');
  return validKeys.includes(providedKey);
}
```

### 3. Rate Limiting Protection

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', limiter);
```

### 4. IP Whitelisting

Configure in Mission Control Portal:
1. Go to **Auth** → **API Keys**
2. Select your API key
3. Add allowed IP addresses
4. Save changes

### 5. Request Logging (Without Exposing Keys)

```javascript
// Safe logging - masks sensitive data
function logRequest(req) {
  console.log({
    method: req.method,
    url: req.url,
    // Mask API key
    authorization: req.headers['authorization']?.replace(/KEY\w+/, 'KEY***'),
    body: req.body
  });
}
```

## Webhook Security

### Public Key for Verification

Retrieve your public key from Mission Control Portal:
1. Go to **Auth** → **API Keys**
2. Find your public key (different from API key)
3. Use for webhook signature verification

### Verifying Webhook Signatures

See `webhooks.md` for detailed signature verification examples.

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(body, signature, timestamp, publicKey) {
  const payload = `${timestamp}.${JSON.stringify(body)}`;
  const hmac = crypto.createHmac('sha256', publicKey);
  const digest = hmac.update(payload).digest('hex');
  return signature === digest;
}
```

## Testing Authentication

### Test API Key
```bash
# Test if API key is valid
curl -X GET https://api.telnyx.com/v2/available_phone_numbers \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -G \
  -d 'filter[phone_number][contains]=555'

# Success: Returns available numbers
# Failure: Returns 401 Unauthorized
```

### Test in Node.js
```javascript
async function testApiKey(apiKey) {
  try {
    const response = await axios.get(
      'https://api.telnyx.com/v2/available_phone_numbers',
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`
        },
        params: {
          'filter[phone_number][contains]': '555'
        }
      }
    );

    console.log('✅ API key is valid');
    return true;
  } catch (error) {
    if (error.response?.status === 401) {
      console.error('❌ API key is invalid');
    } else {
      console.error('Error testing API key:', error.message);
    }
    return false;
  }
}
```

## Common Mistakes

### 1. Exposed API Keys
❌ **Wrong:**
```javascript
// Hardcoded key
const apiKey = 'KEY019A080F468AAFD4AF4F6888D7795244_xxx';
```

✅ **Correct:**
```javascript
// Environment variable
const apiKey = process.env.TELNYX_API_KEY;
```

### 2. Missing Authorization Header
❌ **Wrong:**
```bash
curl -X POST https://api.telnyx.com/v2/messages \
  -d '{"from":"+1...", "to":"+1...", "text":"Hi"}'
```

✅ **Correct:**
```bash
curl -X POST https://api.telnyx.com/v2/messages \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"from":"+1...", "to":"+1...", "text":"Hi"}'
```

### 3. Using Production Keys in Development
❌ **Wrong:**
```javascript
// .env.development
TELNYX_API_KEY=KEY_PRODUCTION_KEY_HERE
```

✅ **Correct:**
```javascript
// .env.development
TELNYX_API_KEY=KEY_DEVELOPMENT_KEY_HERE

// .env.production
TELNYX_API_KEY=KEY_PRODUCTION_KEY_HERE
```

## Compliance & Regulations

### GDPR Compliance
- Store API keys securely encrypted
- Log access to sensitive data
- Implement data retention policies
- Allow users to request data deletion

### SOC 2 Compliance
- Rotate keys every 90 days
- Monitor API key usage
- Implement least-privilege access
- Maintain audit logs

### HIPAA Compliance (if applicable)
- Use encrypted storage for keys
- Implement access controls
- Maintain audit trails
- Use TLS 1.2+ for all API calls

## Troubleshooting

### API Key Not Working

1. **Check Format**: Must start with "KEY"
2. **Check Permissions**: Ensure key has required permissions
3. **Check Status**: Verify key isn't revoked in Mission Control
4. **Check Environment**: Ensure using correct environment variable

### Header Format Issues

```javascript
// ✅ Correct formats
'Authorization': 'Bearer KEY019A...'
'Authorization': `Bearer ${apiKey}`

// ❌ Wrong formats
'Authorization': 'KEY019A...'  // Missing "Bearer"
'Authorization': 'Basic KEY019A...'  // Wrong auth type
'Api-Key': 'KEY019A...'  // Wrong header name
```

## Additional Resources

- [Mission Control Portal](https://portal.telnyx.com/)
- [API Key Management](https://portal.telnyx.com/app/auth/api-keys)
- [Security Best Practices](https://developers.telnyx.com/docs/security)
- [Rate Limits](https://developers.telnyx.com/docs/api/rate-limits)
