#!/usr/bin/env python3
"""
Simple Database Initializer using PostgreSQL connection
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get PostgreSQL connection from Supabase URL"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url:
        raise ValueError("SUPABASE_URL must be set")
    
    # Extract connection details from Supabase URL
    # Format: https://xxx.supabase.co
    project_ref = url.replace("https://", "").replace(".supabase.co", "")
    
    # Supabase connection details
    conn_params = {
        'host': f'aws-0-{project_ref.split("-")[-1]}.pooler.supabase.com',
        'database': 'postgres',
        'user': 'postgres.{}'.format(project_ref),
        'password': os.environ.get('DB_PASSWORD', ''),
        'port': 6543,
        'sslmode': 'require'
    }
    
    return psycopg2.connect(**conn_params)

def create_tables():
    """Create database tables"""
    
    schema_sql = """
    -- Enable UUID extension
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Programs table
    CREATE TABLE IF NOT EXISTS programs (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        code VARCHAR(20) UNIQUE NOT NULL,
        type VARCHAR(50) NOT NULL,
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
        room_type VARCHAR(50),
        is_available BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Time slots table
    CREATE TABLE IF NOT EXISTS time_slots (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        day_of_week INTEGER NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        slot_type VARCHAR(50) DEFAULT 'Theory',
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
        course_type VARCHAR(50),
        prerequisites TEXT[],
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Faculty assignments
    CREATE TABLE IF NOT EXISTS faculty_assignments (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        faculty_id UUID REFERENCES faculty(id) ON DELETE CASCADE,
        course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
        semester VARCHAR(20) NOT NULL,
        academic_year VARCHAR(20) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Constraints
    CREATE TABLE IF NOT EXISTS constraints (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        constraint_type VARCHAR(50) NOT NULL,
        is_hard_constraint BOOLEAN DEFAULT true,
        parameters JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Generated timetables
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
    
    print("Creating tables...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(schema_sql)
        conn.commit()
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        create_tables()
    except Exception as e:
        print(f"Database setup failed: {e}")
        print("\n💡 Alternative: Use the REST API approach instead")