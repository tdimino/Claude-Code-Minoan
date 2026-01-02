/**
 * V2 Session API Template (TypeScript)
 *
 * Demonstrates the V2 Session API patterns:
 * - Basic session with send/receive
 * - Multi-turn conversations with context retention
 * - One-shot with unstable_v2_prompt()
 * - Session resume showing memory persistence
 *
 * Based on Anthropic's hello-world-v2 demo.
 */

import {
  unstable_v2_createSession,
  unstable_v2_resumeSession,
  unstable_v2_prompt,
  AssistantMessage,
  TextBlock,
  ResultMessage
} from '@anthropic-ai/claude-agent-sdk';

// V1 vs V2 Comparison:
// V1: query()          → Async generator of all messages
// V2: Session API      → Separate send() / receive()
//
// V1: for await (msg of query({prompt}))
// V2: await session.send() then for await (msg of session.receive())

/**
 * Example 1: Basic Session
 *
 * Create a session, send a message, receive response.
 * Session auto-closes with "await using" syntax.
 */
async function basicSession(): Promise<void> {
  console.log('\n=== Basic Session Example ===\n');

  // Create session (auto-closes when block exits)
  await using session = unstable_v2_createSession({
    model: 'sonnet',
    allowedTools: ['Read', 'Glob', 'Grep']
  });

  // Send a message
  await session.send('What files are in the current directory?');

  // Receive and process responses
  for await (const message of session.receive()) {
    if (message.type === 'assistant') {
      for (const block of message.content) {
        if (block.type === 'text') {
          console.log(block.text);
        }
      }
    } else if (message.type === 'result') {
      console.log(`\nCompleted in ${message.duration_ms}ms`);
    }
  }
}

/**
 * Example 2: Multi-Turn Conversation
 *
 * Multiple send/receive cycles in one session.
 * Context is retained between turns.
 */
async function multiTurnConversation(): Promise<void> {
  console.log('\n=== Multi-Turn Conversation Example ===\n');

  await using session = unstable_v2_createSession({
    model: 'sonnet',
    allowedTools: ['Read', 'Write', 'Glob']
  });

  // First turn
  console.log('User: List the Python files');
  await session.send('List all Python files in this directory');

  for await (const message of session.receive()) {
    if (message.type === 'assistant') {
      for (const block of message.content) {
        if (block.type === 'text') {
          console.log(`Assistant: ${block.text}`);
        }
      }
    }
  }

  // Second turn - context retained
  console.log('\nUser: Show me the first one');
  await session.send('Show me the contents of the first Python file you found');

  for await (const message of session.receive()) {
    if (message.type === 'assistant') {
      for (const block of message.content) {
        if (block.type === 'text') {
          console.log(`Assistant: ${block.text}`);
        }
      }
    }
  }

  // Third turn - still has context
  console.log('\nUser: Add a docstring to it');
  await session.send('Add a module docstring to that file');

  for await (const message of session.receive()) {
    if (message.type === 'assistant') {
      for (const block of message.content) {
        if (block.type === 'text') {
          console.log(`Assistant: ${block.text}`);
        }
      }
    } else if (message.type === 'result') {
      console.log(`\nConversation completed in ${message.duration_ms}ms`);
    }
  }
}

/**
 * Example 3: One-Shot with unstable_v2_prompt()
 *
 * For simple queries that don't need multi-turn.
 * Returns result directly instead of streaming.
 */
async function oneShot(): Promise<void> {
  console.log('\n=== One-Shot Example ===\n');

  // Simple one-shot query
  const result = await unstable_v2_prompt(
    'What is the current working directory?',
    {
      model: 'haiku',  // Use Haiku for simple queries
      allowedTools: ['Bash']
    }
  );

  console.log('Question: What is the current working directory?');
  console.log(`Answer: ${result.text}`);
  console.log(`Duration: ${result.duration_ms}ms`);
}

/**
 * Example 4: Session Resume
 *
 * Create a session, save its ID, then resume it later.
 * Demonstrates memory persistence across sessions.
 */
async function sessionResume(): Promise<void> {
  console.log('\n=== Session Resume Example ===\n');

  let sessionId: string;

  // First session - establish context
  {
    await using session = unstable_v2_createSession({
      model: 'sonnet',
      allowedTools: ['Read', 'Write']
    });

    sessionId = session.id;
    console.log(`Created session: ${sessionId}`);

    // Establish some context
    await session.send('Remember this: my favorite color is blue');

    for await (const message of session.receive()) {
      if (message.type === 'assistant') {
        for (const block of message.content) {
          if (block.type === 'text') {
            console.log(`Assistant: ${block.text}`);
          }
        }
      }
    }
  }
  // Session closed here but state persisted

  console.log('\n--- Session closed, now resuming... ---\n');

  // Resume the session
  {
    await using session = unstable_v2_resumeSession(sessionId, {
      model: 'sonnet'
    });

    console.log(`Resumed session: ${session.id}`);

    // Test if context is retained
    await session.send('What is my favorite color?');

    for await (const message of session.receive()) {
      if (message.type === 'assistant') {
        for (const block of message.content) {
          if (block.type === 'text') {
            console.log(`Assistant: ${block.text}`);
          }
        }
      } else if (message.type === 'result') {
        console.log(`\nSession completed`);
      }
    }
  }
}

/**
 * Example 5: Session with Streaming Input
 *
 * Process messages as they arrive for real-time UI updates.
 */
async function streamingInput(): Promise<void> {
  console.log('\n=== Streaming Input Example ===\n');

  await using session = unstable_v2_createSession({
    model: 'sonnet',
    allowedTools: ['Read', 'Bash']
  });

  await session.send('Count from 1 to 5 slowly, explaining each number');

  // Process each message as it arrives
  for await (const message of session.receive()) {
    if (message.type === 'assistant') {
      for (const block of message.content) {
        if (block.type === 'text') {
          // In a real app, you'd update UI here
          process.stdout.write(block.text);
        } else if (block.type === 'tool_use') {
          console.log(`\n[Using tool: ${block.name}]`);
        }
      }
    } else if (message.type === 'tool_result') {
      console.log(`[Tool result received]`);
    } else if (message.type === 'result') {
      console.log(`\n\nCompleted in ${message.duration_ms}ms`);
    }
  }
}

// Main runner
async function main(): Promise<void> {
  const example = process.argv[2] || 'basic';

  switch (example) {
    case 'basic':
      await basicSession();
      break;
    case 'multi-turn':
      await multiTurnConversation();
      break;
    case 'one-shot':
      await oneShot();
      break;
    case 'resume':
      await sessionResume();
      break;
    case 'streaming':
      await streamingInput();
      break;
    default:
      console.log('Usage: npx tsx session-api-typescript.ts [basic|multi-turn|one-shot|resume|streaming]');
  }
}

main().catch(console.error);
