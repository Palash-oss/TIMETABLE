-- Sample data for testing the timetable system

-- Insert sample programs
INSERT INTO programs (name, code, type, duration_years, total_credits) VALUES
('Bachelor of Education', 'BED', 'B.Ed.', 2, 120),
('Master of Education', 'MED', 'M.Ed.', 2, 80),
('Four Year Undergraduate Program', 'FYUP', 'FYUP', 4, 160),
('Integrated Teacher Education Program', 'ITEP', 'ITEP', 4, 140);

-- Insert sample faculty
INSERT INTO faculty (employee_id, name, email, department, expertise, max_hours_per_week) VALUES
('FAC001', 'Dr. Sarah Johnson', 'sarah.johnson@university.edu', 'Education', ARRAY['Educational Psychology', 'Child Development'], 20),
('FAC002', 'Prof. Michael Brown', 'michael.brown@university.edu', 'Mathematics', ARRAY['Mathematics Pedagogy', 'Curriculum Design'], 18),
('FAC003', 'Dr. Emily Davis', 'emily.davis@university.edu', 'Science', ARRAY['Science Teaching', 'Research Methods'], 20),
('FAC004', 'Prof. James Wilson', 'james.wilson@university.edu', 'Languages', ARRAY['Language Teaching', 'Literature'], 16);

-- Insert sample rooms
INSERT INTO rooms (room_number, building, capacity, room_type, is_available) VALUES
('101', 'Main Building', 50, 'Classroom', true),
('102', 'Main Building', 45, 'Classroom', true),
('Lab1', 'Science Block', 30, 'Lab', true),
('Lab2', 'Computer Block', 25, 'Lab', true),
('Hall1', 'Administrative Block', 100, 'Seminar Hall', true);

-- Insert sample time slots
INSERT INTO time_slots (day_of_week, start_time, end_time, slot_type) VALUES
(1, '09:00:00', '10:00:00', 'Theory'),
(1, '10:00:00', '11:00:00', 'Theory'),
(1, '11:00:00', '12:00:00', 'Theory'),
(1, '14:00:00', '15:00:00', 'Theory'),
(1, '15:00:00', '16:00:00', 'Practical'),
(2, '09:00:00', '10:00:00', 'Theory'),
(2, '10:00:00', '11:00:00', 'Theory'),
(2, '11:00:00', '12:00:00', 'Theory');

-- Insert sample courses (for B.Ed. program)
INSERT INTO courses (code, name, program_id, semester, credits, theory_hours, practical_hours, course_type) 
SELECT 
    'EDP101', 'Educational Psychology', p.id, 1, 4, 3, 1, 'Core'
FROM programs p WHERE p.code = 'BED'
UNION ALL
SELECT 
    'TM101', 'Teaching Methods', p.id, 1, 4, 3, 1, 'Core'
FROM programs p WHERE p.code = 'BED'
UNION ALL
SELECT 
    'CD101', 'Curriculum Design', p.id, 1, 3, 3, 0, 'Core'
FROM programs p WHERE p.code = 'BED';

-- Note: Run this AFTER creating the schema with database_schema.sql