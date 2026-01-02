/**
 * Supabase Client Initialization Example
 * Pattern: Singleton with lazy initialization for server-side Next.js
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';

let supabaseClient: SupabaseClient | null = null;

/**
 * Get or create Supabase client instance
 * Uses singleton pattern to reuse client across requests
 */
export function getSupabaseClient(): SupabaseClient {
  if (!supabaseClient) {
    // Validate environment variables
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;

    if (!supabaseUrl || !supabaseServiceKey) {
      throw new Error('Missing Supabase environment variables');
    }

    // Create client with server-side configuration
    supabaseClient = createClient(supabaseUrl, supabaseServiceKey, {
      auth: {
        autoRefreshToken: false,  // Server-side: no token refresh
        persistSession: false,     // Server-side: no session storage
      },
    });
  }

  return supabaseClient;
}

// Export singleton instance
export const supabase = getSupabaseClient();
