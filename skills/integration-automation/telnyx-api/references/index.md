# Telnyx API Reference Index

This directory contains comprehensive reference documentation for the Telnyx API.

## Reference Files

### [messaging-api.md](./messaging-api.md)
Complete reference for the Messaging API including:
- Send message endpoint (SMS/MMS)
- Retrieve message endpoint
- List messages endpoint
- Message status values
- Character encoding (GSM-7, UCS-2)
- Message segmentation
- MMS limitations
- Best practices

**Use when:** You need detailed API specifications for sending/receiving messages, understanding message states, or working with character encodings.

### [webhooks.md](./webhooks.md)
Comprehensive webhook documentation including:
- Webhook configuration
- Event types (message.sent, message.delivered, message.failed, message.received)
- Call control events
- Webhook security and signature verification
- Best practices (idempotency, async processing, retry handling)
- Testing webhooks locally (ngrok, webhook.site)
- Complete webhook handler examples

**Use when:** Implementing webhook receivers, handling real-time events, or debugging webhook delivery issues.

### [authentication.md](./authentication.md)
Authentication and security documentation including:
- API key management
- Bearer token authentication
- Environment variable setup
- Security best practices
- API key rotation
- IP whitelisting
- Webhook signature verification
- Testing authentication
- Common authentication mistakes

**Use when:** Setting up API access, managing credentials, implementing security measures, or troubleshooting authentication issues.

### [best-practices.md](./best-practices.md)
Production deployment best practices including:
- Using messaging profiles
- Error handling patterns
- Exponential backoff retry logic
- Rate limiting for bulk sending
- Message tracking and status management
- Phone number validation and formatting
- Message content optimization
- Webhook processing patterns
- Monitoring and logging
- Cost optimization
- Production readiness checklist

**Use when:** Preparing for production deployment, implementing robust error handling, or optimizing costs and performance.

### [error-codes.md](./error-codes.md)
Complete error code reference including:
- HTTP status codes
- Authentication errors (401, 403)
- Validation errors (400, 422)
- Rate limiting errors (429)
- Server errors (500, 502, 503)
- Webhook-specific delivery errors
- Error handling patterns
- Retry logic examples
- Debugging tips

**Use when:** Troubleshooting errors, implementing error handling, or understanding failure modes.

## Quick Navigation

### Getting Started
1. Start with [authentication.md](./authentication.md) to set up API access
2. Review [messaging-api.md](./messaging-api.md) for basic sending
3. Set up [webhooks.md](./webhooks.md) for delivery notifications

### Production Deployment
1. Read [best-practices.md](./best-practices.md) thoroughly
2. Implement error handling from [error-codes.md](./error-codes.md)
3. Set up monitoring and logging
4. Complete production checklist

### Troubleshooting
1. Check [error-codes.md](./error-codes.md) for specific error
2. Verify authentication in [authentication.md](./authentication.md)
3. Review [webhooks.md](./webhooks.md) if webhook issues
4. Check [Telnyx Status Page](https://status.telnyx.com/)

## External Resources

- **Main SKILL.md**: Return to main skill file for quick reference and code examples
- **Telnyx Developer Portal**: https://developers.telnyx.com/
- **API Reference**: https://developers.telnyx.com/api/
- **Mission Control**: https://portal.telnyx.com/
- **Status Page**: https://status.telnyx.com/
- **Support**: https://support.telnyx.com/

## Document Updates

These reference documents are comprehensive but may not reflect the absolute latest API changes. Always refer to the official Telnyx documentation at https://developers.telnyx.com/ for the most current information.

Last Updated: October 2025
