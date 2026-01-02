# Telnyx Webhooks Reference

## Overview

Telnyx uses webhooks to notify your application about events in real-time. Webhooks are HTTP POST requests sent to your specified URL containing event data in JSON format.

## Webhook Configuration

### Setting Up Webhooks

Webhooks can be configured at multiple levels:

1. **Global Level** - Mission Control Portal → Messaging → Settings
2. **Messaging Profile Level** - When creating/editing a messaging profile
3. **Per-Message Level** - Using `webhook_url` parameter in send message request

### Configuration Parameters

```json
{
  "webhook_url": "https://your-domain.com/webhooks/telnyx",
  "webhook_failover_url": "https://backup-domain.com/webhooks/telnyx",
  "webhook_api_version": "2"
}
```

## Webhook Structure

All webhooks follow this structure:

```json
{
  "data": {
    "event_type": "message.sent",
    "id": "event-uuid",
    "occurred_at": "2025-10-24T18:10:02.574Z",
    "record_type": "event",
    "payload": {
      /* Event-specific data */
    }
  },
  "meta": {
    "attempt": 1,
    "delivered_to": "https://your-domain.com/webhooks/telnyx"
  }
}
```

## Message Events

### message.sent

Fired when message is sent to the carrier.

```json
{
  "data": {
    "event_type": "message.sent",
    "id": "event-uuid",
    "occurred_at": "2025-10-24T18:10:02.574Z",
    "payload": {
      "id": "message-uuid",
      "from": { "phone_number": "+18445550001" },
      "to": [{ "phone_number": "+18665550001", "status": "sent" }],
      "text": "Hello!",
      "type": "SMS"
    }
  }
}
```

### message.delivered

Fired when message is delivered to recipient (DLR received from carrier).

```json
{
  "data": {
    "event_type": "message.delivered",
    "payload": {
      "id": "message-uuid",
      "to": [{ "phone_number": "+18665550001", "status": "delivered" }],
      "completed_at": "2025-10-24T18:10:05.123Z"
    }
  }
}
```

### message.failed

Fired when message delivery fails.

```json
{
  "data": {
    "event_type": "message.failed",
    "payload": {
      "id": "message-uuid",
      "to": [{ "phone_number": "+18665550001", "status": "delivery_failed" }],
      "errors": [{
        "code": "10004",
        "title": "Invalid destination",
        "detail": "The destination number is not reachable"
      }]
    }
  }
}
```

### message.received

Fired when an inbound message is received.

```json
{
  "data": {
    "event_type": "message.received",
    "payload": {
      "id": "message-uuid",
      "direction": "inbound",
      "from": { "phone_number": "+18665550001" },
      "to": [{ "phone_number": "+18445550001" }],
      "text": "Hello back!",
      "type": "SMS",
      "received_at": "2025-10-24T18:15:00.000Z"
    }
  }
}
```

### message.finalized

Fired when message reaches a final state (delivered, failed, or unconfirmed).

```json
{
  "data": {
    "event_type": "message.finalized",
    "payload": {
      "id": "message-uuid",
      "to": [{ "status": "delivered" }],
      "completed_at": "2025-10-24T18:10:05.123Z"
    }
  }
}
```

## Call Control Events

### call.initiated

Fired when a call is initiated.

```json
{
  "data": {
    "event_type": "call.initiated",
    "payload": {
      "call_control_id": "call-uuid",
      "connection_id": "connection-uuid",
      "from": "+18445550001",
      "to": "+18665550001",
      "direction": "outgoing",
      "state": "parked"
    }
  }
}
```

### call.answered

Fired when a call is answered.

### call.hangup

Fired when a call ends.

## Webhook Security

### Signature Verification

Telnyx signs all webhooks with HMAC-SHA256. Always verify signatures in production.

#### Headers
```
telnyx-signature-ed25519: <signature>
telnyx-timestamp: <timestamp>
```

#### Verification (Node.js)
```javascript
const crypto = require('crypto');

function verifyWebhook(body, signature, timestamp, publicKey) {
  // Check timestamp freshness (prevent replay attacks)
  const timestampMs = parseInt(timestamp);
  const now = Date.now();
  if (Math.abs(now - timestampMs) > 5 * 60 * 1000) {
    return false; // Reject if older than 5 minutes
  }

  // Verify signature
  const payload = `${timestamp}.${JSON.stringify(body)}`;
  const hmac = crypto.createHmac('sha256', publicKey);
  const digest = hmac.update(payload).digest('hex');

  return signature === digest;
}

// Usage in Express
app.post('/webhooks/telnyx', (req, res) => {
  const signature = req.headers['telnyx-signature-ed25519'];
  const timestamp = req.headers['telnyx-timestamp'];

  if (!verifyWebhook(req.body, signature, timestamp, process.env.TELNYX_PUBLIC_KEY)) {
    return res.status(401).send('Invalid signature');
  }

  // Process webhook...
  res.status(200).send('OK');
});
```

#### Verification (Python)
```python
import hmac
import hashlib
import time

def verify_webhook(body, signature, timestamp, public_key):
    # Check timestamp freshness
    timestamp_ms = int(timestamp)
    if abs(time.time() * 1000 - timestamp_ms) > 5 * 60 * 1000:
        return False

    # Verify signature
    payload = f"{timestamp}.{body}"
    expected_signature = hmac.new(
        public_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)
```

