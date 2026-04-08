-- Run this SQL in your Supabase SQL Editor to create the boost_sessions table

CREATE TABLE IF NOT EXISTS public.boost_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID, -- Optional: links to auth.users if you use authentication
    memory_before INT4 NOT NULL,
    memory_after INT4 NOT NULL,
    apps_optimized INT4 NOT NULL,
    performance_score INT4 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Note: Depending on your RLS (Row Level Security) settings, you might need to insert an access policy
-- For development, you can momentarily allow anon/authenticated inserts:
-- ALTER TABLE public.boost_sessions ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow backend to insert boost sessions" ON public.boost_sessions FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow users to view their own sessions" ON public.boost_sessions FOR SELECT USING (true);
