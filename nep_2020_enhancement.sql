-- NEP 2020 Compliant Database Schema Enhancement
-- Add this to your existing schema for NEP 2020 compliance

-- Update programs table to support NEP 2020 structure
ALTER TABLE programs 
ADD COLUMN program_type VARCHAR(50) DEFAULT 'CBCS',
ADD COLUMN exit_options JSONB DEFAULT '["certificate", "diploma", "bachelor", "bachelor_research"]',
ADD COLUMN total_credits_required INTEGER DEFAULT 160,
ADD COLUMN major_credits INTEGER DEFAULT 80,
ADD COLUMN multidisciplinary_credits INTEGER DEFAULT 80;

-- Update subjects table for NEP 2020 course categories
ALTER TABLE subjects 
DROP COLUMN IF EXISTS subject_type,
ADD COLUMN course_category VARCHAR(50) DEFAULT 'major',
ADD COLUMN course_type VARCHAR(50) DEFAULT 'core',
ADD COLUMN nep_category VARCHAR(20) DEFAULT 'major',
ADD COLUMN is_skill_based BOOLEAN DEFAULT false,
ADD COLUMN is_research_component BOOLEAN DEFAULT false;

-- Create course categories table for NEP 2020
CREATE TABLE IF NOT EXISTS nep_course_categories (
    id SERIAL PRIMARY KEY,
    category_code VARCHAR(20) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    credit_requirements INTEGER DEFAULT 0,
    is_mandatory BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert NEP 2020 course categories
INSERT INTO nep_course_categories (category_code, category_name, description, credit_requirements, is_mandatory) VALUES
('MAJOR', 'Major Courses', 'Core subjects in the chosen discipline', 80, true),
('MINOR', 'Minor Courses', 'Secondary specialization subjects', 40, false),
('AEC', 'Ability Enhancement Courses', 'Communication and quantitative reasoning', 8, true),
('SEC', 'Skill Enhancement Courses', 'Employability and skill development', 12, true),
('VAC', 'Value Added Courses', 'Ethics, environmental science, etc.', 4, true),
('MDC', 'Multidisciplinary Courses', 'Interdisciplinary subjects', 16, true),
('OE', 'Open Electives', 'Any discipline electives', 12, false),
('PROJECT', 'Project/Research', 'Capstone project or research work', 8, false)
ON CONFLICT (category_code) DO NOTHING;

-- Create academic bank of credits table
CREATE TABLE IF NOT EXISTS abc_credits (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    subject_id INTEGER REFERENCES subjects(id),
    credits_earned INTEGER NOT NULL,
    grade VARCHAR(5),
    semester_completed VARCHAR(20),
    institution_id INTEGER REFERENCES institutions(id),
    is_transferred BOOLEAN DEFAULT false,
    transfer_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Update time slots to support flexible scheduling
ALTER TABLE time_slots 
ADD COLUMN slot_type VARCHAR(50) DEFAULT 'regular',
ADD COLUMN duration_minutes INTEGER DEFAULT 60,
ADD COLUMN is_lab_slot BOOLEAN DEFAULT false,
ADD COLUMN is_seminar_slot BOOLEAN DEFAULT false;

-- Create flexible semester structure
CREATE TABLE IF NOT EXISTS academic_years (
    id SERIAL PRIMARY KEY,
    year_code VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT false,
    total_semesters INTEGER DEFAULT 8,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sample data for NEP 2020 structure
INSERT INTO academic_years (year_code, start_date, end_date, is_current) VALUES
('2024-25', '2024-07-01', '2025-06-30', true);

-- Update existing subjects with NEP categories
UPDATE subjects SET 
    course_category = CASE 
        WHEN code LIKE '%101' THEN 'major'
        WHEN code LIKE 'ENG%' THEN 'aec'
        WHEN code LIKE 'SKILL%' THEN 'sec'
        ELSE 'major'
    END,
    nep_category = CASE 
        WHEN code LIKE '%101' THEN 'MAJOR'
        WHEN code LIKE 'ENG%' THEN 'AEC'
        WHEN code LIKE 'SKILL%' THEN 'SEC'
        ELSE 'MAJOR'
    END;

-- Verification query
SELECT 
    'Programs with NEP Structure' as table_info,
    COUNT(*) as count
FROM programs;

SELECT 
    nep_category,
    COUNT(*) as subject_count,
    SUM(credits) as total_credits
FROM subjects 
GROUP BY nep_category;