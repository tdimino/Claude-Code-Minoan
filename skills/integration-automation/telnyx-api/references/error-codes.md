# Telnyx API Error Codes Reference

## Error Response Format

All Telnyx API errors follow this structure:

```json
{
  "errors": [{
    "code": "10001",
    "title": "Error Title",
    "detail": "Detailed error description",
    "source": {
      "pointer": "/data/attributes/to",
      "parameter": "to"
    },
    "meta": {}
  }]
}
```

## HTTP Status Codes

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Fix request parameters |
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Check resource ID/URL |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Implement rate limiting |
| 500 | Internal Server Error | Retry with backoff |
| 502 | Bad Gateway | Retry with backoff |
| 503 | Service Unavailable | Check status page |

## Common Error Codes

### Authentication Errors (401)

#### 40100 - Unauthorized
```json
{
  "errors": [{
    "code": "40100",
    "title": "Unauthorized",
    "detail": "Authentication failed. Please check your API key."
  }]
}
```

**Causes:**
- Missing Authorization header
- Invalid API key
- API key format error (missing "Bearer ")

**Solution:**
```javascript
// Correct format
headers: {
  'Authorization': `Bearer ${process.env.TELNYX_API_KEY}`
}
```

### Permission Errors (403)

#### 40300 - Forbidden
```json
{
  "errors": [{
    "code": "40300",
    "title": "Forbidden",
    "detail": "You do not have permission to access this resource."
  }]
}
```

**Causes:**
- Read-only API key used for write operation
- Insufficient permissions on API key

**Solution:**
- Use full-access API key
- Check key permissions in Mission Control

### Validation Errors (400, 422)

#### 10001 - Invalid Phone Number
```json
{
  "errors": [{
    "code": "10001",
    "title": "Invalid phone number",
    "detail": "The 'to' phone number must be in E.164 format",
    "source": {
      "pointer": "/data/attributes/to",
      "parameter": "to"
    }
  }]
}
```

**Causes:**
- Phone number not in E.164 format
- Missing + prefix
- Invalid country code

**Solution:**
```javascript
// ✅ Correct
to: '+14155552671'

// ❌ Wrong
to: '4155552671'   // Missing + and country code
to: '1-415-555-2671'  // Not E.164 format
```

#### 10002 - Invalid Messaging Profile
```json
{
  "errors": [{
    "code": "10002",
    "title": "Invalid messaging profile",
    "detail": "The messaging_profile_id does not exist or is disabled"
  }]
}
```

**Causes:**
- Non-existent messaging profile ID
- Disabled messaging profile
- Typo in profile ID

**Solution:**
```javascript
// Verify profile exists
const profiles = await axios.get(
  'https://api.telnyx.com/v2/messaging_profiles',
  { headers: { 'Authorization': `Bearer ${apiKey}` }}
);
console.log('Available profiles:', profiles.data.data);
```

#### 10003 - Insufficient Balance
```json
{
  "errors": [{
    "code": "10003",
    "title": "Insufficient balance",
    "detail": "Your account balance is too low to send this message"
  }]
}
```

**Causes:**
- Account balance below required amount

**Solution:**
- Add funds in Mission Control Portal
- Set up auto-recharge

#### 10004 - Invalid Destination
```json
{
  "errors": [{
    "code": "10004",
    "title": "Invalid destination",
    "detail": "The destination number is not reachable or invalid"
  }]
}
```

**Causes:**
- Landline number (SMS not supported)
- Invalid phone number
- Disconnected number

**Solution:**
- Verify number is a mobile number
- Check number is active
- Use number lookup API to validate

#### 10005 - Message Too Long
```json
{
  "errors": [{
    "code": "10005",
    "title": "Message too long",
    "detail": "Message exceeds maximum allowed length (10 segments)"
  }]
}
```

**Causes:**
- Message exceeds 10 SMS segments (1530 chars GSM-7 or 670 chars UCS-2)

