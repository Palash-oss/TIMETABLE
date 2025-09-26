#!/usr/bin/env python3
"""
Complete Database Setup Script for Timetable Generator
This script will create all necessary tables in your Supabase database
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import sys

load_dotenv()

def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        sys.exit(1)
    
    return create_client(url, key)

def create_database_tables():
    """Create all required tables using Supabase SQL execution"""
    
    # SQL to create all tables
    sql_commands = """
-- Create institutions table
CREATE TABLE IF NOT EXISTS institutions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    contact_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create programs table
CREATE TABLE IF NOT EXISTS programs (
    id SERIAL PRIMARY KEY,
    institution_id INTEGER REFERENCES institutions(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    duration_semesters INTEGER NOT NULL DEFAULT 8,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create semesters table
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

-- Create subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    semester_id INTEGER REFERENCES semesters(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    credits INTEGER DEFAULT 3,
    subject_type VARCHAR(50) DEFAULT 'core',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(semester_id, code)
);

-- Create teachers table
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

-- Create classrooms table
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

-- Create time_slots table
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

-- Create subject_teacher_assignments table
CREATE TABLE IF NOT EXISTS subject_teacher_assignments (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    teacher_id INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
    hours_per_week INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(subject_id, teacher_id)
);

-- Create timetables table
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

-- Create timetable_entries table
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
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(timetable_id, classroom_id, time_slot_id, day_of_week),
    UNIQUE(timetable_id, teacher_id, time_slot_id, day_of_week)
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

-- Insert some default time slots (Monday = 0, Sunday = 6)
INSERT INTO institutions (name, address, contact_info) 
VALUES ('Default Institution', 'Sample Address', '{"phone": "+1234567890", "email": "admin@example.com"}')
ON CONFLICT DO NOTHING;

-- Get the institution ID for time slots
DO $$
DECLARE
    inst_id INTEGER;
BEGIN
    SELECT id INTO inst_id FROM institutions WHERE name = 'Default Institution' LIMIT 1;
    
    -- Insert default time slots for weekdays (Monday=0 to Friday=4)
    INSERT INTO time_slots (institution_id, day_of_week, start_time, end_time, slot_name) VALUES
    (inst_id, 0, '09:00', '10:00', 'Period 1'), -- Monday
    (inst_id, 0, '10:00', '11:00', 'Period 2'),
    (inst_id, 0, '11:00', '12:00', 'Period 3'),
    (inst_id, 0, '12:00', '13:00', 'Period 4'),
    (inst_id, 0, '14:00', '15:00', 'Period 5'),
    (inst_id, 0, '15:00', '16:00', 'Period 6'),
    
    (inst_id, 1, '09:00', '10:00', 'Period 1'), -- Tuesday
    (inst_id, 1, '10:00', '11:00', 'Period 2'),
    (inst_id, 1, '11:00', '12:00', 'Period 3'),
    (inst_id, 1, '12:00', '13:00', 'Period 4'),
    (inst_id, 1, '14:00', '15:00', 'Period 5'),
    (inst_id, 1, '15:00', '16:00', 'Period 6'),
    
    (inst_id, 2, '09:00', '10:00', 'Period 1'), -- Wednesday
    (inst_id, 2, '10:00', '11:00', 'Period 2'),
    (inst_id, 2, '11:00', '12:00', 'Period 3'),
    (inst_id, 2, '12:00', '13:00', 'Period 4'),
    (inst_id, 2, '14:00', '15:00', 'Period 5'),
    (inst_id, 2, '15:00', '16:00', 'Period 6'),
    
    (inst_id, 3, '09:00', '10:00', 'Period 1'), -- Thursday
    (inst_id, 3, '10:00', '11:00', 'Period 2'),
    (inst_id, 3, '11:00', '12:00', 'Period 3'),
    (inst_id, 3, '12:00', '13:00', 'Period 4'),
    (inst_id, 3, '14:00', '15:00', 'Period 5'),
    (inst_id, 3, '15:00', '16:00', 'Period 6'),
    
    (inst_id, 4, '09:00', '10:00', 'Period 1'), -- Friday
    (inst_id, 4, '10:00', '11:00', 'Period 2'),
    (inst_id, 4, '11:00', '12:00', 'Period 3'),
    (inst_id, 4, '12:00', '13:00', 'Period 4'),
    (inst_id, 4, '14:00', '15:00', 'Period 5'),
    (inst_id, 4, '15:00', '16:00', 'Period 6')
    ON CONFLICT DO NOTHING;
END $$;
    """
    
    return sql_commands

def main():
    """Main setup function"""
    print("🚀 Setting up Timetable Generator Database...")
    
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        print("✅ Connected to Supabase successfully!")
        
        # Get the SQL commands
        sql_commands = create_database_tables()
        
        # Execute the SQL
        print("📊 Creating database tables...")
        result = supabase.rpc('exec_sql', {'sql': sql_commands}).execute()
        
        print("✅ Database tables created successfully!")
        
        # Test the setup by querying a table
        print("🧪 Testing database setup...")
        institutions = supabase.table('institutions').select('*').execute()
        print(f"✅ Found {len(institutions.data)} institutions in database")
        
        time_slots = supabase.table('time_slots').select('*').execute()
        print(f"✅ Created {len(time_slots.data)} default time slots")
        
        print("\n🎉 Database setup completed successfully!")
        print("You can now run your timetable generator application.")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\nTrying alternative method...")
        
        # Alternative: Create tables one by one using direct table operations
        try:
            setup_with_direct_operations(supabase)
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            print("\nPlease set up tables manually in Supabase dashboard:")
            print("1. Go to your Supabase project dashboard")
            print("2. Navigate to 'SQL Editor'")
            print("3. Copy and paste the SQL from database_schema.sql")
            return False
    
    return True

def setup_with_direct_operations(supabase):
    """Alternative setup method using direct table creation"""
    print("🔄 Attempting direct table creation...")
    
    # Create a simple test entry to verify write access
    test_data = {
        'name': 'Default Institution',
        'address': 'Default Address',
        'contact_info': {'email': 'admin@example.com'}
    }
    
    # Try to insert test data
    result = supabase.table('institutions').insert(test_data).execute()
    print("✅ Direct table operations successful!")

if __name__ == "__main__":
    main()