# Telnyx API Best Practices

## Production Deployment

### 1. Use Messaging Profiles

Messaging profiles provide centralized configuration and better management for production applications.

**Benefits:**
- Centralized webhook configuration
- Number pooling for high-volume sending
- Easy number management
- Alphanumeric sender ID support

```javascript
// Create messaging profile
async function setupMessagingProfile() {
  const profile = await axios.post(
    'https://api.telnyx.com/v2/messaging_profiles',
    {
      name: 'Production Profile',
      enabled: true,
      webhook_url: 'https://api.example.com/webhooks/telnyx',
      webhook_failover_url: 'https://backup.example.com/webhooks/telnyx',
      webhook_api_version: '2'
    },
    {
      headers: {
        'Authorization': `Bearer ${process.env.TELNYX_API_KEY}`,
        'Content-Type': 'application/json'
      }
    }
  );

  console.log('Profile ID:', profile.data.data.id);
  return profile.data.data.id;
}
```

### 2. Implement Robust Error Handling

```javascript
async function sendMessageWithErrorHandling(to, from, text) {
  try {
    const response = await sendSMS(to, from, text);
    return { success: true, data: response.data };

  } catch (error) {
    // Handle specific error types
    if (error.response) {
      const statusCode = error.response.status;
      const errorData = error.response.data.errors[0];

      switch (statusCode) {
        case 400:
          // Bad request - fix input
          console.error('Invalid request:', errorData.detail);
          return { success: false, error: 'INVALID_INPUT', message: errorData.detail };

        case 401:
          // Authentication failed
          console.error('Authentication failed');
          return { success: false, error: 'AUTH_FAILED', message: 'Check API key' };

        case 403:
          // Forbidden
          console.error('Permission denied');
          return { success: false, error: 'FORBIDDEN', message: 'Insufficient permissions' };

        case 429:
          // Rate limit exceeded
          console.error('Rate limit exceeded, retrying after delay');
          await sleep(2000);
          return sendMessageWithErrorHandling(to, from, text); // Retry

        case 500:
        case 502:
        case 503:
          // Server error - retry with backoff
          console.error('Server error, will retry');
          return { success: false, error: 'SERVER_ERROR', retriable: true };

        default:
          console.error('Unknown error:', statusCode);
          return { success: false, error: 'UNKNOWN', statusCode };
      }
    } else if (error.request) {
      // Network error
      console.error('Network error:', error.message);
      return { success: false, error: 'NETWORK_ERROR', retriable: true };

    } else {
      // Unknown error
      console.error('Unexpected error:', error.message);
      return { success: false, error: 'UNEXPECTED', message: error.message };
    }
  }
}
```

### 3. Implement Exponential Backoff Retry

```javascript
async function sendWithRetry(to, from, text, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const result = await sendMessageWithErrorHandling(to, from, text);

    if (result.success) {
      return result;
    }

    // Only retry if error is retriable
    if (!result.retriable || attempt === maxRetries) {
      return result;
    }

    // Exponential backoff: 2^attempt seconds
    const delayMs = Math.pow(2, attempt) * 1000;
    console.log(`Attempt ${attempt} failed, retrying in ${delayMs}ms...`);
    await sleep(delayMs);
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### 4. Rate Limiting for Bulk Sending

```javascript
class MessageQueue {
  constructor(rateLimit = 10) {
    this.queue = [];
    this.rateLimit = rateLimit; // messages per second
    this.isProcessing = false;
  }

  async add(to, from, text) {
    return new Promise((resolve, reject) => {
      this.queue.push({ to, from, text, resolve, reject });
      if (!this.isProcessing) {
        this.process();
      }
    });
  }

  async process() {
    this.isProcessing = true;

    while (this.queue.length > 0) {
      const item = this.queue.shift();

      try {
        const result = await sendSMS(item.to, item.from, item.text);
        item.resolve(result);
      } catch (error) {
        item.reject(error);
      }

      // Rate limiting delay
      const delayMs = 1000 / this.rateLimit;
      await sleep(delayMs);
    }

    this.isProcessing = false;
  }
}

// Usage
const messageQueue = new MessageQueue(10); // 10 messages/second

// Send many messages
const recipients = ['+1555...', '+1556...', '+1557...'];
const promises = recipients.map(to =>
  messageQueue.add(to, '+14155559999', 'Hello!')
);

const results = await Promise.all(promises);
```

### 5. Track Message Status

```javascript
class MessageTracker {
  constructor() {
    this.messages = new Map();
  }

  track(messageId, metadata) {
    this.messages.set(messageId, {
      id: messageId,
      status: 'queued',
      createdAt: new Date(),
      ...metadata
    });
  }

  updateStatus(messageId, status, details = {}) {
    const message = this.messages.get(messageId);
    if (message) {
      message.status = status;
      message.updatedAt = new Date();
      Object.assign(message, details);
    }
  }

  getStatus(messageId) {
    return this.messages.get(messageId);
  }

