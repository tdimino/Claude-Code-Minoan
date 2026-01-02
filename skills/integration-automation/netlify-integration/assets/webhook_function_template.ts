// Netlify Function Template: Webhook Handler
// Copy this to .netlify/functions/webhook.ts or similar

import type { Handler, HandlerEvent, HandlerContext } from "@netlify/functions";

/**
 * Webhook handler with async processing pattern
 *
 * This template implements the "return response immediately, process async" pattern
 * which is critical for webhooks that must respond within 10 seconds but need
 * longer processing time.
 *
 * Key features:
 * - Immediate response (< 1s)
 * - Async processing without blocking response
 * - Signature validation
 * - Error handling
 * - Structured logging
 */
export const handler: Handler = async (
  event: HandlerEvent,
  context: HandlerContext
) => {
  // Log incoming request
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level: "info",
    message: "Webhook received",
    requestId: context.requestId,
    method: event.httpMethod,
    path: event.path,
  }));

  try {
    // ==========================================
    // 1. Quick Validation (< 1s)
    // ==========================================

    // Validate HTTP method
    if (event.httpMethod !== "POST") {
      return {
        statusCode: 405,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Method not allowed" }),
      };
    }

    // Validate request body
    if (!event.body) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Request body required" }),
      };
    }

    // Validate signature (implement your signature validation here)
    const isValid = await validateSignature(event);
    if (!isValid) {
      console.error(JSON.stringify({
        timestamp: new Date().toISOString(),
        level: "error",
        message: "Signature validation failed",
        requestId: context.requestId,
      }));

      return {
        statusCode: 401,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Unauthorized" }),
      };
    }

    // ==========================================
    // 2. Return Response IMMEDIATELY
    // ==========================================

    // Create response to return immediately
    const response = {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        received: true,
        requestId: context.requestId,
      }),
    };

    // ==========================================
    // 3. Process Async (DON'T AWAIT)
    // ==========================================

    // Process webhook WITHOUT awaiting
    // This continues after the response is sent
    processWebhookAsync(event, context)
      .catch((error) => {
        console.error(JSON.stringify({
          timestamp: new Date().toISOString(),
          level: "error",
          message: "Async processing error",
          requestId: context.requestId,
          error: error instanceof Error ? error.message : "Unknown",
          stack: error instanceof Error ? error.stack : undefined,
        }));

        // TODO: Log to error tracking service (Sentry, etc.)
      });

    // Return response immediately
    return response;

  } catch (error) {
    // Catch synchronous errors only
    console.error(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: "error",
      message: "Webhook handler error",
      requestId: context.requestId,
      error: error instanceof Error ? error.message : "Unknown",
      stack: error instanceof Error ? error.stack : undefined,
    }));

    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        error: "Internal server error",
        requestId: context.requestId,
      }),
    };
  }
};

/**
 * Validate webhook signature
 * Implement your signature validation logic here
 */
async function validateSignature(event: HandlerEvent): Promise<boolean> {
  // TODO: Implement signature validation
  // Example for Telnyx:
  // const signature = event.headers["telnyx-signature-ed25519"];
  // const timestamp = event.headers["telnyx-timestamp"];
  // const publicKey = process.env.TELNYX_PUBLIC_KEY;
  // ... validate signature

  // For now, return true (CHANGE THIS IN PRODUCTION)
  return true;
}

/**
 * Process webhook asynchronously
 * This runs AFTER the response is sent to the webhook sender
 */
async function processWebhookAsync(
  event: HandlerEvent,
  context: HandlerContext
): Promise<void> {
  const startTime = Date.now();

  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level: "info",
    message: "Starting async processing",
    requestId: context.requestId,
  }));

  try {
    // Parse request body
    const data = JSON.parse(event.body || "{}");

    // ==========================================
    // TODO: Add your processing logic here
    // ==========================================

    // Example: Save to database
    // await saveToDatabase(data);

    // Example: Trigger workflow
    // await triggerWorkflow(data);

    // Example: Send notification
    // await sendNotification(data);

    // Log completion
    const duration = Date.now() - startTime;
    console.log(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: "info",
      message: "Async processing complete",
      requestId: context.requestId,
      duration_ms: duration,
    }));

  } catch (error) {
    // Log error (don't throw - response already sent)
    console.error(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: "error",
      message: "Processing failed",
      requestId: context.requestId,
      error: error instanceof Error ? error.message : "Unknown",
      stack: error instanceof Error ? error.stack : undefined,
    }));

    // TODO: Implement retry logic or dead letter queue
  }
}
