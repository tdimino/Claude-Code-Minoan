/**
 * Complete Telnyx Provider Implementation
 *
 * Production-ready provider class from Twilio-Aldea platform.
 * Demonstrates full implementation with:
 * - Ed25519 signature validation
 * - Phone number normalization
 * - Messaging profile support
 * - Debugger mode for testing
 * - Error handling
 */

import nacl from 'tweetnacl';

// ============================================
// Type Definitions
// ============================================

interface IncomingMessage {
  messageId: string;
  from: string;
  to: string;
  body: string;
  timestamp: Date;
  provider: 'telnyx';
  rawPayload: any;
}

interface OutgoingMessage {
  from?: string;
  to: string;
  body: string;
}

// ============================================
// Base Provider Class
// ============================================

abstract class BaseSMSProvider {
  abstract readonly name: string;
  abstract sendSMS(message: OutgoingMessage): Promise<string>;
  abstract validateWebhook(payload: string | any, signature: string, url: string, timestamp?: string): boolean;
  abstract parseIncomingMessage(payload: any): IncomingMessage;
  abstract getImmediateResponse(acknowledgment?: string): any;

  /**
   * Normalize phone number to E.164 format
   * E.164: +[country code][number] (e.g., +14155551234)
   */
  protected normalizePhoneNumber(phoneNumber: string): string {
    // Remove all non-digit characters
    let digits = phoneNumber.replace(/\D/g, '');

    // If already has + prefix and 11+ digits, return as-is
    if (phoneNumber.startsWith('+') && digits.length >= 11) {
      return phoneNumber;
    }

    // Add country code if missing (default: US +1)
    if (digits.length === 10) {
      digits = '1' + digits;
    }

    // Add + prefix
    return '+' + digits;
  }

  /**
   * Check if this is a debugger session (no real SMS sending)
   * Debugger uses phone format: debugger-{sessionId}
   */
  protected isDebuggerSession(phoneNumber: string): boolean {
    return phoneNumber.startsWith('debugger-');
  }
}

// ============================================
// Telnyx Provider Implementation
// ============================================

export class TelnyxProvider extends BaseSMSProvider {
  readonly name = 'telnyx' as const;
  private apiKey: string;
  private fromNumber: string;
  private webhookPublicKey?: string;
  private messagingProfileId?: string;

  constructor() {
    super();

    const apiKey = process.env.TELNYX_API_KEY;
    const fromNumber = process.env.TELNYX_PHONE_NUMBER;

    if (!apiKey || !fromNumber) {
      throw new Error('Missing required Telnyx environment variables: TELNYX_API_KEY, TELNYX_PHONE_NUMBER');
    }

    this.apiKey = apiKey;
    this.fromNumber = fromNumber;
    this.webhookPublicKey = process.env.TELNYX_WEBHOOK_PUBLIC_KEY;
    this.messagingProfileId = process.env.TELNYX_MESSAGING_PROFILE_ID;
  }

  /**
   * Send SMS via Telnyx Messages API
   *
   * API Reference: https://developers.telnyx.com/docs/api/v2/messaging/Messages
   */
  async sendSMS(message: OutgoingMessage): Promise<string> {
    // Debugger mode - skip actual send
    if (this.isDebuggerSession(message.to)) {
      console.log('[Telnyx] Debugger mode - skipping SMS send:', message.body);
      return `debug-${Date.now()}`;
    }

    const payload: any = {
      from: message.from || this.fromNumber,
      to: this.normalizePhoneNumber(message.to),
      text: message.body,
    };

    // Add messaging profile ID if configured (recommended for production)
    if (this.messagingProfileId) {
      payload.messaging_profile_id = this.messagingProfileId;
    }

    const response = await fetch('https://api.telnyx.com/v2/messages', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Telnyx API error: ${response.status} ${error}`);
    }

    const data = await response.json();
    return data.data.id;  // Telnyx returns { data: { id: "uuid" } }
  }

  /**
   * Send MMS via Telnyx Messages API
   *
   * Supports media attachments via media_urls parameter.
   */
  async sendMMS(params: {
    from: string;
    to: string;
    text: string;
    media_urls?: string[];
  }): Promise<any> {
    // Debugger mode - skip actual send
    if (this.isDebuggerSession(params.to)) {
      console.log('[Telnyx] Debugger mode - skipping MMS send:', params.text);
      return { data: { id: `debug-${Date.now()}` } };
    }

    const payload: any = {
      from: params.from,
      to: this.normalizePhoneNumber(params.to),
      text: params.text,
    };

    // Add media URLs if provided (makes it MMS)
    if (params.media_urls && params.media_urls.length > 0) {
      payload.media_urls = params.media_urls;
    }

    // Add messaging profile ID if configured
    if (this.messagingProfileId) {
      payload.messaging_profile_id = this.messagingProfileId;
    }

    const response = await fetch('https://api.telnyx.com/v2/messages', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Telnyx API error: ${response.status} ${error}`);
    }

