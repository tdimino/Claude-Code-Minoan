/**
 * Session Management Example
 * Pattern: Load-or-create with timeout handling
 */

import { getSupabaseClient } from './supabase-client';

export interface UserSession {
  id: string;
  phone_number: string;
  assigned_persona: string;
  first_contact_at: string;
  last_active_at: string;
  total_messages: number;
  metadata: Record<string, any>;
  __isNewSession?: boolean;
}

const SESSION_TIMEOUT_MS = 60 * 60 * 1000; // 1 hour

/**
 * Load existing session or create new one
 * Implements timeout logic to reset state after inactivity
 */
export async function loadOrCreateSession(
  phoneNumber: string
): Promise<UserSession> {
  const supabase = getSupabaseClient();
  const now = new Date();
  const nowIso = now.toISOString();

  // Try to find existing session
  const { data: existing, error: fetchError } = await supabase
    .from('user_sessions')
    .select('*')
    .eq('phone_number', phoneNumber)
    .single();

  // PGRST116 = "no rows returned" - not an error
  if (fetchError && fetchError.code !== 'PGRST116') {
    throw new Error(`Failed to load session: ${fetchError.message}`);
  }

  if (existing) {
    // Check for timeout
    const lastUserMessage = await getLastUserMessageTimestamp(
      supabase,
      existing.id
    );

    const timeSinceUserMessage = lastUserMessage
      ? now.getTime() - lastUserMessage.getTime()
      : 0;

    const shouldIncrement = lastUserMessage
      ? timeSinceUserMessage >= SESSION_TIMEOUT_MS
      : false;

    // Update session
    const currentNumber = coerceSessionNumber(existing.metadata);
    const nextSessionNumber = shouldIncrement
      ? currentNumber + 1
      : currentNumber;

    const metadata = {
      ...existing.metadata,
      session_number: nextSessionNumber,
      last_session_started_at: shouldIncrement
        ? nowIso
        : existing.metadata.last_session_started_at,
    };

    await supabase
      .from('user_sessions')
      .update({ last_active_at: nowIso, metadata })
      .eq('id', existing.id);

    // Reset ephemeral state on timeout
    if (shouldIncrement) {
      await Promise.all([
        supabase.from('process_memories').delete().eq('session_id', existing.id),
        supabase.from('mental_process_state').delete().eq('session_id', existing.id),
      ]);
    }

    return {
      ...existing,
      metadata,
      last_active_at: nowIso,
      __isNewSession: false,
    };
  }

  // Create new session
  const { data: newSession, error: insertError } = await supabase
    .from('user_sessions')
    .insert({
      phone_number: phoneNumber,
      assigned_persona: 'default',
      total_messages: 0,
      metadata: { session_number: 1, last_session_started_at: nowIso },
    })
    .select()
    .single();

  if (insertError) {
    throw new Error(`Failed to create session: ${insertError.message}`);
  }

  return {
    ...newSession,
    __isNewSession: true,
  } as UserSession;
}

// Helper functions
async function getLastUserMessageTimestamp(
  supabase: any,
  sessionId: string
): Promise<Date | null> {
  const { data, error } = await supabase
    .from('messages')
    .select('created_at')
    .eq('session_id', sessionId)
    .eq('role', 'user')
    .order('created_at', { ascending: false })
    .limit(1);

  if (error) {
    console.warn('Failed to load last user message timestamp', error);
    return null;
  }

  const raw = data?.[0]?.created_at;
  if (!raw) return null;

  const parsed = new Date(raw);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function coerceSessionNumber(metadata: Record<string, any> | null | undefined): number {
  const value = metadata?.session_number;
  if (typeof value === 'number' && Number.isFinite(value) && value >= 1) {
    return Math.floor(value);
  }
  return 1;
}
