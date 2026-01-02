/**
 * Telnyx SMS Sending Examples
 *
 * Demonstrates:
 * - Basic SMS sending
 * - MMS with media attachments
 * - Using messaging profiles
 * - Error handling with retries
 */

// ============================================
// Example 1: Basic SMS
// ============================================

async function sendBasicSMS(to: string, from: string, text: string): Promise<string> {
  const response = await fetch('https://api.telnyx.com/v2/messages', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.TELNYX_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from,
      to,
      text,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Telnyx API error: ${response.status} ${error}`);
  }

  const data = await response.json();
  return data.data.id;  // Returns message UUID
}

// Usage
const messageId = await sendBasicSMS(
  '+14155552671',
  '+14155559999',
  'Hello from Telnyx!'
);
console.log('Message sent:', messageId);

// ============================================
// Example 2: MMS with Media
// ============================================

async function sendMMS(params: {
  to: string;
  from: string;
  text: string;
  mediaUrls: string[];
}): Promise<string> {
  const response = await fetch('https://api.telnyx.com/v2/messages', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.TELNYX_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: params.from,
      to: params.to,
      text: params.text,
      media_urls: params.mediaUrls,  // Telnyx auto-sets type="MMS"
    }),
  });

  const data = await response.json();
  return data.data.id;
}

// Usage
await sendMMS({
  to: '+14155552671',
  from: '+14155559999',
  text: 'Check out this image!',
  mediaUrls: ['https://example.com/image.jpg'],
});

// ============================================
// Example 3: Using Messaging Profile
// ============================================

async function sendWithProfile(to: string, text: string): Promise<string> {
  const response = await fetch('https://api.telnyx.com/v2/messages', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.TELNYX_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      to,
      text,
      messaging_profile_id: process.env.TELNYX_MESSAGING_PROFILE_ID,
      // No 'from' needed - profile handles it
    }),
  });

  const data = await response.json();
  return data.data.id;
}

// ============================================
// Example 4: Error Handling with Retry
// ============================================

async function sendWithRetry(
  to: string,
  from: string,
  text: string,
  maxRetries: number = 3
): Promise<string> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await sendBasicSMS(to, from, text);
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));

      // Retry only on 500 errors (server issues)
      const is500Error = err.message.includes('500');

      if (is500Error && attempt < maxRetries) {
        const delayMs = Math.pow(2, attempt) * 1000;  // Exponential backoff
        console.log(`Retry ${attempt}/${maxRetries} in ${delayMs}ms...`);
        await new Promise(resolve => setTimeout(resolve, delayMs));
      } else {
        throw err;
      }
    }
  }

  throw new Error('Failed after max retries');
}

// ============================================
// Example 5: Phone Number Validation
// ============================================

function normalizeToE164(phoneNumber: string): string {
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

// Usage
const normalized = normalizeToE164('(415) 555-1234');  // +14155551234
await sendBasicSMS(normalized, '+14155559999', 'Hello!');

// ============================================
// Example 6: Complete TypeScript Class
// ============================================

interface TelnyxConfig {
  apiKey: string;
  fromNumber?: string;
  messagingProfileId?: string;
}

class TelnyxClient {
  private apiKey: string;
  private fromNumber?: string;
  private messagingProfileId?: string;

  constructor(config: TelnyxConfig) {
    this.apiKey = config.apiKey;
    this.fromNumber = config.fromNumber;
    this.messagingProfileId = config.messagingProfileId;
  }

  async sendSMS(to: string, text: string, from?: string): Promise<string> {
    const payload: any = {
      to: this.normalizePhoneNumber(to),
      text,
    };

    // Use messaging profile if configured, otherwise use from number
    if (this.messagingProfileId) {
      payload.messaging_profile_id = this.messagingProfileId;
    } else if (from || this.fromNumber) {
      payload.from = this.normalizePhoneNumber(from || this.fromNumber!);
    } else {
      throw new Error('Must provide either from number or messaging_profile_id');
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
    return data.data.id;
  }

  private normalizePhoneNumber(phoneNumber: string): string {
    let digits = phoneNumber.replace(/\D/g, '');
    if (phoneNumber.startsWith('+') && digits.length >= 11) {
      return phoneNumber;
    }
    if (digits.length === 10) {
      digits = '1' + digits;
    }
    return '+' + digits;
  }
}

// Usage
const telnyx = new TelnyxClient({
  apiKey: process.env.TELNYX_API_KEY!,
  messagingProfileId: process.env.TELNYX_MESSAGING_PROFILE_ID,
});

await telnyx.sendSMS('+14155552671', 'Hello from TypeScript!');
