-- Comprehensive permission fix for Supabase
-- Run this in Supabase SQL Editor

-- First, grant schema permissions
GRANT USAGE ON SCHEMA public TO anon;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT CREATE ON SCHEMA public TO anon;
GRANT CREATE ON SCHEMA public TO authenticated;

-- Grant all privileges on existing tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO authenticated;

-- Grant all privileges on existing sequences
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Grant all privileges on existing functions
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO anon;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO authenticated;

-- Disable RLS on all tables
ALTER TABLE IF EXISTS institutions DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS programs DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS semesters DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS subjects DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS teachers DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS classrooms DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS time_slots DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS subject_teacher_assignments DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS timetables DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS timetable_entries DISABLE ROW LEVEL SECURITY;

-- Verify permissions (this will show current permissions)
SELECT 
    schemaname,
    tablename,
    tableowner,
    hasindexes,
    hasrules,
    hastriggers
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- Alternative permission check
SELECT 
    table_name,
    privilege_type,
    grantee
FROM information_schema.table_privileges 
WHERE table_schema = 'public' 
ORDER BY table_name, grantee;