    return await response.json();
  }

  /**
   * Validate Telnyx webhook signature using Ed25519
   *
   * CRITICAL: payload must be the raw body string, NOT parsed object.
   * Ed25519 signatures are calculated on exact byte sequences.
   *
   * Signed payload format: `${timestamp}|${rawBodyString}`
   *
   * References:
   * - https://developers.telnyx.com/development/api-fundamentals/webhooks/receiving-webhooks
   */
  validateWebhook(payload: string | any, signature: string, url: string, timestamp?: string): boolean {
    // If no webhook public key configured, skip validation (not recommended for production)
    if (!this.webhookPublicKey) {
      console.warn('[Telnyx] Webhook signature validation skipped - no TELNYX_WEBHOOK_PUBLIC_KEY configured. This is insecure for production.');
      return true;
    }

    // Ed25519 verification requires timestamp
    if (!timestamp) {
      console.error('[Telnyx] Webhook validation failed - missing telnyx-timestamp header');
      return false;
    }

    try {
      // Build the signed payload: timestamp|rawBody
      const bodyString = typeof payload === 'string' ? payload : JSON.stringify(payload);
      const signedPayload = `${timestamp}|${bodyString}`;

      // Convert base64 strings to Uint8Array for nacl
      const publicKeyBytes = Buffer.from(this.webhookPublicKey, 'base64');
      const signatureBytes = Buffer.from(signature, 'base64');
      const messageBytes = Buffer.from(signedPayload, 'utf-8');

      // Verify Ed25519 signature
      const isValid = nacl.sign.detached.verify(
        messageBytes,
        signatureBytes,
        publicKeyBytes
      );

      if (!isValid) {
        console.error('[Telnyx] Webhook signature verification failed');
      }

      return isValid;
    } catch (error) {
      console.error('[Telnyx] Webhook validation error:', error);
      return false;
    }
  }

  /**
   * Parse Telnyx webhook payload into standardized format
   *
   * Telnyx webhook structure:
   * {
   *   data: {
   *     event_type: "message.received",
   *     payload: {
   *       id: "message-uuid",
   *       from: { phone_number: "+15551234567" },
   *       to: [{ phone_number: "+15559876543" }],
   *       text: "Hello world"
   *     }
   *   }
   * }
   */
  parseIncomingMessage(payload: any): IncomingMessage {
    const eventData = payload.data;
    const messageData = eventData.payload;

    return {
      messageId: messageData.id,
      from: this.normalizePhoneNumber(messageData.from.phone_number),
      to: this.normalizePhoneNumber(messageData.to[0].phone_number),
      body: messageData.text || '',
      timestamp: new Date(messageData.received_at || eventData.occurred_at),
      provider: 'telnyx',
      rawPayload: payload,
    };
  }

  /**
   * Get immediate webhook response
   *
   * Telnyx expects a simple HTTP 200 response (not TwiML like Twilio)
   * Any response body is ignored - just return empty string
   */
  getImmediateResponse(acknowledgment?: string): any {
    // Telnyx doesn't use TwiML-style responses
    // Just return empty string, webhook handler will set status code 200
    return '';
  }
}

// ============================================
// Usage Example
// ============================================

// Initialize provider
const telnyx = new TelnyxProvider();

// Send SMS
const messageId = await telnyx.sendSMS({
  to: '+14155552671',
  body: 'Hello from Telnyx!',
});

// Send MMS
await telnyx.sendMMS({
  from: '+14155559999',
  to: '+14155552671',
  text: 'Check this out!',
  media_urls: ['https://example.com/image.jpg'],
});

// Validate webhook (in webhook handler)
const isValid = telnyx.validateWebhook(
  rawBody,  // Raw request body string
  signature,  // telnyx-signature-ed25519 header
  url,  // Full webhook URL
  timestamp  // telnyx-timestamp header
);

// Parse incoming message
const message = telnyx.parseIncomingMessage(webhookPayload);
console.log(`Received from ${message.from}: ${message.body}`);