## Webhook Best Practices

### 1. Respond Quickly
```javascript
app.post('/webhooks/telnyx', async (req, res) => {
  // Respond immediately
  res.status(200).send('OK');

  // Process asynchronously
  processWebhook(req.body).catch(console.error);
});
```

### 2. Implement Idempotency
```javascript
const processedEvents = new Set();

async function processWebhook(event) {
  const eventId = event.data.id;

  // Skip if already processed
  if (processedEvents.has(eventId)) {
    console.log('Duplicate event, skipping');
    return;
  }

  processedEvents.add(eventId);

  // Process event...
}
```

### 3. Handle Retries
Telnyx retries failed webhooks with exponential backoff:
- Attempt 1: Immediate
- Attempt 2: After 1 minute
- Attempt 3: After 5 minutes
- Attempt 4: After 15 minutes
- Attempt 5: After 1 hour

Return 2xx status code to acknowledge receipt.

### 4. Use Failover URLs
```json
{
  "webhook_url": "https://primary.example.com/webhooks",
  "webhook_failover_url": "https://backup.example.com/webhooks"
}
```

### 5. Log All Webhooks
```javascript
app.post('/webhooks/telnyx', (req, res) => {
  console.log('Webhook received:', {
    eventType: req.body.data.event_type,
    id: req.body.data.id,
    timestamp: req.body.data.occurred_at
  });

  // Store in database for debugging
  db.webhooks.insert(req.body);

  res.status(200).send('OK');
});
```

## Testing Webhooks Locally

### Using ngrok
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Start your server
node server.js  # Running on port 3000

# Expose to internet
ngrok http 3000

# Use ngrok URL in Telnyx dashboard
https://abc123.ngrok.io/webhooks/telnyx
```

### Using Webhook.site
1. Go to https://webhook.site/
2. Copy the unique URL
3. Use in Telnyx dashboard for testing
4. View all incoming webhooks in browser

## Webhook Event Types Reference

| Event Type | Description | When Fired |
|------------|-------------|------------|
| `message.sent` | Message sent to carrier | After sending to carrier |
| `message.delivered` | Message delivered to recipient | When DLR received |
| `message.failed` | Message delivery failed | When delivery fails |
| `message.received` | Inbound message received | When SMS/MMS received |
| `message.finalized` | Message reached final state | After delivered/failed |
| `call.initiated` | Call initiated | When call starts |
| `call.answered` | Call answered | When call answered |
| `call.hangup` | Call ended | When call ends |
| `call.recording.saved` | Recording saved | After recording completes |

## Troubleshooting

### Webhooks Not Receiving
1. Check webhook URL is publicly accessible
2. Verify TLS/SSL certificate is valid
3. Check firewall rules
4. Ensure server responds with 2xx status
5. Check webhook logs in Mission Control

### Duplicate Events
- Implement idempotency using `event.data.id`
- Store processed event IDs in database
- Use caching (Redis) for recent event IDs

### Webhook Order
Webhooks may arrive out of order. Use `occurred_at` timestamp for ordering if needed.

### Rate Limiting
No rate limiting on webhook delivery, but your server should handle bursts efficiently.

## Example: Complete Webhook Handler

```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

app.use(express.json());

// Store processed events (use Redis in production)
const processedEvents = new Set();

function verifySignature(body, signature, timestamp) {
  const payload = `${timestamp}.${JSON.stringify(body)}`;
  const hmac = crypto.createHmac('sha256', process.env.TELNYX_PUBLIC_KEY);
  const digest = hmac.update(payload).digest('hex');
  return signature === digest;
}

app.post('/webhooks/telnyx', async (req, res) => {
  // Verify signature
  const signature = req.headers['telnyx-signature-ed25519'];
  const timestamp = req.headers['telnyx-timestamp'];

  if (!verifySignature(req.body, signature, timestamp)) {
    return res.status(401).send('Invalid signature');
  }

  // Respond immediately
  res.status(200).send('OK');

  // Process asynchronously
  try {
    const event = req.body.data;

    // Check idempotency
    if (processedEvents.has(event.id)) {
      return;
    }
    processedEvents.add(event.id);

    // Route to handlers
    switch (event.event_type) {
      case 'message.received':
        await handleInboundMessage(event.payload);
        break;
      case 'message.delivered':
        await handleDelivered(event.payload);
        break;
      case 'message.failed':
        await handleFailed(event.payload);
        break;
    }
  } catch (error) {
    console.error('Error processing webhook:', error);
  }
});

async function handleInboundMessage(payload) {
  console.log('Received message from:', payload.from.phone_number);
  console.log('Text:', payload.text);

  // Your business logic here
}

async function handleDelivered(payload) {
  console.log('Message delivered:', payload.id);

  // Update database, notify user, etc.
}

async function handleFailed(payload) {
  console.log('Message failed:', payload.id, payload.errors);

  // Retry logic, notify admin, etc.
}

app.listen(3000, () => console.log('Webhook server running on port 3000'));
```