**Solution:**
```javascript
function truncateMessage(text, maxSegments = 3) {
  const maxChars = maxSegments * 153; // GSM-7 multi-segment
  if (text.length > maxChars) {
    return text.substring(0, maxChars - 3) + '...';
  }
  return text;
}
```

#### 10006 - Missing Required Field
```json
{
  "errors": [{
    "code": "10006",
    "title": "Missing required field",
    "detail": "The 'text' field is required for SMS messages",
    "source": {
      "pointer": "/data/attributes/text"
    }
  }]
}
```

**Causes:**
- Missing required parameter (`text`, `to`, `from`, etc.)

**Solution:**
- Include all required fields
- Check API documentation for requirements

#### 10007 - Invalid Media URL
```json
{
  "errors": [{
    "code": "10007",
    "title": "Invalid media URL",
    "detail": "Media file exceeds maximum size of 1MB"
  }]
}
```

**Causes:**
- Media file too large (> 1MB)
- Invalid URL
- Unsupported file format

**Solution:**
```javascript
// Compress images before sending
// Supported formats: JPG, PNG, GIF, MP4, PDF
const media_urls = ['https://example.com/small-image.jpg'];
```

### Rate Limiting Errors (429)

#### 42900 - Rate Limit Exceeded
```json
{
  "errors": [{
    "code": "42900",
    "title": "Too many requests",
    "detail": "Rate limit exceeded. Please slow down your requests."
  }]
}
```

**Causes:**
- Sending too many requests too quickly
- Exceeding 10 requests/second limit

**Solution:**
```javascript
async function sendWithRateLimit(messages) {
  const delayMs = 100; // 10 messages/second

  for (const msg of messages) {
    await sendSMS(msg.to, msg.from, msg.text);
    await new Promise(resolve => setTimeout(resolve, delayMs));
  }
}
```

### Server Errors (500, 502, 503)

#### 50000 - Internal Server Error
```json
{
  "errors": [{
    "code": "50000",
    "title": "Internal server error",
    "detail": "An unexpected error occurred. Please try again."
  }]
}
```

**Causes:**
- Temporary server issue
- Service degradation

**Solution:**
```javascript
// Implement retry with exponential backoff
async function sendWithRetry(to, from, text, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await sendSMS(to, from, text);
    } catch (error) {
      if (error.response?.status === 500 && attempt < maxRetries) {
        const delayMs = Math.pow(2, attempt) * 1000;
        console.log(`Server error, retrying in ${delayMs}ms...`);
        await new Promise(resolve => setTimeout(resolve, delayMs));
      } else {
        throw error;
      }
    }
  }
}
```

#### 50200 - Bad Gateway
Temporary network issue. Retry the request.

