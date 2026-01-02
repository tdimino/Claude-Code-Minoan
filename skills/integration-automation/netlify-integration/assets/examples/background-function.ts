/**
 * Netlify Background Function: Long-Running Processing
 *
 * Pattern: Handle slow processing without webhook timeouts
 * Timeout: 15 minutes (vs 10 seconds for regular functions)
 *
 * File naming convention:
 * - webhook-background.ts → Netlify auto-detects as background function
 * - webhook.ts → Regular function (10s timeout)
 */

import { Handler } from '@netlify/functions';

export const handler: Handler = async (event) => {
  console.log('[Background] Starting long-running process');

  if (!event.body) {
    return { statusCode: 400, body: 'No body provided' };
  }

  try {
    const data = JSON.parse(event.body);

    // Long-running processing (up to 15 minutes allowed)
    await processDataSlowly(data);

    console.log('[Background] Processing completed');
    return {
      statusCode: 200,
      body: JSON.stringify({ success: true }),
    };
  } catch (error: unknown) {
    const err = error instanceof Error ? error : new Error(String(error));
    console.error('[Background] Error:', err);

    // Optional: Log to external service (database, monitoring, etc.)
    await logError(err, event.body);

    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message }),
    };
  }
};

/**
 * Simulate long-running processing
 */
async function processDataSlowly(data: any): Promise<void> {
  // Example: Call external API
  const response = await fetch('https://api.example.com/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  // Example: Wait for async operation
  await new Promise(resolve => setTimeout(resolve, 5000));

  // Example: Save to database
  // await database.insert({ ...data, processed_at: new Date() });
}

/**
 * Log errors to external service
 */
async function logError(error: Error, payload: string): Promise<void> {
  try {
    // Example: Send to monitoring service
    await fetch(process.env.ERROR_WEBHOOK_URL || '', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error: error.message,
        stack: error.stack,
        payload,
        timestamp: new Date().toISOString(),
      }),
    });
  } catch (logErr) {
    console.error('[Background] Failed to log error:', logErr);
  }
}
