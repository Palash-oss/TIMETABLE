"""
Database initialization utilities
"""
from .database import supabase

def initialize_database():
    """Initialize database with required tables and sample data"""
    
    try:
        # Test connection by trying to create a simple table
        print("Initializing database...")
        
        # Create sample data directly via REST API
        sample_programs = [
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
            }
        ]
        
        # Try to insert sample programs
        result = supabase.table('programs').insert(sample_programs).execute()
        print(f"Programs created: {len(result.data)} records")
        
        # Sample faculty
        sample_faculty = [
            {
                "employee_id": "FAC001",
                "name": "Dr. Sarah Johnson",
                "email": "sarah.johnson@university.edu",
                "department": "Education",
                "expertise": ["Educational Psychology"],
                "max_hours_per_week": 20
            },
            {
                "employee_id": "FAC002", 
                "name": "Prof. Michael Brown",
                "email": "michael.brown@university.edu",
                "department": "Mathematics",
                "expertise": ["Mathematics Pedagogy"],
                "max_hours_per_week": 18
            }
        ]
        
        result = supabase.table('faculty').insert(sample_faculty).execute()
        print(f"Faculty created: {len(result.data)} records")
        
        # Sample rooms
        sample_rooms = [
            {
                "room_number": "101",
                "building": "Main Building", 
                "capacity": 50,
                "room_type": "Classroom",
                "is_available": True
            },
            {
                "room_number": "Lab1",
                "building": "Science Block",
                "capacity": 30, 
                "room_type": "Lab",
                "is_available": True
            }
        ]
        
        result = supabase.table('rooms').insert(sample_rooms).execute()
        print(f"Rooms created: {len(result.data)} records")
        
        # Sample time slots
        sample_time_slots = [
            {"day_of_week": 1, "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "Theory"},
            {"day_of_week": 1, "start_time": "10:00:00", "end_time": "11:00:00", "slot_type": "Theory"},
            {"day_of_week": 1, "start_time": "11:00:00", "end_time": "12:00:00", "slot_type": "Theory"},
            {"day_of_week": 2, "start_time": "09:00:00", "end_time": "10:00:00", "slot_type": "Theory"},
            {"day_of_week": 2, "start_time": "10:00:00", "end_time": "11:00:00", "slot_type": "Theory"}
        ]
        
        result = supabase.table('time_slots').insert(sample_time_slots).execute()
        print(f"Time slots created: {len(result.data)} records")
        
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

def check_database_status():
    """Check if database is properly initialized"""
    try:
        # Try to fetch data from key tables
        programs = supabase.table('programs').select('count').execute()
        faculty = supabase.table('faculty').select('count').execute()
        rooms = supabase.table('rooms').select('count').execute()
        
        return {
            'initialized': True,
            'programs': len(programs.data) if programs.data else 0,
            'faculty': len(faculty.data) if faculty.data else 0, 
            'rooms': len(rooms.data) if rooms.data else 0
        }
        
    except Exception as e:
        return {'initialized': False, 'error': str(e)}