#### 50300 - Service Unavailable
Service temporarily unavailable. Check [status page](https://status.telnyx.com/).

## Webhook-Specific Errors

### Message Delivery Errors

Errors reported in webhook `message.failed` events:

#### carrier_rejected
```json
{
  "errors": [{
    "code": "carrier_rejected",
    "title": "Carrier rejected message",
    "detail": "The carrier rejected the message"
  }]
}
```

**Causes:**
- Carrier-level block
- Spam filter
- Invalid destination

#### expired
```json
{
  "errors": [{
    "code": "expired",
    "title": "Message expired",
    "detail": "Message expired before delivery"
  }]
}
```

**Causes:**
- Recipient phone off for extended period
- Message exceeded validity period

#### invalid_destination
```json
{
  "errors": [{
    "code": "invalid_destination",
    "title": "Invalid destination",
    "detail": "Destination number is invalid or unreachable"
  }]
}
```

#### spam_detected
```json
{
  "errors": [{
    "code": "spam_detected",
    "title": "Spam detected",
    "detail": "Message flagged as spam"
  }]
}
```

**Solutions:**
- Review message content
- Ensure compliance with carrier guidelines
- Register for 10DLC (US)
- Use verified sender ID

## Error Handling Patterns

### Comprehensive Error Handler

```javascript
function handleTelnyxError(error) {
  if (!error.response) {
    // Network error
    return {
      type: 'NETWORK_ERROR',
      message: 'Network request failed',
      retriable: true
    };
  }

  const status = error.response.status;
  const errorData = error.response.data.errors?.[0];
  const errorCode = errorData?.code;

  switch (status) {
    case 400:
    case 422:
      // Validation error - fix input
      return {
        type: 'VALIDATION_ERROR',
        code: errorCode,
        message: errorData?.detail || 'Invalid request',
        retriable: false
      };

    case 401:
      // Authentication error
      return {
        type: 'AUTH_ERROR',
        message: 'Invalid API key',
        retriable: false
      };

    case 403:
      // Permission error
      return {
        type: 'PERMISSION_ERROR',
        message: 'Insufficient permissions',
        retriable: false
      };

    case 404:
      // Not found
      return {
        type: 'NOT_FOUND',
        message: 'Resource not found',
        retriable: false
      };

    case 429:
      // Rate limit
      return {
        type: 'RATE_LIMIT',
        message: 'Rate limit exceeded',
        retriable: true,
        retryAfter: error.response.headers['retry-after'] || 60
      };

    case 500:
    case 502:
    case 503:
      // Server error
      return {
        type: 'SERVER_ERROR',
        message: 'Temporary server error',
        retriable: true
      };

    default:
      return {
        type: 'UNKNOWN_ERROR',
        status: status,
        message: errorData?.detail || 'Unknown error',
        retriable: false
      };
  }
}

// Usage
try {
  await sendSMS(to, from, text);
} catch (error) {
  const errorInfo = handleTelnyxError(error);

  if (errorInfo.retriable) {
    // Queue for retry
    await retryQueue.add({ to, from, text });
  } else {
    // Log and notify
    logger.error('Non-retriable error:', errorInfo);
    await notifyAdmin(errorInfo);
  }
}
```

### Retry with Specific Error Handling

```javascript
async function smartRetry(fn, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      const errorInfo = handleTelnyxError(error);

      // Don't retry non-retriable errors
      if (!errorInfo.retriable || attempt === maxRetries) {
        throw error;
      }

      // Calculate delay
      let delayMs;
      if (errorInfo.type === 'RATE_LIMIT') {
        delayMs = (errorInfo.retryAfter || 60) * 1000;
      } else {
        delayMs = Math.pow(2, attempt) * 1000; // Exponential backoff
      }

      console.log(`Attempt ${attempt} failed, retrying in ${delayMs}ms...`);
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }
}

// Usage
await smartRetry(() => sendSMS(to, from, text));
```

## Debugging Tips

### 1. Enable Request Logging

```javascript
axios.interceptors.request.use(request => {
  console.log('Starting Request:', {
    url: request.url,
    method: request.method,
    // Mask API key
    headers: {
      ...request.headers,
      Authorization: request.headers.Authorization?.replace(/KEY\w+/, 'KEY***')
    },
    data: request.data
  });
  return request;
});

axios.interceptors.response.use(
  response => {
    console.log('Response:', response.status, response.data);
    return response;
  },
  error => {
    console.error('Error Response:', {
      status: error.response?.status,
      data: error.response?.data
    });
    return Promise.reject(error);
  }
);
```

### 2. Test with curl

```bash
# Test authentication
curl -X GET "https://api.telnyx.com/v2/available_phone_numbers?filter[phone_number][contains]=555" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -v

# Test sending message
curl -X POST https://api.telnyx.com/v2/messages \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+14155552671",
    "to": "+14155559999",
    "text": "Test message"
  }' \
  -v
```

### 3. Check Telnyx Status

Always check https://status.telnyx.com/ when experiencing widespread issues.

## Getting Help

If you encounter persistent errors:

1. **Check documentation**: https://developers.telnyx.com/
2. **Search support articles**: https://support.telnyx.com/
3. **Check status page**: https://status.telnyx.com/
4. **Contact support**: Through Mission Control Portal
5. **Community Slack**: Available via developer portal

Include in your support request:
- Error code and message
- Request/response payloads (redact sensitive data)
- Timestamp of error
- Your organization ID (from Mission Control)
