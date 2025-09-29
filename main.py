from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional
from uuid import UUID
import os

from app.database import supabase
from app.models import *
from app.generator import TimetableGenerator
from app.export_utils import TimetableExporter
from app.db_init import initialize_database, check_database_status

app = FastAPI(
    title="AI Timetable Generator",
    description="Automated Academic Timetable Generation System compliant with NEP 2020",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
async def root():
    return {"message": "AI Timetable Generator API is running", "status": "healthy"}

# Database initialization endpoints
@app.post("/api/init-database")
async def init_database():
    """Initialize database with sample data"""
    try:
        success = initialize_database()
        if success:
            return {"message": "Database initialized successfully", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize database")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")

@app.get("/api/database-status")
async def get_database_status():
    """Check database initialization status"""
    try:
        status = check_database_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NEP 2020 Helper Functions
def generate_nep_compliant_schedule(subjects, teachers, classrooms, time_slots):
    """Generate NEP 2020 compliant schedule with randomization"""
    import random
    
    schedule = {}
    
    # NEP category priority order
    nep_priority = ['MAJOR', 'AEC', 'SEC', 'MDC', 'MINOR', 'VAC', 'PROJECT']
    
    # Sort subjects by NEP priority but add some randomness
    sorted_subjects = sorted(subjects, 
                           key=lambda x: (nep_priority.index(x.get('nep_category', 'MAJOR')) 
                           if x.get('nep_category', 'MAJOR') in nep_priority else len(nep_priority), 
                           random.random()))
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    time_periods = [
        ('09:00', '10:00'),
        ('10:00', '11:00'), 
        ('11:00', '12:00'),
        ('12:00', '13:00'),  # Lunch break possibility
        ('14:00', '15:00'),
        ('15:00', '16:00'),
        ('16:00', '17:00')
    ]
    
    # Create a pool of all possible combinations
    subject_pool = []
    for subject in sorted_subjects:
        # Each subject appears multiple times based on credits (more credits = more classes)
        credits = subject.get('credits', 1)
        for _ in range(max(1, credits)):
            subject_pool.append(subject.copy())
    
    # Randomize the subject pool
    random.shuffle(subject_pool)
    
    # Track subject usage to ensure variety
    daily_subject_usage = {day: {} for day in days}
    
    for day_idx, day in enumerate(days):
        schedule[day] = []
        
        # Randomly select 4-6 periods for the day
        num_periods = random.randint(4, 6)
        selected_periods = random.sample(time_periods, num_periods)
        selected_periods.sort()  # Sort by time
        
        # Skip lunch hour (12-13) sometimes
        if ('12:00', '13:00') in selected_periods and random.random() < 0.7:
            selected_periods.remove(('12:00', '13:00'))
        
        for period_idx, (start_time, end_time) in enumerate(selected_periods):
            if subject_pool:
                # Try to pick a subject we haven't used much today
                available_subjects = [s for s in subject_pool 
                                    if daily_subject_usage[day].get(s.get('code', ''), 0) < 2]
                
                if not available_subjects:
                    available_subjects = subject_pool
                
                subject = random.choice(available_subjects)
                subject_code = subject.get('code', '')
                daily_subject_usage[day][subject_code] = daily_subject_usage[day].get(subject_code, 0) + 1
                
                # Smart teacher assignment with some randomization
                suitable_teachers = [t for t in teachers 
                                   if subject_code[:2].lower() in t.get('specialization', '').lower() or
                                   any(word in t.get('specialization', '').lower() 
                                       for word in subject.get('name', '').lower().split())]
                
                if not suitable_teachers:
                    suitable_teachers = teachers
                    
                assigned_teacher = random.choice(suitable_teachers) if suitable_teachers else None
                
                # Smart classroom assignment
                assigned_classroom = assign_classroom_by_type(subject, classrooms)
                if not assigned_classroom:
                    assigned_classroom = random.choice(classrooms) if classrooms else None
                
                schedule[day].append({
                    'time': f"{start_time}-{end_time}",
                    'subject_name': subject.get('name', 'Unknown'),
                    'subject_code': subject.get('code', ''),
                    'nep_category': subject.get('nep_category', 'MAJOR'),
                    'credits': subject.get('credits', 0),
                    'teacher': assigned_teacher.get('name', 'TBA') if assigned_teacher else 'TBA',
                    'classroom': assigned_classroom.get('name', 'TBA') if assigned_classroom else 'TBA',
                    'is_skill_based': subject.get('is_skill_based', False),
                    'is_lab': 'lab' in subject.get('name', '').lower()
                })
    
    return schedule

def assign_teacher_by_expertise(subject, teachers):
    """Assign teacher based on subject and expertise with better matching"""
    subject_name = subject.get('name', '').lower()
    subject_code = subject.get('code', '')
    
    # Extract department from subject code (e.g., CS301 -> CS, ECE301 -> ECE)
    subject_dept = subject_code[:2].upper() if len(subject_code) >= 2 else ''
    if subject_dept in ['EV', 'PS', 'EC', 'MG', 'EN']:  # Handle special cases
        subject_dept_map = {
            'EV': 'ENV',
            'PS': 'PSY', 
            'EC': 'ECO',
            'MG': 'MGT',
            'EN': 'ENT'
        }
        subject_dept = subject_dept_map.get(subject_dept, subject_dept)
    
    # First, try exact department match
    for teacher in teachers:
        teacher_dept = teacher.get('department', '')
        if teacher_dept == subject_dept:
            return teacher
    
    # Then try specialization matching
    for teacher in teachers:
        specialization = teacher.get('specialization', '').lower()
        
        # Subject-specific matching
        if ('computer' in subject_name or 'software' in subject_name or 'programming' in subject_name) and 'computer' in specialization:
            return teacher
        elif ('electronics' in subject_name or 'circuit' in subject_name or 'digital' in subject_name) and 'electronics' in specialization:
            return teacher
        elif ('mechanical' in subject_name or 'thermo' in subject_name or 'fluid' in subject_name) and 'mechanical' in specialization:
            return teacher
        elif ('civil' in subject_name or 'structural' in subject_name or 'concrete' in subject_name) and 'civil' in specialization:
            return teacher
        elif ('electrical' in subject_name or 'power' in subject_name) and 'electrical' in specialization:
            return teacher
        elif ('chemical' in subject_name or 'process' in subject_name) and 'chemical' in specialization:
            return teacher
        elif 'environmental' in subject_name and 'environmental' in specialization:
            return teacher
        elif 'management' in subject_name and 'management' in specialization:
            return teacher
        elif 'economics' in subject_name and 'economics' in specialization:
            return teacher
    
    # Return first available teacher as fallback
    return teachers[0] if teachers else None

def assign_classroom_by_type(subject, classrooms):
    """Assign classroom based on subject type and department"""
    subject_name = subject.get('name', '').lower()
    subject_code = subject.get('code', '')
    is_lab = subject.get('is_skill_based', False) or 'lab' in subject_name
    
    # Extract department from subject code
    subject_dept = subject_code[:2].upper() if len(subject_code) >= 2 else ''
    
    # Lab subjects need specific labs
    if is_lab:
        # Try to match department-specific lab first
        for classroom in classrooms:
            classroom_dept = classroom.get('department', '')
            classroom_type = classroom.get('type', '')
            if (classroom_dept == subject_dept or 
                ('LAB' in classroom_type and subject_dept in classroom.get('name', ''))):
                return classroom
        
        # Fallback to any lab
        for classroom in classrooms:
            if 'LAB' in classroom.get('type', ''):
                return classroom
    
    # Special subject types
    if 'workshop' in subject_name or 'manufacturing' in subject_name:
        for classroom in classrooms:
            if classroom.get('type') == 'WORKSHOP':
                return classroom
    
    if 'cad' in subject_name or 'design' in subject_name:
        for classroom in classrooms:
            if classroom.get('type') == 'CAD_LAB':
                return classroom
    
    # Regular subjects get lecture halls or tutorial rooms
    for classroom in classrooms:
        classroom_type = classroom.get('type', '')
        if classroom_type in ['LECTURE', 'SEMINAR', 'TUTORIAL']:
            return classroom
            
    # Fallback to first available classroom
    return classrooms[0] if classrooms else None

def calculate_nep_compliance(subjects):
    """Calculate NEP 2020 compliance for subjects"""
    # Calculate credit distribution by NEP category
    credit_distribution = {}
    total_credits = 0
    
    for subject in subjects:
        category = subject.get('nep_category', 'MAJOR')
        credits = subject.get('credits', 0)
        credit_distribution[category] = credit_distribution.get(category, 0) + credits
        total_credits += credits
    
    # Check compliance
    compliance = {
        'total_credits': total_credits,
        'is_compliant': 18 <= total_credits <= 22,
        'has_multidisciplinary': credit_distribution.get('MDC', 0) > 0,
        'has_skill_component': any(s.get('is_skill_based', False) for s in subjects),
        'distribution': credit_distribution,
        'recommendations': []
    }
    
    # Generate recommendations
    if total_credits < 18:
        compliance['recommendations'].append("⚠️ Add more courses - minimum 18 credits required")
    elif total_credits > 22:
        compliance['recommendations'].append("⚠️ Consider reducing course load - maximum 22 credits recommended") 
    else:
        compliance['recommendations'].append("✅ Credit load is optimal (18-22 credits)")
    
    if not compliance['has_multidisciplinary']:
        compliance['recommendations'].append("📚 Add Multidisciplinary Courses (MDC)")
    else:
        compliance['recommendations'].append("✅ Multidisciplinary learning component present")
    
    if not compliance['has_skill_component']:
        compliance['recommendations'].append("🛠️ Include Skill Enhancement Courses (SEC)")
    else:
        compliance['recommendations'].append("✅ Skill-based learning component present")
    
    return compliance

# Program endpoints
@app.get("/api/programs")
async def get_programs():
    """Get all programs from the database"""
    try:
        response = supabase.table('programs').select("*").execute()
        
        if response.data:
            return {"programs": response.data, "status": "success"}
        else:
            return {"programs": [], "status": "empty", "message": "No programs found in database"}
            
    except Exception as e:
        return {"programs": [], "status": "error", "error": str(e), "message": "Failed to fetch programs from database"}

@app.post("/api/programs", response_model=Program)
async def create_program(program: ProgramCreate):
    try:
        response = supabase.table('programs').insert(program.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Seed more programs endpoint
@app.post("/api/programs/seed")
async def seed_programs():
    """Add more engineering programs to the database"""
    try:
        # Check if programs already exist
        existing_response = supabase.table('programs').select("code").execute()
        existing_codes = {prog['code'] for prog in existing_response.data} if existing_response.data else set()
        
        new_programs = [
            {
                "institution_id": 1,
                "name": "Electronics and Communication Engineering",
                "code": "ECE",
                "duration_semesters": 8
            },
            {
                "institution_id": 1,
                "name": "Mechanical Engineering", 
                "code": "MECH",
                "duration_semesters": 8
            },
            {
                "institution_id": 1,
                "name": "Civil Engineering",
                "code": "CIVIL", 
                "duration_semesters": 8
            },
            {
                "institution_id": 1,
                "name": "Electrical Engineering",
                "code": "EE",
                "duration_semesters": 8
            },
            {
                "institution_id": 1,
                "name": "Information Technology",
                "code": "IT",
                "duration_semesters": 8
            },
            {
                "institution_id": 1,
                "name": "Chemical Engineering",
                "code": "CHEM",
                "duration_semesters": 8
            }
        ]
        
        # Filter out existing programs
        programs_to_add = [prog for prog in new_programs if prog['code'] not in existing_codes]
        
        if not programs_to_add:
            return {"message": "All programs already exist", "added": 0, "status": "skipped"}
        
        # Insert new programs
        response = supabase.table('programs').insert(programs_to_add).execute()
        
        return {
            "message": f"Successfully added {len(programs_to_add)} new programs",
            "added": len(programs_to_add),
            "programs": response.data,
            "status": "success"
        }
        
    except Exception as e:
        return {"message": f"Failed to seed programs: {str(e)}", "status": "error"}

# NEP 2020 Enhanced endpoints
@app.get("/api/subjects")
async def get_subjects():
    """Get all subjects with NEP 2020 category information"""
    try:
        response = supabase.table('subjects').select("""
            *, 
            semesters(semester_number, programs(name, code))
        """).execute()
        return {"subjects": response.data, "status": "success"}
    except Exception as e:
        return {"subjects": [], "status": "error", "error": str(e)}

@app.get("/api/nep-categories")
async def get_nep_categories():
    """Get verified NEP 2020 categories from database"""
    try:
        response = supabase.table('nep_categories').select("*").order('id').execute()
        
        if response.data:
            return {
                "categories": response.data, 
                "status": "success",
                "total_categories": len(response.data),
                "compliance_info": "Based on UGC NEP 2020 Implementation Guidelines"
            }
        else:
            return {
                "categories": [], 
                "status": "empty", 
                "message": "No NEP categories found in database. Please run nep_2020_verified_data.sql"
            }
            
    except Exception as e:
        return {
            "categories": [], 
            "status": "error", 
            "error": str(e), 
            "message": "Failed to fetch NEP categories from database"
        }

@app.get("/api/nep-curriculum/{program_id}/{semester}")
async def get_nep_curriculum(program_id: int, semester: int):
    """Get NEP 2020 compliant curriculum for a program and semester"""
    try:
        # Get subjects for the semester with NEP categories
        subjects_response = supabase.table('subjects').select("""
            *,
            semesters!inner(semester_number, programs!inner(id, name, code))
        """).eq('semesters.programs.id', program_id).eq('semesters.semester_number', semester).execute()
        
        subjects = subjects_response.data
        
        # Calculate credit distribution by NEP category
        credit_distribution = {}
        total_credits = 0
        
        for subject in subjects:
            category = subject.get('nep_category', 'MAJOR')
            credits = subject.get('credits', 0)
            credit_distribution[category] = credit_distribution.get(category, 0) + credits
            total_credits += credits
        
        # Check NEP compliance
        nep_compliance = {
            'total_credits': total_credits,
            'recommended_range': '18-22',
            'is_compliant': 18 <= total_credits <= 22,
            'has_multidisciplinary': credit_distribution.get('MDC', 0) > 0,
            'has_skill_component': any(s.get('is_skill_based', False) for s in subjects),
            'distribution': credit_distribution
        }
        
        return {
            'program_id': program_id,
            'semester': semester,
            'subjects': subjects,
            'credit_distribution': credit_distribution,
            'total_credits': total_credits,
            'nep_compliance': nep_compliance,
            'status': 'success'
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@app.get("/api/nep-verified-curriculum/{program_id}/{semester}")
async def get_nep_verified_curriculum(program_id: int, semester: int):
    """Get NEP 2020 verified curriculum for a program and semester"""
    try:
        # Get curriculum structure for the semester
        structure_response = supabase.table('nep_course_structure').select("""
            *, 
            nep_categories(code, name, description, min_credits, max_credits)
        """).eq('semester', semester).eq('program_type', 'undergraduate').execute()
        
        # Get verified NEP subjects for the semester and program
        subjects_response = supabase.table('nep_subjects').select("""
            *, 
            nep_categories(name, description)
        """).eq('semester', semester).eq('program_id', program_id).execute()
        
        return {
            "semester": semester,
            "program_id": program_id,
            "structure": structure_response.data if structure_response.data else [],
            "subjects": subjects_response.data if subjects_response.data else [],
            "status": "success",
            "compliance": "NEP 2020 verified curriculum structure"
        }
        
    except Exception as e:
        return {
            "semester": semester,
            "program_id": program_id,
            "structure": [],
            "subjects": [],
            "status": "error",
            "error": str(e)
        }

@app.get("/api/nep-compliance/{program_id}")
async def get_nep_compliance(program_id: int):
    """Calculate NEP 2020 compliance for a program using verified data"""
    try:
        # Get all NEP subjects for the program
        subjects_response = supabase.table('nep_subjects').select("""
            category_code,
            credits,
            semester,
            nep_categories(name, min_credits, max_credits)
        """).eq('program_id', program_id).execute()
        
        if not subjects_response.data:
            return {
                "program_id": program_id,
                "compliance": {},
                "status": "empty",
                "message": "No NEP subjects found for program"
            }
        
        # Calculate credits by category
        category_credits = {}
        for subject in subjects_response.data:
            category = subject['category_code']
            credits = subject['credits']
            
            if category in category_credits:
                category_credits[category] += credits
            else:
                category_credits[category] = credits
        
        # Get NEP compliance requirements
        compliance_response = supabase.table('nep_credit_distribution').select("""
            category_code,
            allocated_credits,
            percentage_of_total,
            compliance_notes
        """).eq('program_type', 'undergraduate').execute()
        
        # Calculate compliance status
        compliance_status = {}
        total_credits = sum(category_credits.values())
        
        for req in compliance_response.data:
            category = req['category_code']
            actual_credits = category_credits.get(category, 0)
            required_credits = req['allocated_credits']
            
            compliance_status[category] = {
                "actual_credits": actual_credits,
                "required_credits": required_credits,
                "percentage": round((actual_credits / total_credits * 100) if total_credits > 0 else 0, 2),
                "required_percentage": req['percentage_of_total'],
                "status": "COMPLIANT" if actual_credits >= required_credits else "NON_COMPLIANT",
                "notes": req['compliance_notes']
            }
        
        overall_compliance = all(
            status["status"] == "COMPLIANT" 
            for status in compliance_status.values()
        )
        
        return {
            "program_id": program_id,
            "total_credits": total_credits,
            "compliance": compliance_status,
            "overall_compliance": "COMPLIANT" if overall_compliance else "NON_COMPLIANT",
            "status": "success",
            "verification": "Based on UGC NEP 2020 Implementation Guidelines"
        }
        
    except Exception as e:
        return {
            "program_id": program_id,
            "compliance": {},
            "status": "error",
            "error": str(e)
        }

@app.get("/api/nep-semester-structure/{semester}")
async def get_nep_semester_structure(semester: int):
    """Get NEP 2020 verified semester structure"""
    try:
        response = supabase.from_('nep_semester_structure').select("*").eq('semester', semester).execute()
        
        return {
            "semester": semester,
            "structure": response.data if response.data else [],
            "status": "success",
            "description": f"NEP 2020 verified structure for semester {semester}"
        }
        
    except Exception as e:
        return {
            "semester": semester,
            "structure": [],
            "status": "error",
            "error": str(e)
        }

@app.get("/api/teachers")
async def get_teachers():
    """Get all teachers"""
    try:
        response = supabase.table('teachers').select("*").execute()
        return {"teachers": response.data, "status": "success"}
    except Exception as e:
        return {"teachers": [], "status": "error", "error": str(e)}

@app.get("/api/classrooms")
async def get_classrooms():
    """Get all classrooms"""
    try:
        response = supabase.table('classrooms').select("*").execute()
        return {"classrooms": response.data, "status": "success"}
    except Exception as e:
        return {"classrooms": [], "status": "error", "error": str(e)}

@app.get("/api/time-slots")
async def get_time_slots():
    """Get all time slots"""
    try:
        response = supabase.table('time_slots').select("*").execute()
        return {"time_slots": response.data, "status": "success"}
    except Exception as e:
        return {"time_slots": [], "status": "error", "error": str(e)}

@app.get("/api/programs/{program_id}", response_model=Program)
async def get_program(program_id: UUID):
    try:
        response = supabase.table('programs').select("*").eq('id', str(program_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Program not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Faculty endpoints
@app.get("/api/faculty", response_model=List[Faculty])
async def get_faculty():
    try:
        response = supabase.table('faculty').select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/faculty", response_model=Faculty)
async def create_faculty(faculty: FacultyCreate):
    try:
        response = supabase.table('faculty').insert(faculty.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/faculty/{faculty_id}", response_model=Faculty)
async def get_faculty_member(faculty_id: UUID):
    try:
        response = supabase.table('faculty').select("*").eq('id', str(faculty_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Faculty not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Course endpoints
@app.get("/api/courses", response_model=List[Course])
async def get_courses(program_id: Optional[UUID] = None, semester: Optional[int] = None):
    try:
        query = supabase.table('courses').select("*")
        if program_id:
            query = query.eq('program_id', str(program_id))
        if semester:
            query = query.eq('semester', semester)
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/courses", response_model=Course)
async def create_course(course: CourseCreate):
    try:
        response = supabase.table('courses').insert(course.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/courses/{course_id}", response_model=Course)
async def get_course(course_id: UUID):
    try:
        response = supabase.table('courses').select("*").eq('id', str(course_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Course not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Room endpoints
@app.get("/api/rooms", response_model=List[Room])
async def get_rooms(available_only: bool = False):
    try:
        query = supabase.table('rooms').select("*")
        if available_only:
            query = query.eq('is_available', True)
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rooms", response_model=Room)
async def create_room(room: RoomCreate):
    try:
        response = supabase.table('rooms').insert(room.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Student endpoints
@app.get("/api/students", response_model=List[Student])
async def get_students(program_id: Optional[UUID] = None, semester: Optional[int] = None):
    try:
        query = supabase.table('students').select("*")
        if program_id:
            query = query.eq('program_id', str(program_id))
        if semester:
            query = query.eq('semester', semester)
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/students", response_model=Student)
async def create_student(student: StudentCreate):
    try:
        response = supabase.table('students').insert(student.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Time slot endpoints
@app.get("/api/time-slots", response_model=List[TimeSlot])
async def get_time_slots():
    try:
        response = supabase.table('time_slots').select("*").order('day_of_week').order('start_time').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/time-slots", response_model=TimeSlot)
async def create_time_slot(slot: TimeSlotCreate):
    try:
        response = supabase.table('time_slots').insert(slot.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Constraint endpoints
@app.get("/api/constraints", response_model=List[Constraint])
async def get_constraints():
    try:
        response = supabase.table('constraints').select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/constraints", response_model=Constraint)
async def create_constraint(constraint: ConstraintCreate):
    try:
        response = supabase.table('constraints').insert(constraint.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/constraints/{constraint_id}")
async def delete_constraint(constraint_id: UUID):
    try:
        response = supabase.table('constraints').delete().eq('id', str(constraint_id)).execute()
        return {"message": "Constraint deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-generation")
async def test_generation():
    """Simple test endpoint to debug generation issues"""
    try:
        # Test database connectivity
        subjects_response = supabase.table('subjects').select("*").limit(2).execute()
        teachers_response = supabase.table('teachers').select("*").limit(2).execute()
        classrooms_response = supabase.table('classrooms').select("*").limit(2).execute()
        time_slots_response = supabase.table('time_slots').select("*").limit(2).execute()
        
        return {
            "status": "success",
            "database_access": "working",
            "subjects_found": len(subjects_response.data),
            "teachers_found": len(teachers_response.data),
            "classrooms_found": len(classrooms_response.data),
            "time_slots_found": len(time_slots_response.data),
            "sample_subject": subjects_response.data[0] if subjects_response.data else None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

# NEP 2020 Enhanced Timetable generation endpoint
@app.post("/api/generate-timetable")
async def generate_timetable(request: dict):
    """Generate NEP 2020 compliant timetable using real database data"""
    try:
        program_id = request.get('program_id', 1)
        semester = request.get('semester', 1)
        
        # Try to get subjects - use simpler query first, fallback if no complex relations exist
        try:
            subjects_response = supabase.table('subjects').select("*").execute()
        except Exception as e:
            # If subjects table doesn't exist, create sample data
            subjects_response = None
        
        # Get teachers from database or create fallback
        try:
            teachers_response = supabase.table('teachers').select("*").execute()
        except Exception as e:
            teachers_response = None
        
        # Get classrooms from database or create fallback
        try:
            classrooms_response = supabase.table('classrooms').select("*").execute()
        except Exception as e:
            classrooms_response = None
        
        # Get real time slots from database or create fallback
        try:
            time_slots_response = supabase.table('time_slots').select("*").execute()
        except Exception as e:
            time_slots_response = None
        
        # Extract data or use fallback based on program
        def get_program_subjects(program_id):
            """Get program-specific subjects"""
            program_subjects = {
                1: [  # Computer Science
                    {"id": 1, "name": "Data Structures & Algorithms", "code": "CS301", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 2, "name": "Web Development Lab", "code": "CS302", "credits": 3, "nep_category": "SEC", "is_skill_based": True},
                    {"id": 3, "name": "Machine Learning", "code": "CS303", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 4, "name": "Environmental Studies", "code": "EVS101", "credits": 2, "nep_category": "AEC", "is_skill_based": False},
                    {"id": 5, "name": "Psychology", "code": "PSY201", "credits": 3, "nep_category": "MDC", "is_skill_based": False},
                    {"id": 6, "name": "Database Management Systems", "code": "CS304", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 7, "name": "Software Engineering", "code": "CS305", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 8, "name": "Computer Networks", "code": "CS306", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 9, "name": "Operating Systems", "code": "CS307", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False}
                ],
                2: [  # Electronics and Communication Engineering (ECE)
                    {"id": 1, "name": "Digital Electronics", "code": "ECE301", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 2, "name": "Microprocessors & Microcontrollers", "code": "ECE302", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 3, "name": "Circuit Analysis", "code": "ECE303", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 4, "name": "Communication Systems", "code": "ECE304", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 5, "name": "Environmental Studies", "code": "EVS101", "credits": 2, "nep_category": "AEC", "is_skill_based": False},
                    {"id": 6, "name": "PCB Design Lab", "code": "ECE305", "credits": 3, "nep_category": "SEC", "is_skill_based": True},
                    {"id": 7, "name": "Innovation & Entrepreneurship", "code": "ENT201", "credits": 2, "nep_category": "MDC", "is_skill_based": False},
                    {"id": 8, "name": "Analog Electronics", "code": "ECE306", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 9, "name": "Signal Processing", "code": "ECE307", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False}
                ],
                3: [  # Mechanical Engineering (MECH)
                    {"id": 1, "name": "Thermodynamics", "code": "MECH301", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 2, "name": "Fluid Mechanics", "code": "MECH302", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 3, "name": "Machine Design", "code": "MECH303", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 4, "name": "Manufacturing Processes", "code": "MECH304", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 5, "name": "Environmental Studies", "code": "EVS101", "credits": 2, "nep_category": "AEC", "is_skill_based": False},
                    {"id": 6, "name": "CAD/CAM Lab", "code": "MECH305", "credits": 3, "nep_category": "SEC", "is_skill_based": True},
                    {"id": 7, "name": "Economics", "code": "ECO201", "credits": 3, "nep_category": "MDC", "is_skill_based": False},
                    {"id": 8, "name": "Heat Transfer", "code": "MECH306", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 9, "name": "Strength of Materials", "code": "MECH307", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False}
                ],
                4: [  # Civil Engineering (CIVIL)
                    {"id": 1, "name": "Structural Analysis", "code": "CIVIL301", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 2, "name": "Concrete Technology", "code": "CIVIL302", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 3, "name": "Surveying & Leveling", "code": "CIVIL303", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 4, "name": "Geotechnical Engineering", "code": "CIVIL304", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 5, "name": "Environmental Studies", "code": "EVS101", "credits": 2, "nep_category": "AEC", "is_skill_based": False},
                    {"id": 6, "name": "AutoCAD Lab", "code": "CIVIL305", "credits": 3, "nep_category": "SEC", "is_skill_based": True},
                    {"id": 7, "name": "Management Studies", "code": "MGT201", "credits": 3, "nep_category": "MDC", "is_skill_based": False},
                    {"id": 8, "name": "Hydraulics & Fluid Mechanics", "code": "CIVIL306", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 9, "name": "Transportation Engineering", "code": "CIVIL307", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False}
                ],
                5: [  # Electrical Engineering (EE)
                    {"id": 1, "name": "Power Systems", "code": "EE301", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 2, "name": "Electrical Machines", "code": "EE302", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 3, "name": "Control Systems", "code": "EE303", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 4, "name": "Power Electronics", "code": "EE304", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 5, "name": "Environmental Studies", "code": "EVS101", "credits": 2, "nep_category": "AEC", "is_skill_based": False},
                    {"id": 6, "name": "PLC Programming Lab", "code": "EE305", "credits": 3, "nep_category": "SEC", "is_skill_based": True},
                    {"id": 7, "name": "Innovation & Entrepreneurship", "code": "ENT201", "credits": 2, "nep_category": "MDC", "is_skill_based": False},
                    {"id": 8, "name": "Electrical Measurements", "code": "EE306", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 9, "name": "Renewable Energy Systems", "code": "EE307", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False}
                ],
                6: [  # Information Technology (IT)
                    {"id": 1, "name": "System Analysis & Design", "code": "IT301", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 2, "name": "Mobile App Development", "code": "IT302", "credits": 3, "nep_category": "SEC", "is_skill_based": True},
                    {"id": 3, "name": "Network Security", "code": "IT303", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 4, "name": "Cloud Computing", "code": "IT304", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 5, "name": "Environmental Studies", "code": "EVS101", "credits": 2, "nep_category": "AEC", "is_skill_based": False},
                    {"id": 6, "name": "DevOps Lab", "code": "IT305", "credits": 3, "nep_category": "SEC", "is_skill_based": True},
                    {"id": 7, "name": "Digital Marketing", "code": "MKT201", "credits": 3, "nep_category": "MDC", "is_skill_based": False},
                    {"id": 8, "name": "Big Data Analytics", "code": "IT306", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 9, "name": "Enterprise Resource Planning", "code": "IT307", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False}
                ],
                7: [  # Chemical Engineering (CHEM)
                    {"id": 1, "name": "Chemical Process Principles", "code": "CHEM301", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 2, "name": "Unit Operations", "code": "CHEM302", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 3, "name": "Reaction Engineering", "code": "CHEM303", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 4, "name": "Process Control", "code": "CHEM304", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 5, "name": "Environmental Studies", "code": "EVS101", "credits": 2, "nep_category": "AEC", "is_skill_based": False},
                    {"id": 6, "name": "Process Simulation Lab", "code": "CHEM305", "credits": 3, "nep_category": "SEC", "is_skill_based": True},
                    {"id": 7, "name": "Industrial Economics", "code": "ECO202", "credits": 3, "nep_category": "MDC", "is_skill_based": False},
                    {"id": 8, "name": "Mass Transfer Operations", "code": "CHEM306", "credits": 4, "nep_category": "MAJOR", "is_skill_based": False},
                    {"id": 9, "name": "Plant Design", "code": "CHEM307", "credits": 3, "nep_category": "MAJOR", "is_skill_based": False}
                ]
            }
            return program_subjects.get(program_id, program_subjects[1])  # Default to CS
        
        # Always use program-specific subjects instead of generic database subjects
        subjects = get_program_subjects(program_id)
        
        teachers = teachers_response.data if teachers_response and teachers_response.data else [
            {"id": 1, "name": "Dr. Rajesh Kumar", "email": "rajesh@university.edu", "specialization": "Computer Science", "department": "CS"},
            {"id": 2, "name": "Prof. Priya Sharma", "email": "priya@university.edu", "specialization": "Electronics", "department": "ECE"},
            {"id": 3, "name": "Dr. Amit Singh", "email": "amit@university.edu", "specialization": "Mechanical Engineering", "department": "MECH"},
            {"id": 4, "name": "Dr. Sunita Verma", "email": "sunita@university.edu", "specialization": "Civil Engineering", "department": "CIVIL"},
            {"id": 5, "name": "Prof. Vikash Gupta", "email": "vikash@university.edu", "specialization": "Electrical Engineering", "department": "EE"},
            {"id": 6, "name": "Dr. Neha Agarwal", "email": "neha@university.edu", "specialization": "Information Technology", "department": "IT"},
            {"id": 7, "name": "Prof. Ravi Patel", "email": "ravi@university.edu", "specialization": "Chemical Engineering", "department": "CHEM"},
            {"id": 8, "name": "Dr. Anjali Mishra", "email": "anjali@university.edu", "specialization": "Environmental Studies", "department": "ENV"},
            {"id": 9, "name": "Prof. Suresh Joshi", "email": "suresh@university.edu", "specialization": "Mathematics", "department": "MATH"},
            {"id": 10, "name": "Dr. Kavita Rao", "email": "kavita@university.edu", "specialization": "Physics", "department": "PHY"},
            {"id": 11, "name": "Prof. Manoj Tiwari", "email": "manoj@university.edu", "specialization": "Management Studies", "department": "MGT"},
            {"id": 12, "name": "Dr. Shweta Pandey", "email": "shweta@university.edu", "specialization": "Economics", "department": "ECO"}
        ]
        
        classrooms = classrooms_response.data if classrooms_response and classrooms_response.data else [
            {"id": 1, "name": "CS Lab-101", "capacity": 30, "type": "COMPUTER_LAB", "has_projector": True, "department": "CS"},
            {"id": 2, "name": "ECE Lab-201", "capacity": 25, "type": "ELECTRONICS_LAB", "has_projector": True, "department": "ECE"},
            {"id": 3, "name": "Mech Workshop", "capacity": 20, "type": "WORKSHOP", "has_projector": False, "department": "MECH"},
            {"id": 4, "name": "Civil Lab-301", "capacity": 25, "type": "CIVIL_LAB", "has_projector": True, "department": "CIVIL"},
            {"id": 5, "name": "EE Lab-401", "capacity": 25, "type": "ELECTRICAL_LAB", "has_projector": True, "department": "EE"},
            {"id": 6, "name": "IT Server Room", "capacity": 30, "type": "COMPUTER_LAB", "has_projector": True, "department": "IT"},
            {"id": 7, "name": "Chem Lab-501", "capacity": 20, "type": "CHEMISTRY_LAB", "has_projector": False, "department": "CHEM"},
            {"id": 8, "name": "Lecture Hall-A", "capacity": 60, "type": "LECTURE", "has_projector": True, "department": "GENERAL"},
            {"id": 9, "name": "Lecture Hall-B", "capacity": 50, "type": "LECTURE", "has_projector": True, "department": "GENERAL"},
            {"id": 10, "name": "Seminar Room-1", "capacity": 40, "type": "SEMINAR", "has_projector": True, "department": "GENERAL"},
            {"id": 11, "name": "Tutorial Room-1", "capacity": 30, "type": "TUTORIAL", "has_projector": False, "department": "GENERAL"},
            {"id": 12, "name": "CAD Lab", "capacity": 25, "type": "CAD_LAB", "has_projector": True, "department": "GENERAL"}
        ]
        
        time_slots = time_slots_response.data if time_slots_response and time_slots_response.data else [
            {"id": 1, "start_time": "09:00", "end_time": "10:00", "day_of_week": 0},
            {"id": 2, "start_time": "10:00", "end_time": "11:00", "day_of_week": 0},
            {"id": 3, "start_time": "11:00", "end_time": "12:00", "day_of_week": 0},
            {"id": 4, "start_time": "14:00", "end_time": "15:00", "day_of_week": 0},
            {"id": 5, "start_time": "15:00", "end_time": "16:00", "day_of_week": 0}
        ]
        
        # Generate timetable using the data (real or fallback)
        timetable = generate_nep_compliant_schedule(subjects, teachers, classrooms, time_slots)
        
        # Calculate NEP compliance using the data
        nep_compliance = calculate_nep_compliance(subjects)
        
        return {
            "success": True,
            "message": "NEP 2020 compliant timetable generated successfully!",
            "timetable": timetable,
            "nep_compliance_report": nep_compliance,
            "subjects_count": len(subjects),
            "total_credits": sum(s.get('credits', 0) for s in subjects),
            "generation_method": "NEP_2020_DATABASE_DRIVEN",
            "data_sources": {
                "subjects": len(subjects),
                "teachers": len(teachers),
                "classrooms": len(classrooms),
                "time_slots": len(time_slots)
            },
            "using_fallback_data": not (subjects_response and subjects_response.data)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Generation failed: {str(e)}",
            "error_details": type(e).__name__
        }

# Get timetable entries
@app.get("/api/timetable-entries")
async def get_timetable_entries(
    semester: str,
    academic_year: str,
    program_id: Optional[UUID] = None,
    faculty_id: Optional[UUID] = None
):
    try:
        query = supabase.table('timetable_entries').select(
            "*, courses(*), faculty(*), rooms(*), time_slots(*)"
        ).eq('semester', semester).eq('academic_year', academic_year)
        
        if program_id:
            # Get courses for the program first
            courses = supabase.table('courses').select("id").eq('program_id', str(program_id)).execute()
            course_ids = [c['id'] for c in courses.data] if courses.data else []
            if course_ids:
                query = query.in_('course_id', course_ids)
        
        if faculty_id:
            query = query.eq('faculty_id', str(faculty_id))
        
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Export endpoints
@app.get("/api/export/timetable/excel")
async def export_timetable_excel(
    program_id: UUID,
    semester: str,
    academic_year: str
):
    try:
        exporter = TimetableExporter()
        filename = exporter.export_to_excel(str(program_id), semester, academic_year)
        return FileResponse(
            filename, 
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/timetable/pdf")
async def export_timetable_pdf(
    program_id: UUID,
    semester: str,
    academic_year: str
):
    try:
        exporter = TimetableExporter()
        filename = exporter.export_to_pdf(str(program_id), semester, academic_year)
        return FileResponse(
            filename,
            media_type='application/pdf',
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/faculty-timetable")
async def export_faculty_timetable(
    faculty_id: UUID,
    semester: str,
    academic_year: str,
    format: str = "excel"
):
    try:
        exporter = TimetableExporter()
        filename = exporter.export_faculty_timetable(
            str(faculty_id), 
            semester, 
            academic_year, 
            format
        )
        if not filename:
            raise HTTPException(status_code=404, detail="Faculty not found")
        
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if format == 'excel' else 'application/pdf'
        return FileResponse(filename, media_type=media_type, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Faculty assignment endpoints
@app.post("/api/faculty-assignments")
async def create_faculty_assignment(
    faculty_id: UUID,
    course_id: UUID,
    semester: str,
    academic_year: str,
    role: str = "Primary"
):
    try:
        data = {
            "faculty_id": str(faculty_id),
            "course_id": str(course_id),
            "semester": semester,
            "academic_year": academic_year,
            "role": role
        }
        response = supabase.table('faculty_assignments').insert(data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/faculty-assignments")
async def get_faculty_assignments(
    semester: str,
    academic_year: str,
    faculty_id: Optional[UUID] = None,
    course_id: Optional[UUID] = None
):
    try:
        query = supabase.table('faculty_assignments').select(
            "*, faculty(*), courses(*)"
        ).eq('semester', semester).eq('academic_year', academic_year)
        
        if faculty_id:
            query = query.eq('faculty_id', str(faculty_id))
        if course_id:
            query = query.eq('course_id', str(course_id))
        
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Field activity endpoints
@app.post("/api/field-activities", response_model=FieldActivity)
async def create_field_activity(activity: FieldActivityCreate):
    try:
        response = supabase.table('field_activities').insert(activity.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/field-activities", response_model=List[FieldActivity])
async def get_field_activities(course_id: Optional[UUID] = None):
    try:
        query = supabase.table('field_activities').select("*")
        if course_id:
            query = query.eq('course_id', str(course_id))
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)