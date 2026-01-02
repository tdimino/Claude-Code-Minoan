/**
 * Telnyx Webhook Handler with Ed25519 Signature Validation
 *
 * Use case: Receive incoming SMS/MMS messages with security validation
 * Pattern: Ed25519 signature verification with tweetnacl
 *
 * Install dependencies:
 * npm install tweetnacl @types/tweetnacl
 */

import type { NextApiRequest, NextApiResponse } from 'next';
import nacl from 'tweetnacl';

// CRITICAL: Disable Next.js body parser to preserve raw body
export const config = {
  api: {
    bodyParser: false,
  },
};

/**
 * Read raw request body as string
 */
async function readRawBody(req: NextApiRequest): Promise<string> {
  return new Promise<string>((resolve, reject) => {
    let data = '';
    req.setEncoding('utf8');
    req.on('data', (chunk) => { data += chunk; });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

/**
 * Validate Telnyx webhook signature using Ed25519
 *
 * Telnyx signs webhooks with Ed25519 public key cryptography.
 * Signed payload format: `${timestamp}|${rawBody}`
 */
function validateTelnyxSignature(
  rawBody: string,
  signature: string,
  timestamp: string,
  publicKey: string
): boolean {
  try {
    // Build the signed payload: timestamp|rawBody
    const signedPayload = `${timestamp}|${rawBody}`;

    // Convert base64 strings to Uint8Array
    const publicKeyBytes = Buffer.from(publicKey, 'base64');
    const signatureBytes = Buffer.from(signature, 'base64');
    const messageBytes = Buffer.from(signedPayload, 'utf-8');

    // Verify Ed25519 signature
    return nacl.sign.detached.verify(
      messageBytes,
      signatureBytes,
      publicKeyBytes
    );
  } catch (error) {
    console.error('Signature validation error:', error);
    return false;
  }
}

/**
 * Webhook handler
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Only accept POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Step 1: Read raw body (needed for signature validation)
    const rawBody = await readRawBody(req);

    // Step 2: Validate signature
    const signature = req.headers['telnyx-signature-ed25519'] as string;
    const timestamp = req.headers['telnyx-timestamp'] as string;
    const publicKey = process.env.TELNYX_WEBHOOK_PUBLIC_KEY as string;

    if (!signature || !timestamp) {
      console.error('Missing signature headers');
      return res.status(401).json({ error: 'Missing signature headers' });
    }

    const isValid = validateTelnyxSignature(rawBody, signature, timestamp, publicKey);

    if (!isValid) {
      console.error('Invalid signature');
      return res.status(403).json({ error: 'Invalid signature' });
    }

    // Step 3: Parse body for processing
    const payload = JSON.parse(rawBody);
    console.log('Webhook received:', payload.data.event_type);

    // Step 4: Handle message.received event
    if (payload.data.event_type === 'message.received') {
      const messageData = payload.data.payload;
      const from = messageData.from.phone_number;
      const to = messageData.to[0].phone_number;
      const text = messageData.text;

      console.log(`Received SMS from ${from}: ${text}`);

      // Process message (your business logic here)
      await processIncomingSMS({ from, to, text, messageId: messageData.id });
    }

    // Step 5: Return 200 OK (Telnyx expects simple HTTP 200)
    return res.status(200).send('');

  } catch (error) {
    console.error('Webhook error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

async function processIncomingSMS(data: {
  from: string;
  to: string;
  text: string;
  messageId: string;
}): Promise<void> {
  // Your processing logic here
  console.log('Processing:', data);
}
