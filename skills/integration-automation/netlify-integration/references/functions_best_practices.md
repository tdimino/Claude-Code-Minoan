# Netlify Functions Best Practices

Patterns and best practices for developing Netlify Functions with Next.js, focusing on SMS/telephony applications.

## Function Structure

### Basic Handler Pattern

```typescript
import type { Handler, HandlerEvent, HandlerContext } from "@netlify/functions";

export const handler: Handler = async (
  event: HandlerEvent,
  context: HandlerContext
) => {
  try {
    // Parse request
    const body = JSON.parse(event.body || "{}");
    const headers = event.headers;

    // Process request
    const result = await processRequest(body);

    // Return response
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(result),
    };
  } catch (error) {
    console.error("Function error:", error);
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        error: "Internal server error",
        message: error instanceof Error ? error.message : "Unknown error",
      }),
    };
  }
};
```

### Async Processing Pattern (Critical for Webhooks)

For webhook handlers that must respond quickly (< 10s), return response immediately and process async:

```typescript
export const handler: Handler = async (event, context) => {
  // Validate request
  const isValid = validateWebhook(event);
  if (!isValid) {
    return { statusCode: 401, body: "Unauthorized" };
  }

  // Return 200 IMMEDIATELY
  const response = {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ received: true }),
  };

  // Process async WITHOUT awaiting
  // This continues after response is sent
  processWebhookAsync(event.body)
    .catch((error) => {
      console.error("Async processing error:", error);
      // Log to monitoring service
    });

  return response;
};

// Separate async processor
async function processWebhookAsync(body: string) {
  const data = JSON.parse(body);

  // Long-running operations
  await saveToDatabase(data);
  await triggerWorkflow(data);
  await sendNotification(data);
}
```

## Performance Optimization

### Cold Start Reduction

```typescript
// ❌ BAD - Import inside handler
export const handler: Handler = async (event, context) => {
  const { createClient } = await import("@supabase/supabase-js");
  // Cold start penalty
};

// ✅ GOOD - Import at module level
import { createClient } from "@supabase/supabase-js";

export const handler: Handler = async (event, context) => {
  // Faster execution
};
```

### Connection Pooling

```typescript
// Reuse connections across invocations
let supabaseClient: any = null;

function getSupabaseClient() {
  if (!supabaseClient) {
    supabaseClient = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  }
  return supabaseClient;
}

export const handler: Handler = async (event, context) => {
  const supabase = getSupabaseClient();
  // Use cached client
};
```

### Lazy Loading

```typescript
// Load heavy dependencies only when needed
export const handler: Handler = async (event, context) => {
  const operation = event.queryStringParameters?.operation;

  if (operation === "image") {
    // Only load sharp when needed
    const sharp = (await import("sharp")).default;
    // Process image
  } else if (operation === "pdf") {
    // Only load pdf-lib when needed
    const { PDFDocument } = await import("pdf-lib");
    // Process PDF
  }
};
```

## Error Handling

### Comprehensive Error Handling

```typescript
export const handler: Handler = async (event, context) => {
  try {
    // Validate input
    if (!event.body) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "Request body required" }),
      };
    }

    // Parse request
    let data;
    try {
      data = JSON.parse(event.body);
    } catch (parseError) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "Invalid JSON" }),
      };
    }

    // Process
    const result = await processData(data);

    return {
      statusCode: 200,
      body: JSON.stringify(result),
    };
  } catch (error) {
    // Log full error for debugging
    console.error("Handler error:", {
      message: error instanceof Error ? error.message : "Unknown",
      stack: error instanceof Error ? error.stack : undefined,
      event: {
        httpMethod: event.httpMethod,
        path: event.path,
        headers: event.headers,
      },
    });

    // Return user-friendly error
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: "Internal server error",
        requestId: context.requestId,
      }),
    };
  }
};
```

### Retry Logic

```typescript
async function retryOperation<T>(
  operation: () => Promise<T>,
  maxRetries = 3,
  delayMs = 1000
): Promise<T> {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      console.warn(`Attempt ${attempt} failed:`, error);

      if (attempt < maxRetries) {
        await new Promise((resolve) => setTimeout(resolve, delayMs * attempt));
      }
    }
  }

  throw lastError;
}

// Usage
export const handler: Handler = async (event, context) => {
  const result = await retryOperation(
    () => callExternalAPI(event.body),
    3,    // 3 attempts
    1000  // 1 second base delay
  );

  return {
    statusCode: 200,
    body: JSON.stringify(result),
  };
};
```

