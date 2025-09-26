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
    """Generate NEP 2020 compliant schedule"""
    schedule = {}
    
    # NEP category priority order
    nep_priority = ['MAJOR', 'AEC', 'SEC', 'MDC', 'MINOR', 'VAC', 'PROJECT']
    
    # Sort subjects by NEP priority
    sorted_subjects = sorted(subjects, 
                           key=lambda x: nep_priority.index(x.get('nep_category', 'MAJOR')) 
                           if x.get('nep_category', 'MAJOR') in nep_priority else len(nep_priority))
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for day_idx, day in enumerate(days):
        schedule[day] = []
        
        # Get time slots for this day
        day_slots = [slot for slot in time_slots if slot.get('day_of_week') == day_idx]
        
        for slot_idx, time_slot in enumerate(day_slots[:6]):  # Max 6 periods
            if slot_idx < len(sorted_subjects):
                subject = sorted_subjects[slot_idx % len(sorted_subjects)]
                
                # Smart teacher assignment
                assigned_teacher = assign_teacher_by_expertise(subject, teachers)
                
                # Smart classroom assignment  
                assigned_classroom = assign_classroom_by_type(subject, classrooms)
                
                schedule[day].append({
                    'time': f"{time_slot.get('start_time', '09:00')}-{time_slot.get('end_time', '10:00')}",
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
    """Assign teacher based on subject and expertise"""
    subject_name = subject.get('name', '').lower()
    subject_code = subject.get('code', '')
    
    # First, try to match by department/specialization
    for teacher in teachers:
        specialization = teacher.get('specialization', '').lower()
        department = teacher.get('department', '').lower()
        
        if (department in subject_name or 
            subject_code[:2].lower() in specialization or
            any(word in specialization for word in subject_name.split())):
            return teacher
    
    # Return first available teacher
    return teachers[0] if teachers else None

def assign_classroom_by_type(subject, classrooms):
    """Assign classroom based on subject type"""
    subject_name = subject.get('name', '').lower()
    
    # Lab subjects need lab rooms
    if ('lab' in subject_name or 'practical' in subject_name or 
        subject.get('is_skill_based', False)):
        for classroom in classrooms:
            if classroom.get('room_type') == 'lab':
                return classroom
    
    # Regular subjects need lecture rooms
    for classroom in classrooms:
        if classroom.get('room_type') == 'lecture':
            return classroom
            
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
        
        # Get real subjects from database
        subjects_response = supabase.table('subjects').select("""
            *,
            semesters!inner(semester_number, programs!inner(id, name))
        """).eq('semesters.programs.id', program_id).eq('semesters.semester_number', semester).execute()
        
        # Get real teachers from database
        teachers_response = supabase.table('teachers').select("*").execute()
        
        # Get real classrooms from database
        classrooms_response = supabase.table('classrooms').select("*").execute()
        
        # Get real time slots from database
        time_slots_response = supabase.table('time_slots').select("*").execute()
        
        subjects = subjects_response.data
        teachers = teachers_response.data
        classrooms = classrooms_response.data
        time_slots = time_slots_response.data
        
        # Check if we have data
        if not subjects:
            return {
                "success": False,
                "message": "No subjects found for the specified program and semester",
                "data_status": "insufficient"
            }
        
        if not teachers:
            return {
                "success": False,
                "message": "No teachers found in the database",
                "data_status": "insufficient"
            }
        
        if not classrooms:
            return {
                "success": False,
                "message": "No classrooms found in the database",
                "data_status": "insufficient"
            }
        
        if not time_slots:
            return {
                "success": False,
                "message": "No time slots found in the database",
                "data_status": "insufficient"
            }
        
        # Generate timetable using real data
        timetable = generate_nep_compliant_schedule(subjects, teachers, classrooms, time_slots)
        
        # Calculate NEP compliance using real data
        nep_compliance = calculate_nep_compliance(subjects)
        
        return {
            "success": True,
            "message": "NEP 2020 compliant timetable generated successfully using real database data!",
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
            }
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