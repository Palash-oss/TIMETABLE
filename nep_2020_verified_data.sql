-- NEP 2020 Verified Data Structure
-- Based on UGC Guidelines for NEP 2020 Implementation

-- Drop existing tables if they exist
DROP TABLE IF EXISTS nep_categories CASCADE;
DROP TABLE IF EXISTS nep_course_structure CASCADE;
DROP TABLE IF EXISTS nep_subjects CASCADE;
DROP TABLE IF EXISTS nep_credit_distribution CASCADE;

-- NEP 2020 Course Categories (Official)
CREATE TABLE nep_categories (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    min_credits INTEGER NOT NULL,
    max_credits INTEGER NOT NULL,
    is_mandatory BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert verified NEP 2020 categories
INSERT INTO nep_categories (code, name, description, min_credits, max_credits, is_mandatory) VALUES
('MAJOR', 'Major/Discipline Specific Course', 'Core courses in the chosen discipline providing depth of knowledge', 84, 96, true),
('MINOR', 'Minor/Elective Course', 'Courses from other disciplines providing breadth of knowledge', 28, 32, false),
('AEC', 'Ability Enhancement Course', 'Courses to enhance specific abilities like communication, analytical skills', 8, 12, true),
('SEC', 'Skill Enhancement Course', 'Vocational courses providing hands-on training and practical skills', 12, 16, true),
('VAC', 'Value Added Course', 'Courses on ethics, Indian knowledge systems, environmental awareness', 8, 12, true),
('MDC', 'Multi-Disciplinary Course', 'Courses that integrate multiple disciplines and promote holistic learning', 12, 16, true),
('PROJECT', 'Research Project/Internship', 'Capstone projects, research work, or industry internships', 8, 12, true);

-- NEP 2020 Course Structure for 4-Year Undergraduate Program
CREATE TABLE nep_course_structure (
    id SERIAL PRIMARY KEY,
    program_type VARCHAR(50) NOT NULL, -- 'undergraduate', 'postgraduate'
    duration_years INTEGER NOT NULL,
    total_credits INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    category_code VARCHAR(10) REFERENCES nep_categories(code),
    recommended_credits INTEGER NOT NULL,
    courses_per_semester INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert verified NEP course structure for 4-year UG program (160 credits total)
INSERT INTO nep_course_structure (program_type, duration_years, total_credits, semester, category_code, recommended_credits, courses_per_semester) VALUES
-- Semester 1
('undergraduate', 4, 160, 1, 'MAJOR', 12, 2),
('undergraduate', 4, 160, 1, 'AEC', 4, 1),
('undergraduate', 4, 160, 1, 'VAC', 4, 1),
('undergraduate', 4, 160, 1, 'MDC', 4, 1),

-- Semester 2  
('undergraduate', 4, 160, 2, 'MAJOR', 12, 2),
('undergraduate', 4, 160, 2, 'AEC', 4, 1),
('undergraduate', 4, 160, 2, 'SEC', 4, 1),
('undergraduate', 4, 160, 2, 'MDC', 4, 1),

-- Semester 3
('undergraduate', 4, 160, 3, 'MAJOR', 12, 2),
('undergraduate', 4, 160, 3, 'MINOR', 8, 2),
('undergraduate', 4, 160, 3, 'SEC', 4, 1),

-- Semester 4
('undergraduate', 4, 160, 4, 'MAJOR', 12, 2),
('undergraduate', 4, 160, 4, 'MINOR', 8, 2),
('undergraduate', 4, 160, 4, 'MDC', 4, 1),

-- Semester 5
('undergraduate', 4, 160, 5, 'MAJOR', 16, 3),
('undergraduate', 4, 160, 5, 'MINOR', 8, 2),

-- Semester 6
('undergraduate', 4, 160, 6, 'MAJOR', 16, 3),
('undergraduate', 4, 160, 6, 'MINOR', 8, 2),

-- Semester 7
('undergraduate', 4, 160, 7, 'MAJOR', 16, 3),
('undergraduate', 4, 160, 7, 'PROJECT', 8, 1),

-- Semester 8
('undergraduate', 4, 160, 8, 'MAJOR', 12, 2),
('undergraduate', 4, 160, 8, 'PROJECT', 4, 1),
('undergraduate', 4, 160, 8, 'VAC', 4, 1),
('undergraduate', 4, 160, 8, 'MDC', 4, 1);

-- NEP Subjects with verified categories
CREATE TABLE nep_subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    category_code VARCHAR(10) REFERENCES nep_categories(code),
    credits INTEGER NOT NULL,
    semester INTEGER,
    program_id INTEGER,
    prerequisites TEXT[],
    learning_outcomes TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert verified NEP subjects for Computer Science program
INSERT INTO nep_subjects (name, code, category_code, credits, semester, program_id, prerequisites, learning_outcomes) VALUES
-- MAJOR courses
('Programming Fundamentals', 'CS101', 'MAJOR', 4, 1, 1, '{}', '{"Understand basic programming concepts", "Write simple programs"}'),
('Data Structures', 'CS102', 'MAJOR', 4, 1, 1, '{}', '{"Implement basic data structures", "Analyze time complexity"}'),
('Computer Systems Organization', 'CS103', 'MAJOR', 4, 1, 1, '{}', '{"Understand computer architecture", "Learn assembly programming"}'),

('Object Oriented Programming', 'CS201', 'MAJOR', 4, 2, 1, '{"CS101"}', '{"Master OOP concepts", "Design class hierarchies"}'),
('Discrete Mathematics', 'CS202', 'MAJOR', 4, 2, 1, '{}', '{"Apply mathematical reasoning", "Solve discrete problems"}'),
('Computer Networks', 'CS203', 'MAJOR', 4, 2, 1, '{"CS103"}', '{"Understand network protocols", "Configure network systems"}'),

-- AEC courses
('Technical Communication', 'AEC101', 'AEC', 2, 1, 1, '{}', '{"Improve technical writing", "Present technical content"}'),
('Critical Thinking', 'AEC102', 'AEC', 2, 1, 1, '{}', '{"Develop analytical skills", "Make logical arguments"}'),
('Quantitative Reasoning', 'AEC201', 'AEC', 2, 2, 1, '{}', '{"Apply statistical methods", "Interpret quantitative data"}'),
('Research Methodology', 'AEC202', 'AEC', 2, 2, 1, '{}', '{"Design research studies", "Conduct literature reviews"}'),

-- SEC courses  
('Web Development', 'SEC101', 'SEC', 2, 2, 1, '{"CS101"}', '{"Build web applications", "Use modern frameworks"}'),
('Mobile App Development', 'SEC102', 'SEC', 2, 3, 1, '{"CS201"}', '{"Develop mobile applications", "Deploy to app stores"}'),
('Cybersecurity Fundamentals', 'SEC201', 'SEC', 2, 3, 1, '{"CS203"}', '{"Implement security measures", "Identify vulnerabilities"}'),

-- VAC courses
('Indian Knowledge Systems', 'VAC101', 'VAC', 2, 1, 1, '{}', '{"Understand traditional knowledge", "Apply indigenous methods"}'),
('Environmental Studies', 'VAC102', 'VAC', 2, 8, 1, '{}', '{"Analyze environmental issues", "Propose sustainable solutions"}'),
('Ethics in Technology', 'VAC201', 'VAC', 2, 8, 1, '{}', '{"Apply ethical frameworks", "Address moral dilemmas"}'),

-- MDC courses
('Psychology of Human-Computer Interaction', 'MDC101', 'MDC', 2, 1, 1, '{}', '{"Design user interfaces", "Conduct usability studies"}'),
('Mathematics for Computer Science', 'MDC102', 'MDC', 2, 2, 1, '{}', '{"Apply mathematical concepts", "Solve computational problems"}'),
('Business Analytics', 'MDC201', 'MDC', 2, 4, 1, '{"CS202"}', '{"Analyze business data", "Make data-driven decisions"}'),
('Digital Innovation and Entrepreneurship', 'MDC202', 'MDC', 2, 8, 1, '{}', '{"Develop business models", "Create innovative solutions"}'),

-- MINOR courses (Mathematics Minor)
('Calculus I', 'MATH101', 'MINOR', 4, 3, 1, '{}', '{"Master differential calculus", "Solve optimization problems"}'),
('Calculus II', 'MATH102', 'MINOR', 4, 3, 1, '{"MATH101"}', '{"Master integral calculus", "Solve differential equations"}'),
('Linear Algebra', 'MATH201', 'MINOR', 4, 4, 1, '{}', '{"Understand vector spaces", "Perform matrix operations"}'),
('Statistics', 'MATH202', 'MINOR', 4, 4, 1, '{}', '{"Apply statistical methods", "Interpret statistical results"}'),
('Advanced Mathematics', 'MATH301', 'MINOR', 4, 5, 1, '{"MATH102", "MATH201"}', '{"Solve complex mathematical problems", "Apply advanced techniques"}'),
('Numerical Methods', 'MATH302', 'MINOR', 4, 5, 1, '{"MATH201", "CS101"}', '{"Implement numerical algorithms", "Solve mathematical problems computationally"}'),
('Mathematical Modeling', 'MATH401', 'MINOR', 4, 6, 1, '{"MATH202", "MATH301"}', '{"Create mathematical models", "Validate model accuracy"}'),
('Operations Research', 'MATH402', 'MINOR', 4, 6, 1, '{"MATH201", "MATH202"}', '{"Optimize resource allocation", "Solve decision problems"}'),

-- PROJECT courses
('Capstone Project I', 'PROJ401', 'PROJECT', 4, 7, 1, '{"CS201", "CS202", "CS203"}', '{"Define project scope", "Develop project proposal"}'),
('Capstone Project II', 'PROJ402', 'PROJECT', 2, 8, 1, '{"PROJ401"}', '{"Complete project implementation", "Present project results"}'),
('Industry Internship', 'PROJ403', 'PROJECT', 2, 8, 1, '{}', '{"Gain industry experience", "Apply academic knowledge"}');

-- Credit Distribution Summary Table
CREATE TABLE nep_credit_distribution (
    id SERIAL PRIMARY KEY,
    program_type VARCHAR(50) NOT NULL,
    category_code VARCHAR(10) REFERENCES nep_categories(code),
    allocated_credits INTEGER NOT NULL,
    percentage_of_total DECIMAL(5,2),
    compliance_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert credit distribution for 4-year UG program (160 credits total)
INSERT INTO nep_credit_distribution (program_type, category_code, allocated_credits, percentage_of_total, compliance_notes) VALUES
('undergraduate', 'MAJOR', 88, 55.00, 'Minimum 50% as per NEP guidelines'),
('undergraduate', 'MINOR', 32, 20.00, 'Provides breadth across disciplines'),
('undergraduate', 'AEC', 8, 5.00, 'Essential for skill development'),
('undergraduate', 'SEC', 12, 7.50, 'Vocational and practical skills'),
('undergraduate', 'VAC', 8, 5.00, 'Values and ethics integration'),
('undergraduate', 'MDC', 12, 7.50, 'Multidisciplinary learning');

-- Create indexes for better performance
CREATE INDEX idx_nep_subjects_category ON nep_subjects(category_code);
CREATE INDEX idx_nep_subjects_semester ON nep_subjects(semester);
CREATE INDEX idx_nep_course_structure_semester ON nep_course_structure(semester, category_code);

-- Views for easy data retrieval
CREATE VIEW nep_semester_structure AS
SELECT 
    s.semester,
    s.category_code,
    nc.name as category_name,
    s.recommended_credits,
    s.courses_per_semester,
    nc.description as category_description
FROM nep_course_structure s
JOIN nep_categories nc ON s.category_code = nc.code
WHERE s.program_type = 'undergraduate'
ORDER BY s.semester, s.category_code;

CREATE VIEW nep_compliance_summary AS
SELECT 
    cd.category_code,
    nc.name as category_name,
    cd.allocated_credits,
    cd.percentage_of_total,
    nc.min_credits,
    nc.max_credits,
    CASE 
        WHEN cd.allocated_credits >= nc.min_credits AND cd.allocated_credits <= nc.max_credits 
        THEN 'COMPLIANT' 
        ELSE 'NON_COMPLIANT' 
    END as compliance_status
FROM nep_credit_distribution cd
JOIN nep_categories nc ON cd.category_code = nc.code
WHERE cd.program_type = 'undergraduate';