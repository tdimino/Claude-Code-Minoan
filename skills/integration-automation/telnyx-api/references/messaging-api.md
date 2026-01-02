# Telnyx Messaging API Reference

## Overview

The Telnyx Messaging API allows you to send and receive SMS and MMS messages programmatically using phone numbers, short codes, or alphanumeric sender IDs.

**Base URL**: `https://api.telnyx.com/v2`

## Send a Message

### Endpoint
```
POST /v2/messages
```

### Headers
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### Request Body Parameters

#### Required Parameters

- `to` (string, required) - Receiving address in E.164 format (+18445550001)
- `from` (string, conditional) - Sending address. Required if sending with phone number or short code
- `messaging_profile_id` (string, conditional) - Required if sending via number pool or alphanumeric sender ID
- `text` (string, conditional) - Message body. Required for SMS

#### Optional Parameters

- `type` (string) - Protocol: `SMS` or `MMS` (default: auto-detect)
- `subject` (string) - Subject for multimedia messages
- `media_urls` (array) - List of media URLs. Required for MMS. Max total size: 1MB
- `webhook_url` (string) - URL for webhooks related to this message
- `webhook_failover_url` (string) - Failover URL if primary webhook fails
- `use_profile_webhooks` (boolean) - Use profile webhooks (default: true)
- `send_at` (string) - ISO 8601 datetime for scheduled sending
- `auto_detect` (boolean) - Auto-detect long messages

### Request Examples

#### Send SMS with Phone Number
```json
{
  "from": "+18445550001",
  "to": "+18665550001",
  "text": "Hello from Telnyx!"
}
```

#### Send MMS with Media
```json
{
  "from": "+18445550001",
  "to": "+18665550001",
  "text": "Check out this image!",
  "media_urls": ["https://example.com/image.jpg"],
  "type": "MMS"
}
```

#### Send with Messaging Profile
```json
{
  "messaging_profile_id": "abc85f64-5717-4562-b3fc-2c9600000000",
  "to": "+18665550001",
  "text": "Hello via messaging profile!"
}
```

#### Schedule Message
```json
{
  "from": "+18445550001",
  "to": "+18665550001",
  "text": "Scheduled message",
  "send_at": "2025-10-25T14:30:00Z"
}
```

### Response (200 OK)

```json
{
  "data": {
    "record_type": "message",
    "direction": "outbound",
    "id": "40385f64-5717-4562-b3fc-2c963f66afa6",
    "type": "SMS",
    "messaging_profile_id": "4000eba1-a0c0-4563-9925-b25e842a7cb6",
    "organization_id": "b448f9cc-a842-4784-98e9-03c1a5872950",
    "from": {
      "phone_number": "+18445550001",
      "carrier": "TELNYX LLC",
      "line_type": "VoIP"
    },
    "to": [{
      "phone_number": "+18665550001",
      "status": "queued",
      "carrier": "T-MOBILE USA, INC.",
      "line_type": "Wireless"
    }],
    "text": "Hello from Telnyx!",
    "encoding": "GSM-7",
    "parts": 1,
    "tags": [],
    "cost": {
      "amount": "0.0051",
      "currency": "USD"
    },
    "received_at": "2025-10-24T18:10:02.574Z",
    "sent_at": null,
    "completed_at": null,
    "valid_until": null,
    "errors": []
  }
}
```

### Response Fields

- `id` - Unique message identifier
- `direction` - `outbound` or `inbound`
- `type` - `SMS` or `MMS`
- `from.phone_number` - Sender phone number
- `to[].phone_number` - Recipient phone number
- `to[].status` - Delivery status (queued, sending, sent, delivered, failed)
- `text` - Message content
- `encoding` - Character encoding (GSM-7, UCS-2)
- `parts` - Number of message segments (1-10)
- `cost` - Cost breakdown
- `received_at` - When Telnyx received the request
- `sent_at` - When message was sent to carrier
- `completed_at` - When delivery completed

## Retrieve a Message

### Endpoint
```
GET /v2/messages/{id}
```

### Response
Returns the same structure as send message response.

## List Messages

### Endpoint
```
GET /v2/messages
```

### Query Parameters

- `page[size]` (integer) - Number of records per page (default: 20, max: 250)
- `page[number]` (integer) - Page number (default: 1)
- `filter[phone_number]` - Filter by phone number (E.164 format)
- `filter[direction]` - Filter by direction (`inbound` or `outbound`)
- `filter[status]` - Filter by status
- `filter[from]` - Filter by sender
- `filter[to]` - Filter by recipient

### Example Request
```bash
curl -X GET "https://api.telnyx.com/v2/messages?page[size]=10&filter[phone_number]=+18445550001" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Response
```json
{
  "data": [
    { /* message object */ },
    { /* message object */ }
  ],
  "meta": {
    "page_number": 1,
    "page_size": 10,
    "total_pages": 5,
    "total_results": 47
  }
}
```

## Message Status Values

- `queued` - Message accepted by Telnyx
- `sending` - Being sent to carrier
- `sent` - Delivered to carrier
- `delivered` - Delivered to recipient (confirmed)
- `delivery_unconfirmed` - Sent but delivery not confirmed
- `delivery_failed` - Failed to deliver
- `sending_failed` - Failed to send

## Character Encoding

### GSM-7 Encoding
- 160 characters per SMS segment
- Standard ASCII characters
- Some special characters: @£$¥èéùìòÇØøÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !"#¤%&'()*+,-./

### UCS-2 Encoding (Unicode)
- 70 characters per SMS segment
- Used for emojis, non-Latin scripts
- Automatically selected if message contains unicode

## Message Segmentation

- Long messages automatically split into parts
- Each part counted separately for billing
- Maximum 10 parts per message
- Concatenation headers reduce character count per segment:
  - GSM-7: 153 characters per segment (multi-part)
  - UCS-2: 67 characters per segment (multi-part)

## MMS Limitations

- Maximum total media size: 1MB
- Supported formats: JPG, PNG, GIF, MP4, PDF
- Multiple media files allowed
- Not all carriers support MMS
- Higher cost than SMS

## Best Practices

1. **Always use E.164 format** for phone numbers
2. **Validate phone numbers** before sending
3. **Handle webhook events** for delivery status
4. **Implement retry logic** for failed messages
5. **Use messaging profiles** for production
6. **Monitor message costs** in Mission Control
7. **Test with your own number** before bulk sending
8. **Respect opt-out requests** and comply with regulations

## Error Handling

See `error-codes.md` for complete error reference.

Common errors:
- `10001` - Invalid phone number format
- `10002` - Invalid messaging profile
- `10003` - Insufficient balance
- `40000` - Authentication failed
- `40300` - Forbidden
- `42900` - Rate limit exceeded