  // Clean up old messages (run periodically)
  cleanup(olderThanHours = 24) {
    const cutoff = Date.now() - (olderThanHours * 60 * 60 * 1000);
    for (const [id, msg] of this.messages) {
      if (msg.createdAt.getTime() < cutoff) {
        this.messages.delete(id);
      }
    }
  }
}

const tracker = new MessageTracker();

// When sending
const response = await sendSMS(to, from, text);
tracker.track(response.data.data.id, { to, from, text });

// In webhook handler
app.post('/webhooks/telnyx', (req, res) => {
  const event = req.body.data;

  if (event.event_type === 'message.delivered') {
    tracker.updateStatus(event.payload.id, 'delivered');
  } else if (event.event_type === 'message.failed') {
    tracker.updateStatus(event.payload.id, 'failed', {
      errors: event.payload.errors
    });
  }

  res.status(200).send('OK');
});
```

## Phone Number Best Practices

### 1. Validate Phone Numbers

```javascript
function validateE164(phoneNumber) {
  // E.164 format: +[country code][number]
  // Max 15 digits (excluding +)
  const e164Regex = /^\+[1-9]\d{1,14}$/;

  if (!e164Regex.test(phoneNumber)) {
    return {
      valid: false,
      error: 'Phone number must be in E.164 format (e.g., +14155552671)'
    };
  }

  return { valid: true };
}

// Usage
const validation = validateE164(userInput);
if (!validation.valid) {
  throw new Error(validation.error);
}
```

### 2. Phone Number Formatting

```javascript
function formatToE164(number, defaultCountryCode = '1') {
  // Remove all non-digit characters
  let digits = number.replace(/\D/g, '');

  // Add country code if missing
  if (!digits.startsWith(defaultCountryCode)) {
    digits = defaultCountryCode + digits;
  }

  return '+' + digits;
}

// Examples
formatToE164('415-555-2671');           // +14155552671
formatToE164('(415) 555-2671');         // +14155552671
formatToE164('+1 415-555-2671');        // +14155552671
formatToE164('4155552671');             // +14155552671
```

### 3. International Number Handling

```javascript
// Country code mapping
const countryCodes = {
  'US': '1',
  'UK': '44',
  'CA': '1',
  'AU': '61',
  'FR': '33',
  'DE': '49'
};

function formatInternational(number, countryCode) {
  const prefix = countryCodes[countryCode];
  if (!prefix) {
    throw new Error(`Unknown country code: ${countryCode}`);
  }

  const digits = number.replace(/\D/g, '');
  return `+${prefix}${digits}`;
}
```

## Message Content Best Practices

### 1. Character Limit Handling

```javascript
function optimizeMessage(text, maxSegments = 3) {
  const GSM7_CHARS = 160;
  const GSM7_MULTI = 153;
  const UCS2_CHARS = 70;
  const UCS2_MULTI = 67;

  // Detect if message needs UCS-2 encoding
  const needsUCS2 = /[^\x00-\x7F]/.test(text);
  const singleSegmentLimit = needsUCS2 ? UCS2_CHARS : GSM7_CHARS;
  const multiSegmentLimit = needsUCS2 ? UCS2_MULTI : GSM7_MULTI;

  // Calculate segments needed
  let segments;
  if (text.length <= singleSegmentLimit) {
    segments = 1;
  } else {
    segments = Math.ceil(text.length / multiSegmentLimit);
  }

  if (segments > maxSegments) {
    // Truncate and add ellipsis
    const maxChars = multiSegmentLimit * maxSegments - 3; // Reserve 3 chars for "..."
    return {
      text: text.substring(0, maxChars) + '...',
      segments: maxSegments,
      truncated: true
    };
  }

  return {
    text: text,
    segments: segments,
    truncated: false,
    encoding: needsUCS2 ? 'UCS-2' : 'GSM-7'
  };
}

// Usage
const optimized = optimizeMessage(longText, 3);
if (optimized.truncated) {
  console.warn('Message was truncated to fit 3 segments');
}
```

### 2. URL Shortening

```javascript
// For long URLs in SMS
async function shortenURL(longUrl) {
  // Use a URL shortening service
  // Example with bit.ly API (requires API key)
  const response = await axios.post(
    'https://api-ssl.bitly.com/v4/shorten',
    { long_url: longUrl },
    {
      headers: {
        'Authorization': `Bearer ${process.env.BITLY_API_KEY}`,
        'Content-Type': 'application/json'
      }
    }
  );

  return response.data.link;
}

// Usage
const message = `Check out this link: ${await shortenURL('https://example.com/very/long/url')}`;
```

### 3. Template Management

```javascript
const messageTemplates = {
  welcome: (name) => `Welcome ${name}! Reply HELP for assistance or STOP to unsubscribe.`,

  verification: (code) => `Your verification code is: ${code}. Valid for 10 minutes.`,

  reminder: (event, time) => `Reminder: ${event} at ${time}. Reply YES to confirm.`,

  order_confirmation: (orderNum, total) =>
    `Order #${orderNum} confirmed! Total: $${total}. Track at example.com/track`
};