## Security

### Input Validation

```typescript
import { z } from "zod";

// Define schema
const WebhookSchema = z.object({
  from: z.string().min(10).max(15),
  to: z.string().min(10).max(15),
  body: z.string().min(1).max(1600),
  messageId: z.string().uuid(),
});

export const handler: Handler = async (event, context) => {
  try {
    // Parse and validate
    const data = JSON.parse(event.body || "{}");
    const validated = WebhookSchema.parse(data);

    // Process validated data
    await processMessage(validated);

    return {
      statusCode: 200,
      body: JSON.stringify({ success: true }),
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        statusCode: 400,
        body: JSON.stringify({
          error: "Validation failed",
          details: error.errors,
        }),
      };
    }

    throw error;
  }
};
```

### Webhook Signature Validation

```typescript
import crypto from "crypto";

function validateTelnyxSignature(
  payload: string,
  signature: string,
  publicKey: string,
  timestamp: string
): boolean {
  try {
    const signedPayload = `${timestamp}|${payload}`;

    const verifier = crypto.createVerify("sha256");
    verifier.update(signedPayload);

    return verifier.verify(
      publicKey,
      signature,
      "base64"
    );
  } catch (error) {
    console.error("Signature validation error:", error);
    return false;
  }
}

export const handler: Handler = async (event, context) => {
  // Validate signature
  const signature = event.headers["telnyx-signature-ed25519"];
  const timestamp = event.headers["telnyx-timestamp"];

  if (!signature || !timestamp) {
    return { statusCode: 401, body: "Missing signature headers" };
  }

  const isValid = validateTelnyxSignature(
    event.body!,
    signature,
    process.env.TELNYX_PUBLIC_KEY!,
    timestamp
  );

  if (!isValid) {
    return { statusCode: 401, body: "Invalid signature" };
  }

  // Process webhook
  // ...
};
```

### Rate Limiting

```typescript
// Simple in-memory rate limiter
const rateLimits = new Map<string, number[]>();

function isRateLimited(
  identifier: string,
  maxRequests: number,
  windowMs: number
): boolean {
  const now = Date.now();
  const timestamps = rateLimits.get(identifier) || [];

  // Remove old timestamps
  const recentTimestamps = timestamps.filter((t) => now - t < windowMs);

  if (recentTimestamps.length >= maxRequests) {
    return true;
  }

  // Add current timestamp
  recentTimestamps.push(now);
  rateLimits.set(identifier, recentTimestamps);

  return false;
}

export const handler: Handler = async (event, context) => {
  const phoneNumber = event.queryStringParameters?.from;

  if (!phoneNumber) {
    return { statusCode: 400, body: "Phone number required" };
  }

  // 5 requests per minute per phone number
  if (isRateLimited(phoneNumber, 5, 60000)) {
    return {
      statusCode: 429,
      body: JSON.stringify({ error: "Rate limit exceeded" }),
    };
  }

  // Process request
  // ...
};
```

## Database Operations

### Supabase Integration

```typescript
import { createClient } from "@supabase/supabase-js";

// Singleton client
let supabase: any = null;

function getSupabase() {
  if (!supabase) {
    supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  }
  return supabase;
}

export const handler: Handler = async (event, context) => {
  const db = getSupabase();

  try {
    // Insert with error handling
    const { data, error } = await db
      .from("messages")
      .insert({
        from_number: "+12345678900",
        to_number: "+10987654321",
        body: "Test message",
        direction: "inbound",
      })
      .select()
      .single();

    if (error) {
      console.error("Database error:", error);
      return {
        statusCode: 500,
        body: JSON.stringify({ error: "Database operation failed" }),
      };
    }

    return {
      statusCode: 200,
      body: JSON.stringify(data),
    };
  } catch (error) {
    console.error("Unexpected error:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Internal server error" }),
    };
  }
};
```

### Transaction Patterns

```typescript
export const handler: Handler = async (event, context) => {
  const db = getSupabase();

  try {
    // Start transaction (via RPC)
    const { data, error } = await db.rpc("process_message_transaction", {
      p_from: "+12345678900",
      p_to: "+10987654321",
      p_body: "Message text",
    });

    if (error) throw error;

    return {
      statusCode: 200,
      body: JSON.stringify({ success: true }),
    };
  } catch (error) {
    console.error("Transaction failed:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Transaction failed" }),
    };
  }
};
```

## Monitoring and Logging

### Structured Logging

