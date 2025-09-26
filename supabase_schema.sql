-- Timetable Generator Database Schema
-- Copy and paste this entire script into Supabase SQL Editor

-- Drop existing tables if they exist (optional - remove this section if you want to keep existing data)
-- DROP TABLE IF EXISTS timetable_entries CASCADE;
-- DROP TABLE IF EXISTS timetables CASCADE;
-- DROP TABLE IF EXISTS subject_teacher_assignments CASCADE;
-- DROP TABLE IF EXISTS time_slots CASCADE;
-- DROP TABLE IF EXISTS classrooms CASCADE;
-- DROP TABLE IF EXISTS teachers CASCADE;
-- DROP TABLE IF EXISTS subjects CASCADE;
-- DROP TABLE IF EXISTS semesters CASCADE;
-- DROP TABLE IF EXISTS programs CASCADE;
-- DROP TABLE IF EXISTS institutions CASCADE;

-- 1. Create institutions table
CREATE TABLE IF NOT EXISTS institutions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    contact_info JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create programs table
CREATE TABLE IF NOT EXISTS programs (
    id SERIAL PRIMARY KEY,
    institution_id INTEGER REFERENCES institutions(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    duration_semesters INTEGER NOT NULL DEFAULT 8,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create semesters table
CREATE TABLE IF NOT EXISTS semesters (
    id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
    semester_number INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(program_id, semester_number)
);

-- 4. Create subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    semester_id INTEGER REFERENCES semesters(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    credits INTEGER DEFAULT 3,
    subject_type VARCHAR(50) DEFAULT 'core',
    hours_per_week INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(semester_id, code)
);

-- 5. Create teachers table
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    institution_id INTEGER REFERENCES institutions(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    employee_id VARCHAR(100) UNIQUE,
    department VARCHAR(100),
    specialization VARCHAR(255),
    max_hours_per_week INTEGER DEFAULT 20,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Create classrooms table
CREATE TABLE IF NOT EXISTS classrooms (
    id SERIAL PRIMARY KEY,
    institution_id INTEGER REFERENCES institutions(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 50,
    room_type VARCHAR(50) DEFAULT 'lecture',
    facilities JSONB DEFAULT '[]',
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(institution_id, name)
);

-- 7. Create time_slots table
CREATE TABLE IF NOT EXISTS time_slots (
    id SERIAL PRIMARY KEY,
    institution_id INTEGER REFERENCES institutions(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(institution_id, day_of_week, start_time, end_time)
);

-- 8. Create subject_teacher_assignments table
CREATE TABLE IF NOT EXISTS subject_teacher_assignments (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    teacher_id INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
    hours_per_week INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(subject_id, teacher_id)
);

-- 9. Create timetables table
CREATE TABLE IF NOT EXISTS timetables (
    id SERIAL PRIMARY KEY,
    semester_id INTEGER REFERENCES semesters(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    generated_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. Create timetable_entries table
CREATE TABLE IF NOT EXISTS timetable_entries (
    id SERIAL PRIMARY KEY,
    timetable_id INTEGER REFERENCES timetables(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    teacher_id INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
    classroom_id INTEGER REFERENCES classrooms(id) ON DELETE CASCADE,
    time_slot_id INTEGER REFERENCES time_slots(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    entry_type VARCHAR(50) DEFAULT 'lecture',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_programs_institution ON programs(institution_id);
CREATE INDEX IF NOT EXISTS idx_semesters_program ON semesters(program_id);
CREATE INDEX IF NOT EXISTS idx_subjects_semester ON subjects(semester_id);
CREATE INDEX IF NOT EXISTS idx_teachers_institution ON teachers(institution_id);
CREATE INDEX IF NOT EXISTS idx_classrooms_institution ON classrooms(institution_id);
CREATE INDEX IF NOT EXISTS idx_time_slots_institution ON time_slots(institution_id);
CREATE INDEX IF NOT EXISTS idx_timetable_entries_timetable ON timetable_entries(timetable_id);
CREATE INDEX IF NOT EXISTS idx_timetable_entries_day_time ON timetable_entries(day_of_week, start_time);

-- Insert sample data
INSERT INTO institutions (name, address, contact_info) 
VALUES ('Sample University', '123 Education Street, Academic City', '{"phone": "+1234567890", "email": "admin@university.edu", "website": "www.university.edu"}')
ON CONFLICT DO NOTHING;

-- Insert sample program
INSERT INTO programs (institution_id, name, code, duration_semesters)
SELECT i.id, 'Computer Science', 'CS', 8
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (code) DO NOTHING;

-- Insert sample semester
INSERT INTO semesters (program_id, semester_number, name, is_active)
SELECT p.id, 1, 'Semester 1', true
FROM programs p 
WHERE p.code = 'CS'
ON CONFLICT (program_id, semester_number) DO NOTHING;

-- Insert sample subjects
INSERT INTO subjects (semester_id, name, code, credits, hours_per_week)
SELECT s.id, 'Introduction to Programming', 'CS101', 4, 4
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 1
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, hours_per_week)
SELECT s.id, 'Mathematics I', 'MATH101', 3, 3
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 1
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, hours_per_week)
SELECT s.id, 'Physics I', 'PHY101', 3, 3
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 1
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, hours_per_week)
SELECT s.id, 'English Communication', 'ENG101', 2, 2
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 1
ON CONFLICT (semester_id, code) DO NOTHING;

-- Insert sample teachers
INSERT INTO teachers (institution_id, name, email, employee_id, department, specialization)
SELECT i.id, 'Dr. John Smith', 'john.smith@university.edu', 'EMP001', 'Computer Science', 'Programming Languages'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (email) DO NOTHING;

INSERT INTO teachers (institution_id, name, email, employee_id, department, specialization)
SELECT i.id, 'Dr. Jane Wilson', 'jane.wilson@university.edu', 'EMP002', 'Mathematics', 'Applied Mathematics'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (email) DO NOTHING;

INSERT INTO teachers (institution_id, name, email, employee_id, department, specialization)
SELECT i.id, 'Dr. Mike Johnson', 'mike.johnson@university.edu', 'EMP003', 'Physics', 'Quantum Physics'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (email) DO NOTHING;

INSERT INTO teachers (institution_id, name, email, employee_id, department, specialization)
SELECT i.id, 'Prof. Sarah Brown', 'sarah.brown@university.edu', 'EMP004', 'English', 'Communication Skills'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (email) DO NOTHING;

-- Insert sample classrooms
INSERT INTO classrooms (institution_id, name, capacity, room_type)
SELECT i.id, 'Room A101', 60, 'lecture'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, name) DO NOTHING;

INSERT INTO classrooms (institution_id, name, capacity, room_type)
SELECT i.id, 'Room A102', 50, 'lecture'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, name) DO NOTHING;

INSERT INTO classrooms (institution_id, name, capacity, room_type)
SELECT i.id, 'Lab B201', 30, 'lab'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, name) DO NOTHING;

-- Insert time slots for weekdays (Monday=0 to Friday=4)
INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, 0, '09:00', '10:00', 'Period 1 - Monday'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, 0, '10:00', '11:00', 'Period 2 - Monday'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, 0, '11:00', '12:00', 'Period 3 - Monday'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, 0, '14:00', '15:00', 'Period 4 - Monday'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

-- Add similar time slots for Tuesday (day_of_week = 1)
INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, 1, '09:00', '10:00', 'Period 1 - Tuesday'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, 1, '10:00', '11:00', 'Period 2 - Tuesday'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, 1, '11:00', '12:00', 'Period 3 - Tuesday'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, 1, '14:00', '15:00', 'Period 4 - Tuesday'
FROM institutions i 
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

-- Add Wednesday, Thursday, Friday time slots (day_of_week = 2, 3, 4)
INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, day_num, '09:00', '10:00', 'Period 1 - ' || 
    CASE day_num 
        WHEN 2 THEN 'Wednesday'
        WHEN 3 THEN 'Thursday' 
        WHEN 4 THEN 'Friday'
    END
FROM institutions i 
CROSS JOIN (SELECT unnest(ARRAY[2,3,4]) as day_num) days
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, day_num, '10:00', '11:00', 'Period 2 - ' || 
    CASE day_num 
        WHEN 2 THEN 'Wednesday'
        WHEN 3 THEN 'Thursday' 
        WHEN 4 THEN 'Friday'
    END
FROM institutions i 
CROSS JOIN (SELECT unnest(ARRAY[2,3,4]) as day_num) days
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, day_num, '11:00', '12:00', 'Period 3 - ' || 
    CASE day_num 
        WHEN 2 THEN 'Wednesday'
        WHEN 3 THEN 'Thursday' 
        WHEN 4 THEN 'Friday'
    END
FROM institutions i 
CROSS JOIN (SELECT unnest(ARRAY[2,3,4]) as day_num) days
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name)
SELECT i.id, day_num, '14:00', '15:00', 'Period 4 - ' || 
    CASE day_num 
        WHEN 2 THEN 'Wednesday'
        WHEN 3 THEN 'Thursday' 
        WHEN 4 THEN 'Friday'
    END
FROM institutions i 
CROSS JOIN (SELECT unnest(ARRAY[2,3,4]) as day_num) days
WHERE i.name = 'Sample University'
ON CONFLICT (institution_id, day_of_week, start_time, end_time) DO NOTHING;

-- Create subject-teacher assignments
INSERT INTO subject_teacher_assignments (subject_id, teacher_id, hours_per_week)
SELECT sub.id, t.id, 4
FROM subjects sub 
JOIN teachers t ON t.employee_id = 'EMP001'
WHERE sub.code = 'CS101'
ON CONFLICT (subject_id, teacher_id) DO NOTHING;

INSERT INTO subject_teacher_assignments (subject_id, teacher_id, hours_per_week)
SELECT sub.id, t.id, 3
FROM subjects sub 
JOIN teachers t ON t.employee_id = 'EMP002'
WHERE sub.code = 'MATH101'
ON CONFLICT (subject_id, teacher_id) DO NOTHING;

INSERT INTO subject_teacher_assignments (subject_id, teacher_id, hours_per_week)
SELECT sub.id, t.id, 3
FROM subjects sub 
JOIN teachers t ON t.employee_id = 'EMP003'
WHERE sub.code = 'PHY101'
ON CONFLICT (subject_id, teacher_id) DO NOTHING;

INSERT INTO subject_teacher_assignments (subject_id, teacher_id, hours_per_week)
SELECT sub.id, t.id, 2
FROM subjects sub 
JOIN teachers t ON t.employee_id = 'EMP004'
WHERE sub.code = 'ENG101'
ON CONFLICT (subject_id, teacher_id) DO NOTHING;

-- Verification queries (these will show the data that was inserted)
SELECT 'Institutions' as table_name, COUNT(*) as record_count FROM institutions
UNION ALL
SELECT 'Programs', COUNT(*) FROM programs
UNION ALL
SELECT 'Semesters', COUNT(*) FROM semesters
UNION ALL
SELECT 'Subjects', COUNT(*) FROM subjects
UNION ALL
SELECT 'Teachers', COUNT(*) FROM teachers
UNION ALL
SELECT 'Classrooms', COUNT(*) FROM classrooms
UNION ALL
SELECT 'Time Slots', COUNT(*) FROM time_slots
UNION ALL
SELECT 'Subject-Teacher Assignments', COUNT(*) FROM subject_teacher_assignments;