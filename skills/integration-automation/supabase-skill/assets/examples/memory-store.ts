/**
 * Memory Persistence Example
 * Pattern: Dual persistence (soul memory + process memory)
 */

import { getSupabaseClient } from './supabase-client';

export interface SoulMemoryRow {
  id: string;
  session_id: string;
  key: string;
  value: any;
  updated_at: string;
}

export interface ProcessMemoryRow {
  id: string;
  session_id: string;
  process_name: string;
  key: string;
  value: any;
  updated_at: string;
}

/**
 * Save soul memory (persistent across process transitions)
 * Uses upsert to insert or update atomically
 */
export async function saveSoulMemory(
  sessionId: string,
  key: string,
  value: any
): Promise<SoulMemoryRow> {
  const supabase = getSupabaseClient();

  const { data, error } = await supabase
    .from('soul_memories')
    .upsert(
      {
        session_id: sessionId,
        key,
        value,
        updated_at: new Date().toISOString(),
      },
      { onConflict: 'session_id,key' }
    )
    .select()
    .single();

  if (error) {
    throw new Error(`Failed to save soul memory '${key}': ${error.message}`);
  }

  return data as SoulMemoryRow;
}

/**
 * Load all soul memories for a session
 * Returns key-value map for easy access
 */
export async function loadSoulMemories(
  sessionId: string
): Promise<Record<string, any>> {
  const supabase = getSupabaseClient();

  const { data, error } = await supabase
    .from('soul_memories')
    .select('*')
    .eq('session_id', sessionId);

  if (error) {
    throw new Error(`Failed to load soul memories: ${error.message}`);
  }

  const map: Record<string, any> = {};
  for (const row of (data || []) as SoulMemoryRow[]) {
    map[row.key] = row.value;
  }

  return map;
}

/**
 * Load specific soul memory key
 * Returns undefined if key doesn't exist
 */
export async function loadSoulMemoryKey(
  sessionId: string,
  key: string
): Promise<any | undefined> {
  const supabase = getSupabaseClient();

  const { data, error } = await supabase
    .from('soul_memories')
    .select('value')
    .eq('session_id', sessionId)
    .eq('key', key)
    .single();

  // PGRST116 = no rows - not an error
  if (error && error.code !== 'PGRST116') {
    throw new Error(`Failed to load soul memory '${key}': ${error.message}`);
  }

  return (data as any)?.value;
}

/**
 * Save process memory (ephemeral, cleared on process transition)
 * Scoped by session + process name
 */
export async function saveProcessMemory(
  sessionId: string,
  processName: string,
  key: string,
  value: any
): Promise<ProcessMemoryRow> {
  const supabase = getSupabaseClient();

  const { data, error } = await supabase
    .from('process_memories')
    .upsert(
      {
        session_id: sessionId,
        process_name: processName,
        key,
        value,
        updated_at: new Date().toISOString(),
      },
      { onConflict: 'session_id,process_name,key' }
    )
    .select()
    .single();

  if (error) {
    throw new Error(
      `Failed to save process memory '${processName}:${key}': ${error.message}`
    );
  }

  return data as ProcessMemoryRow;
}

/**
 * Load all process memories for a session
 */
export async function loadProcessMemories(
  sessionId: string
): Promise<ProcessMemoryRow[]> {
  const supabase = getSupabaseClient();

  const { data, error } = await supabase
    .from('process_memories')
    .select('*')
    .eq('session_id', sessionId);

  if (error) {
    throw new Error(`Failed to load process memories: ${error.message}`);
  }

  return (data || []) as ProcessMemoryRow[];
}