```typescript
function log(level: string, message: string, context?: any) {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    message,
    context,
  }));
}

export const handler: Handler = async (event, context) => {
  log("info", "Function invoked", {
    requestId: context.requestId,
    httpMethod: event.httpMethod,
    path: event.path,
  });

  try {
    // Process
    const result = await processRequest(event.body);

    log("info", "Request processed successfully", {
      requestId: context.requestId,
      result,
    });

    return {
      statusCode: 200,
      body: JSON.stringify(result),
    };
  } catch (error) {
    log("error", "Request processing failed", {
      requestId: context.requestId,
      error: error instanceof Error ? error.message : "Unknown",
      stack: error instanceof Error ? error.stack : undefined,
    });

    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Internal server error" }),
    };
  }
};
```

### Performance Metrics

```typescript
function measureDuration<T>(
  label: string,
  fn: () => Promise<T>
): Promise<T> {
  const start = Date.now();

  return fn().finally(() => {
    const duration = Date.now() - start;
    console.log(JSON.stringify({
      metric: "duration",
      label,
      duration_ms: duration,
    }));
  });
}

export const handler: Handler = async (event, context) => {
  return measureDuration("handler_execution", async () => {
    const dbResult = await measureDuration("database_query", async () => {
      return await queryDatabase();
    });

    const apiResult = await measureDuration("external_api_call", async () => {
      return await callExternalAPI();
    });

    return {
      statusCode: 200,
      body: JSON.stringify({ dbResult, apiResult }),
    };
  });
};
```

## Testing

### Local Testing Setup

```typescript
// test-function.ts
import { handler } from "./.netlify/functions/webhook";
import type { HandlerEvent, HandlerContext } from "@netlify/functions";

async function testWebhook() {
  const event: HandlerEvent = {
    httpMethod: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      from: "+12345678900",
      to: "+10987654321",
      body: "Test message",
    }),
    isBase64Encoded: false,
    path: "/.netlify/functions/webhook",
    queryStringParameters: null,
    multiValueQueryStringParameters: null,
    pathParameters: null,
    stageVariables: null,
    requestContext: {} as any,
    resource: "",
    multiValueHeaders: {},
    rawUrl: "",
    rawQuery: "",
  };

  const context: HandlerContext = {
    callbackWaitsForEmptyEventLoop: true,
    functionName: "webhook",
    functionVersion: "1",
    invokedFunctionArn: "",
    memoryLimitInMB: "1024",
    awsRequestId: "test-request-id",
    logGroupName: "",
    logStreamName: "",
    getRemainingTimeInMillis: () => 30000,
    done: () => {},
    fail: () => {},
    succeed: () => {},
    clientContext: undefined,
    identity: undefined,
  };

  const response = await handler(event, context);
  console.log("Response:", response);
}

testWebhook().catch(console.error);
```

Run with:
```bash
ts-node test-function.ts
```

## Common Patterns for Twilio-Aldea

### Unified SMS Webhook Handler

```typescript
export const handler: Handler = async (event, context) => {
  // Detect provider
  const provider = detectProvider(event);

  // Validate signature
  const isValid = await validateSignature(event, provider);
  if (!isValid) {
    return { statusCode: 401, body: "Unauthorized" };
  }

  // Return response immediately
  const response = {
    statusCode: 200,
    body: JSON.stringify({ received: true }),
  };

  // Process async
  processSMSAsync(event, provider).catch((error) => {
    console.error("SMS processing error:", error);
  });

  return response;
};

function detectProvider(event: HandlerEvent): "telnyx" | "twilio" {
  if (event.headers["telnyx-signature-ed25519"]) return "telnyx";
  if (event.headers["x-twilio-signature"]) return "twilio";
  return "telnyx"; // default
}
```

### Session Management

```typescript
async function getOrCreateSession(phoneNumber: string) {
  const db = getSupabase();

  // Try to get existing session
  let { data: session, error } = await db
    .from("user_sessions")
    .select("*")
    .eq("phone_number", phoneNumber)
    .single();

  // Create new session if doesn't exist
  if (error || !session) {
    const { data: newSession } = await db
      .from("user_sessions")
      .insert({
        phone_number: phoneNumber,
        assigned_persona: "dr-shefali",
        session_state: {},
      })
      .select()
      .single();

    session = newSession;
  }

  return session;
}
```

## Resources

- [Netlify Functions Documentation](https://docs.netlify.com/functions/overview/)
- [Handler API Reference](https://docs.netlify.com/functions/api/)
- [Function Examples](https://github.com/netlify/functions-examples)
