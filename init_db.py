#!/usr/bin/env python3
"""
Initialize database using Supabase REST API
This approach creates tables by inserting data directly
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def create_sample_data():
    """Create sample data that will auto-create tables"""
    
    print("🚀 Initializing database with sample data...")
    
    # Sample programs data
    programs_data = [
        {
            "name": "Bachelor of Education", 
            "code": "BED", 
            "type": "B.Ed.", 
            "duration_years": 2, 
            "total_credits": 120
        },
        {
            "name": "Master of Education", 
            "code": "MED", 
            "type": "M.Ed.", 
            "duration_years": 2, 
            "total_credits": 80
        },
        {
            "name": "Four Year Undergraduate Program", 
            "code": "FYUP", 
            "type": "FYUP", 
            "duration_years": 4, 
            "total_credits": 160
        }
    ]
    
    # Faculty data
    faculty_data = [
        {
            "employee_id": "FAC001",
            "name": "Dr. Sarah Johnson",
            "email": "sarah.johnson@university.edu",
            "department": "Education",
            "expertise": ["Educational Psychology", "Child Development"],
            "max_hours_per_week": 20
        },
        {
            "employee_id": "FAC002",
            "name": "Prof. Michael Brown",
            "email": "michael.brown@university.edu",
            "department": "Mathematics", 
            "expertise": ["Mathematics Pedagogy", "Curriculum Design"],
            "max_hours_per_week": 18
        },
        {
            "employee_id": "FAC003",
            "name": "Dr. Emily Davis",
            "email": "emily.davis@university.edu",
            "department": "Science",
            "expertise": ["Science Teaching", "Research Methods"],
            "max_hours_per_week": 20
        }
    ]
    
    # Rooms data
    rooms_data = [
        {
            "room_number": "101",
            "building": "Main Building",
            "capacity": 50,
            "room_type": "Classroom",
            "is_available": True
        },
        {
            "room_number": "102", 
            "building": "Main Building",
            "capacity": 45,
            "room_type": "Classroom",
            "is_available": True
        },
        {
            "room_number": "Lab1",
            "building": "Science Block",
            "capacity": 30,
            "room_type": "Lab",
            "is_available": True
        },
        {
            "room_number": "Hall1",
            "building": "Administrative Block", 
            "capacity": 100,
            "room_type": "Seminar Hall",
            "is_available": True
        }
    ]
    
    # Time slots data
    time_slots_data = [
        {"day_of_week": 1, "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "Theory"},
        {"day_of_week": 1, "start_time": "10:00:00", "end_time": "11:00:00", "slot_type": "Theory"},
        {"day_of_week": 1, "start_time": "11:00:00", "end_time": "12:00:00", "slot_type": "Theory"},
        {"day_of_week": 1, "start_time": "14:00:00", "end_time": "15:00:00", "slot_type": "Theory"},
        {"day_of_week": 1, "start_time": "15:00:00", "end_time": "16:00:00", "slot_type": "Practical"},
        {"day_of_week": 2, "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "Theory"},
        {"day_of_week": 2, "start_time": "10:00:00", "end_time": "11:00:00", "slot_type": "Theory"},
        {"day_of_week": 2, "start_time": "11:00:00", "end_time": "12:00:00", "slot_type": "Theory"},
        {"day_of_week": 3, "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "Theory"},
        {"day_of_week": 3, "start_time": "10:00:00", "end_time": "11:00:00", "slot_type": "Theory"}
    ]

    # Insert data into tables
    tables = [
        ("programs", programs_data),
        ("faculty", faculty_data), 
        ("rooms", rooms_data),
        ("time_slots", time_slots_data)
    ]
    
    for table_name, data in tables:
        print(f"📊 Creating {table_name} data...")
        
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/{table_name}",
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ {table_name} data created successfully!")
            else:
                print(f"⚠️  {table_name}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating {table_name}: {e}")
    
    # Now create courses (depends on programs)
    print("📚 Creating courses...")
    
    # First, get program IDs
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/programs?select=id,code",
            headers=headers
        )
        
        if response.status_code == 200:
            programs = response.json()
            
            # Create courses for B.Ed program
            bed_program = next((p for p in programs if p['code'] == 'BED'), None)
            
            if bed_program:
                courses_data = [
                    {
                        "code": "EDP101",
                        "name": "Educational Psychology", 
                        "program_id": bed_program['id'],
                        "semester": 1,
                        "credits": 4,
                        "theory_hours": 3,
                        "practical_hours": 1,
                        "course_type": "Core"
                    },
                    {
                        "code": "TM101",
                        "name": "Teaching Methods",
                        "program_id": bed_program['id'], 
                        "semester": 1,
                        "credits": 4,
                        "theory_hours": 3,
                        "practical_hours": 1,
                        "course_type": "Core"
                    },
                    {
                        "code": "CD101", 
                        "name": "Curriculum Design",
                        "program_id": bed_program['id'],
                        "semester": 1,
                        "credits": 3,
                        "theory_hours": 3,
                        "practical_hours": 0,
                        "course_type": "Core"
                    }
                ]
                
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/courses",
                    headers=headers,
                    data=json.dumps(courses_data)
                )
                
                if response.status_code in [200, 201]:
                    print("✅ Courses created successfully!")
                else:
                    print(f"⚠️  Courses: {response.status_code} - {response.text}")
                    
        else:
            print(f"❌ Could not fetch programs: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating courses: {e}")

def test_connection():
    """Test API connection"""
    print("🔍 Testing Supabase connection...")
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/programs?select=count",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Connection successful!")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🎓 Timetable Generator - Database Initialization")
    print("=" * 55)
    
    if test_connection():
        create_sample_data()
        print("\n🎉 Database initialization completed!")
        print("✅ You can now use the timetable generator!")
    else:
        print("❌ Failed to connect to Supabase. Check your credentials.")
        exit(1)