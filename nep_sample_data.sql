-- NEP 2020 Sample Data Setup
-- Run this after the enhancement script to populate with NEP-compliant sample data

-- Update existing subjects with NEP categories
UPDATE subjects SET 
    nep_category = 'MAJOR',
    course_category = 'major',
    course_type = 'core'
WHERE code = 'CS101';

UPDATE subjects SET 
    nep_category = 'MAJOR',
    course_category = 'major', 
    course_type = 'core'
WHERE code = 'MATH101';

UPDATE subjects SET 
    nep_category = 'MAJOR',
    course_category = 'major',
    course_type = 'core' 
WHERE code = 'PHY101';

UPDATE subjects SET 
    nep_category = 'AEC',
    course_category = 'ability_enhancement',
    course_type = 'core',
    is_skill_based = true
WHERE code = 'ENG101';

-- Add more NEP 2020 compliant subjects
INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Environmental Science', 'EVS101', 2, 'VAC', 'value_added', false, 2
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 1
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Digital Literacy', 'DL101', 3, 'SEC', 'skill_enhancement', true, 3
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 1
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Psychology of Learning', 'PSY101', 3, 'MDC', 'multidisciplinary', false, 3
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 1
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Entrepreneurship', 'ENT101', 2, 'SEC', 'skill_enhancement', true, 2
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 1
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Indian Knowledge Systems', 'IKS101', 2, 'MDC', 'multidisciplinary', false, 2
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 1
ON CONFLICT (semester_id, code) DO NOTHING;

-- Update program to be NEP 2020 compliant
UPDATE programs SET 
    duration_semesters = 8,
    program_type = 'CBCS',
    total_credits_required = 160,
    major_credits = 80,
    multidisciplinary_credits = 80
WHERE code = 'CS';

-- Add second semester with more NEP subjects
INSERT INTO semesters (program_id, semester_number, name, is_active)
SELECT p.id, 2, 'Semester 2', true
FROM programs p 
WHERE p.code = 'CS'
ON CONFLICT (program_id, semester_number) DO NOTHING;

-- Add subjects for semester 2
INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Object Oriented Programming', 'CS201', 4, 'MAJOR', 'major', true, 4
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 2
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Mathematics II', 'MATH201', 4, 'MAJOR', 'major', false, 4
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 2
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Data Analytics', 'DA201', 3, 'SEC', 'skill_enhancement', true, 3
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 2
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Philosophy and Ethics', 'PHI201', 3, 'VAC', 'value_added', false, 3
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 2
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Economics for Engineers', 'ECO201', 3, 'MDC', 'multidisciplinary', false, 3
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 2
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Technical Communication', 'TC201', 2, 'AEC', 'ability_enhancement', true, 2
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 2
ON CONFLICT (semester_id, code) DO NOTHING;

INSERT INTO subjects (semester_id, name, code, credits, nep_category, course_category, is_skill_based, hours_per_week)
SELECT s.id, 'Open Elective - Art Appreciation', 'ART201', 2, 'OE', 'open_elective', false, 2
FROM semesters s 
JOIN programs p ON s.program_id = p.id
WHERE p.code = 'CS' AND s.semester_number = 2
ON CONFLICT (semester_id, code) DO NOTHING;

-- Create subject-teacher assignments for new subjects
INSERT INTO subject_teacher_assignments (subject_id, teacher_id, hours_per_week)
SELECT sub.id, t.id, sub.hours_per_week
FROM subjects sub 
CROSS JOIN teachers t
WHERE sub.code IN ('EVS101', 'DL101', 'PSY101', 'ENT101', 'IKS101')
AND NOT EXISTS (
    SELECT 1 FROM subject_teacher_assignments sta 
    WHERE sta.subject_id = sub.id AND sta.teacher_id = t.id
)
LIMIT 5;

-- Verification - show NEP 2020 compliance
SELECT 
    'NEP 2020 Compliance Report' as report_title,
    p.name as program_name,
    s.semester_number,
    COUNT(sub.id) as total_subjects,
    SUM(sub.credits) as total_credits,
    COUNT(CASE WHEN sub.nep_category = 'MAJOR' THEN 1 END) as major_courses,
    COUNT(CASE WHEN sub.nep_category = 'AEC' THEN 1 END) as aec_courses,
    COUNT(CASE WHEN sub.nep_category = 'SEC' THEN 1 END) as sec_courses,
    COUNT(CASE WHEN sub.nep_category = 'VAC' THEN 1 END) as vac_courses,
    COUNT(CASE WHEN sub.nep_category = 'MDC' THEN 1 END) as mdc_courses,
    COUNT(CASE WHEN sub.is_skill_based = true THEN 1 END) as skill_based_courses
FROM programs p
JOIN semesters s ON p.id = s.program_id  
JOIN subjects sub ON s.id = sub.semester_id
WHERE p.code = 'CS'
GROUP BY p.name, s.semester_number
ORDER BY s.semester_number;

-- Credit distribution by NEP category
SELECT 
    sub.nep_category,
    COUNT(*) as course_count,
    SUM(sub.credits) as total_credits,
    ROUND(AVG(sub.credits::numeric), 2) as avg_credits_per_course
FROM subjects sub
JOIN semesters s ON sub.semester_id = s.id
JOIN programs p ON s.program_id = p.id  
WHERE p.code = 'CS'
GROUP BY sub.nep_category
ORDER BY total_credits DESC;