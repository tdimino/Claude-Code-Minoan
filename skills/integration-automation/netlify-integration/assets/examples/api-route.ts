/**
 * Next.js API Route: Webhook Handler with Raw Body Parsing
 *
 * Use case: Webhooks requiring signature validation (Twilio, Stripe, GitHub)
 * Pattern: Disable Next.js bodyParser to preserve raw request body
 */

import type { NextApiRequest, NextApiResponse } from 'next';
import crypto from 'crypto';

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
 * Validate webhook signature (example for HMAC-SHA256)
 */
function validateSignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

/**
 * Get base URL for internal requests
 */
function getBaseUrl(req: NextApiRequest): string {
  const proto = (req.headers['x-forwarded-proto'] as string) || 'https';
  const host = (req.headers['x-forwarded-host'] as string) || (req.headers.host as string);
  return `${proto}://${host}`;
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
    // Step 1: Read raw body
    const rawBody = await readRawBody(req);

    // Step 2: Validate signature (example)
    const signature = req.headers['x-webhook-signature'] as string;
    const secret = process.env.WEBHOOK_SECRET as string;

    if (!validateSignature(rawBody, signature, secret)) {
      return res.status(401).json({ error: 'Invalid signature' });
    }

    // Step 3: Parse body for processing
    const body = JSON.parse(rawBody);
    console.log('Webhook received:', body);

    // Step 4: Return immediate response
    res.status(200).json({ received: true });

    // Step 5: Trigger background processing (fire-and-forget)
    const baseUrl = getBaseUrl(req);
    fetch(`${baseUrl}/.netlify/functions/webhook-background`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: rawBody,
    }).catch(err => console.error('Background trigger failed:', err));

  } catch (error) {
    console.error('Webhook error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

/**
 * Alternative: Without signature validation
 * For webhooks that don't require signature validation
 */
export async function simpleWebhookHandler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Read body (can use default bodyParser in this case)
    const body = req.body;
    console.log('Webhook received:', body);

    // Process immediately (if fast) or trigger background function
    await processWebhook(body);

    return res.status(200).json({ success: true });
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

async function processWebhook(data: any): Promise<void> {
  // Your processing logic here
  console.log('Processing:', data);
}
