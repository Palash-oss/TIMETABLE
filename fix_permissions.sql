-- Enable Row Level Security and set permissions for your tables
-- Run this in Supabase SQL Editor

-- Disable RLS for development (you can enable it later for production)
ALTER TABLE institutions DISABLE ROW LEVEL SECURITY;
ALTER TABLE programs DISABLE ROW LEVEL SECURITY;
ALTER TABLE semesters DISABLE ROW LEVEL SECURITY;
ALTER TABLE subjects DISABLE ROW LEVEL SECURITY;
ALTER TABLE teachers DISABLE ROW LEVEL SECURITY;
ALTER TABLE classrooms DISABLE ROW LEVEL SECURITY;
ALTER TABLE time_slots DISABLE ROW LEVEL SECURITY;
ALTER TABLE subject_teacher_assignments DISABLE ROW LEVEL SECURITY;
ALTER TABLE timetables DISABLE ROW LEVEL SECURITY;
ALTER TABLE timetable_entries DISABLE ROW LEVEL SECURITY;

-- Grant permissions to anon role (your API key role)
GRANT ALL ON institutions TO anon;
GRANT ALL ON programs TO anon;
GRANT ALL ON semesters TO anon;
GRANT ALL ON subjects TO anon;
GRANT ALL ON teachers TO anon;
GRANT ALL ON classrooms TO anon;
GRANT ALL ON time_slots TO anon;
GRANT ALL ON subject_teacher_assignments TO anon;
GRANT ALL ON timetables TO anon;
GRANT ALL ON timetable_entries TO anon;

-- Grant permissions to authenticated role
GRANT ALL ON institutions TO authenticated;
GRANT ALL ON programs TO authenticated;
GRANT ALL ON semesters TO authenticated;
GRANT ALL ON subjects TO authenticated;
GRANT ALL ON teachers TO authenticated;
GRANT ALL ON classrooms TO authenticated;
GRANT ALL ON time_slots TO authenticated;
GRANT ALL ON subject_teacher_assignments TO authenticated;
GRANT ALL ON timetables TO authenticated;
GRANT ALL ON timetable_entries TO authenticated;

-- Grant usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;