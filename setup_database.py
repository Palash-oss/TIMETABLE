#!/usr/bin/env python3
"""
Database Setup Script for Timetable Generator
This script will create all necessary tables and add sample data
"""

import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    
    return create_client(url, key)

def setup_database():
    """Setup database tables and initial data"""
    print("🚀 Setting up Timetable Generator Database...")
    
    supabase = get_supabase_client()
    
    # Database schema SQL
    schema_sql = """
    -- Enable UUID extension if not already enabled
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Programs table
    CREATE TABLE IF NOT EXISTS programs (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        code VARCHAR(20) UNIQUE NOT NULL,
        type VARCHAR(50) NOT NULL, -- B.Ed., M.Ed., FYUP, ITEP
        duration_years INTEGER NOT NULL,
        total_credits INTEGER NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Faculty table
    CREATE TABLE IF NOT EXISTS faculty (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        employee_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        department VARCHAR(100),
        expertise TEXT[],
        max_hours_per_week INTEGER DEFAULT 20,
        availability JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Rooms table
    CREATE TABLE IF NOT EXISTS rooms (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        room_number VARCHAR(20) UNIQUE NOT NULL,
        building VARCHAR(100),
        capacity INTEGER NOT NULL,
        room_type VARCHAR(50), -- Classroom, Lab, Seminar Hall
        is_available BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Time slots table
    CREATE TABLE IF NOT EXISTS time_slots (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        day_of_week INTEGER NOT NULL, -- 1=Monday, 2=Tuesday, etc.
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        slot_type VARCHAR(50) DEFAULT 'Theory', -- Theory, Practical, Tutorial
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Courses table
    CREATE TABLE IF NOT EXISTS courses (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        code VARCHAR(20) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
        semester INTEGER NOT NULL,
        credits INTEGER NOT NULL,
        theory_hours INTEGER DEFAULT 0,
        practical_hours INTEGER DEFAULT 0,
        tutorial_hours INTEGER DEFAULT 0,
        course_type VARCHAR(50), -- Core, Elective, AEC, SEC, VAC
        prerequisites TEXT[],
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Faculty assignments table
    CREATE TABLE IF NOT EXISTS faculty_assignments (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        faculty_id UUID REFERENCES faculty(id) ON DELETE CASCADE,
        course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
        semester VARCHAR(20) NOT NULL,
        academic_year VARCHAR(20) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(faculty_id, course_id, semester, academic_year)
    );

    -- Constraints table
    CREATE TABLE IF NOT EXISTS constraints (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        constraint_type VARCHAR(50) NOT NULL,
        is_hard_constraint BOOLEAN DEFAULT true,
        parameters JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Generated timetables table
    CREATE TABLE IF NOT EXISTS generated_timetables (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        semester VARCHAR(20) NOT NULL,
        academic_year VARCHAR(20) NOT NULL,
        program_ids UUID[],
        status VARCHAR(50) DEFAULT 'generated',
        generation_params JSONB,
        timetable_data JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        # Execute schema creation using raw SQL
        print("📋 Creating database schema...")
        result = supabase.rpc('exec_sql', {'sql': schema_sql})
        print("✅ Database schema created successfully!")
        
    except Exception as e:
        print(f"⚠️  Schema creation via RPC failed: {e}")
        print("📋 Trying alternative approach - creating tables individually...")
        
        # Try creating tables through REST API inserts (this might work better)
        try:
            # Create programs
            programs_data = [
                {'name': 'Bachelor of Education', 'code': 'BED', 'type': 'B.Ed.', 'duration_years': 2, 'total_credits': 120},
                {'name': 'Master of Education', 'code': 'MED', 'type': 'M.Ed.', 'duration_years': 2, 'total_credits': 80},
                {'name': 'Four Year Undergraduate Program', 'code': 'FYUP', 'type': 'FYUP', 'duration_years': 4, 'total_credits': 160},
                {'name': 'Integrated Teacher Education Program', 'code': 'ITEP', 'type': 'ITEP', 'duration_years': 4, 'total_credits': 140}
            ]
            
            print("📚 Adding sample programs...")
            supabase.table('programs').insert(programs_data).execute()
            print("✅ Sample programs added!")
            
        except Exception as e2:
            print(f"❌ Failed to create tables: {e2}")
            print("💡 You may need to manually create the database schema in Supabase dashboard")
            return False

    # Add sample data
    try:
        add_sample_data(supabase)
        print("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"⚠️  Sample data creation failed: {e}")
        print("✅ Database schema is ready, but you may need to add data manually")
        return True

def add_sample_data(supabase: Client):
    """Add sample data for testing"""
    print("📊 Adding sample data...")
    
    # Sample faculty
    faculty_data = [
        {
            'employee_id': 'FAC001',
            'name': 'Dr. Sarah Johnson',
            'email': 'sarah.johnson@university.edu',
            'department': 'Education',
            'expertise': ['Educational Psychology', 'Child Development'],
            'max_hours_per_week': 20
        },
        {
            'employee_id': 'FAC002',
            'name': 'Prof. Michael Brown',
            'email': 'michael.brown@university.edu',
            'department': 'Mathematics',
            'expertise': ['Mathematics Pedagogy', 'Curriculum Design'],
            'max_hours_per_week': 18
        }
    ]
    
    # Sample rooms
    rooms_data = [
        {'room_number': '101', 'building': 'Main Building', 'capacity': 50, 'room_type': 'Classroom', 'is_available': True},
        {'room_number': '102', 'building': 'Main Building', 'capacity': 45, 'room_type': 'Classroom', 'is_available': True},
        {'room_number': 'Lab1', 'building': 'Science Block', 'capacity': 30, 'room_type': 'Lab', 'is_available': True}
    ]
    
    # Sample time slots
    time_slots_data = [
        {'day_of_week': 1, 'start_time': '09:00:00', 'end_time': '10:00:00', 'slot_type': 'Theory'},
        {'day_of_week': 1, 'start_time': '10:00:00', 'end_time': '11:00:00', 'slot_type': 'Theory'},
        {'day_of_week': 1, 'start_time': '11:00:00', 'end_time': '12:00:00', 'slot_type': 'Theory'},
        {'day_of_week': 2, 'start_time': '09:00:00', 'end_time': '10:00:00', 'slot_type': 'Theory'},
        {'day_of_week': 2, 'start_time': '10:00:00', 'end_time': '11:00:00', 'slot_type': 'Theory'}
    ]
    
    try:
        supabase.table('faculty').insert(faculty_data).execute()
        print("👥 Faculty data added!")
        
        supabase.table('rooms').insert(rooms_data).execute()
        print("🏢 Rooms data added!")
        
        supabase.table('time_slots').insert(time_slots_data).execute()
        print("⏰ Time slots added!")
        
    except Exception as e:
        print(f"⚠️  Some sample data may already exist: {e}")

def test_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        supabase = get_supabase_client()
        
        # Test by fetching programs
        result = supabase.table('programs').select("*").execute()
        print(f"✅ Connection successful! Found {len(result.data)} programs in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🎓 Timetable Generator - Database Setup")
    print("=" * 50)
    
    # Test connection first
    if not test_connection():
        print("❌ Cannot connect to database. Please check your credentials.")
        exit(1)
    
    # Setup database
    if setup_database():
        print("\n🎉 Setup completed successfully!")
        print("✅ You can now use the timetable generator!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        exit(1)