// Usage
const message = messageTemplates.verification('123456');
```

## Webhook Best Practices

### 1. Async Processing

```javascript
const Queue = require('bull');
const webhookQueue = new Queue('webhooks', process.env.REDIS_URL);

app.post('/webhooks/telnyx', (req, res) => {
  // Respond immediately
  res.status(200).send('OK');

  // Queue for async processing
  webhookQueue.add(req.body);
});

// Process webhooks asynchronously
webhookQueue.process(async (job) => {
  const event = job.data.data;

  try {
    await processEvent(event);
  } catch (error) {
    console.error('Error processing webhook:', error);
    throw error; // Will trigger retry
  }
});
```

### 2. Idempotency with Database

```javascript
// Using PostgreSQL
async function processWebhookIdempotent(event) {
  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    // Check if already processed
    const existing = await client.query(
      'SELECT id FROM processed_webhooks WHERE event_id = $1',
      [event.id]
    );

    if (existing.rows.length > 0) {
      console.log('Event already processed, skipping');
      await client.query('COMMIT');
      return;
    }

    // Process event
    await handleEvent(event, client);

    // Mark as processed
    await client.query(
      'INSERT INTO processed_webhooks (event_id, processed_at) VALUES ($1, NOW())',
      [event.id]
    );

    await client.query('COMMIT');
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}
```

## Monitoring & Logging

### 1. Structured Logging

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Log message sent
logger.info('Message sent', {
  messageId: response.data.data.id,
  to: to,
  from: from,
  segments: response.data.data.parts,
  cost: response.data.data.cost.amount
});

// Log message delivered
logger.info('Message delivered', {
  messageId: event.payload.id,
  deliveryTime: event.payload.completed_at
});

// Log error
logger.error('Message failed', {
  messageId: event.payload.id,
  errors: event.payload.errors
});
```

### 2. Metrics & Alerts

```javascript
const prometheus = require('prom-client');

// Define metrics
const messagesSent = new prometheus.Counter({
  name: 'messages_sent_total',
  help: 'Total messages sent',
  labelNames: ['status']
});

const messageCost = new prometheus.Summary({
  name: 'message_cost_usd',
  help: 'Message cost in USD'
});

// Track metrics
messagesSent.inc({ status: 'success' });
messageCost.observe(parseFloat(cost.amount));

// Expose metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', prometheus.register.contentType);
  res.end(await prometheus.register.metrics());
});
```

## Cost Optimization

### 1. Message Segment Optimization

```javascript
// Prefer GSM-7 encoding (cheaper, longer)
function optimizeForGSM7(text) {
  // Replace unicode quotes with GSM-7 quotes
  return text
    .replace(/[""]/g, '"')
    .replace(/['']/g, "'")
    .replace(/[—–]/g, '-')
    .replace(/…/g, '...');
}
```

### 2. Batch Similar Messages

```javascript
// Instead of sending individually
for (const user of users) {
  await sendSMS(user.phone, from, `Hi ${user.name}, ...`);
}

// Batch by message template
const messagesByTemplate = groupByTemplate(users);
for (const [template, users] of Object.entries(messagesByTemplate)) {
  await sendBulk(users, from, template);
}
```

## Testing

### 1. Test Numbers

Telnyx provides test numbers that don't actually send messages:

```javascript
const TEST_NUMBERS = {
  success: '+15005550006',  // Always succeeds
  failure: '+15005550007',  // Always fails
  invalid: '+15005550001'   // Invalid number error
};

// In tests
if (process.env.NODE_ENV === 'test') {
  to = TEST_NUMBERS.success;
}
```

### 2. Webhook Testing

```javascript
// Mock webhook payload for testing
const mockWebhook = {
  data: {
    event_type: 'message.delivered',
    id: 'test-event-id',
    occurred_at: new Date().toISOString(),
    payload: {
      id: 'test-message-id',
      to: [{ phone_number: '+14155552671', status: 'delivered' }]
    }
  }
};

// Test webhook handler
await request(app)
  .post('/webhooks/telnyx')
  .send(mockWebhook)
  .expect(200);
```

## Production Checklist

- [ ] Use messaging profiles
- [ ] Implement error handling and retries
- [ ] Validate all phone numbers
- [ ] Set up webhook signature verification
- [ ] Implement rate limiting
- [ ] Add structured logging
- [ ] Set up monitoring and alerts
- [ ] Test with small batches first
- [ ] Implement opt-out handling (STOP keywords)
- [ ] Add cost tracking
- [ ] Set up failover webhook URL
- [ ] Document API key rotation process
- [ ] Test disaster recovery procedures
- [ ] Implement message archiving (compliance)
- [ ] Set up budget alerts in Mission Control

## Additional Resources

- [Telnyx Status Page](https://status.telnyx.com/)
- [API Rate Limits](https://developers.telnyx.com/docs/api/rate-limits)
- [Messaging Compliance](https://developers.telnyx.com/docs/messaging/compliance)
- [Production Readiness Checklist](https://developers.telnyx.com/docs/production-ready)
