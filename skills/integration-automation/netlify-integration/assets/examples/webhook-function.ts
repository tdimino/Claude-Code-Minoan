/**
 * Netlify Function: Webhook Handler with Immediate Response
 *
 * Pattern: Return immediate acknowledgment, then trigger background processing
 * Use case: SMS/webhook handlers that need to respond quickly but process slowly
 */

import { Handler, HandlerEvent, HandlerContext } from '@netlify/functions';

export const handler: Handler = async (
  event: HandlerEvent,
  context: HandlerContext
) => {
  // Only accept POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    // Parse incoming webhook data
    const body = JSON.parse(event.body || '{}');
    console.log('Webhook received:', body);

    // IMMEDIATE: Return success to webhook provider (< 200ms)
    // This prevents timeout errors
    const response = {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ received: true }),
    };

    // BACKGROUND: Trigger background function for processing
    // Note: This is fire-and-forget - don't await
    const baseUrl = process.env.URL || `https://${event.headers.host}`;
    fetch(`${baseUrl}/.netlify/functions/webhook-background`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).catch(err => console.error('Background trigger failed:', err));

    return response;
  } catch (error) {
    console.error('Webhook error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' }),
    };
  }
};
