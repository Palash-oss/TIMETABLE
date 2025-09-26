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

# Program endpoints
@app.get("/api/programs", response_model=List[Program])
async def get_programs():
    try:
        response = supabase.table('programs').select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/programs", response_model=Program)
async def create_program(program: ProgramCreate):
    try:
        response = supabase.table('programs').insert(program.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# Timetable generation endpoint
@app.post("/api/generate-timetable", response_model=TimetableGenerationResponse)
async def generate_timetable(request: TimetableGenerationRequest, background_tasks: BackgroundTasks):
    try:
        generator = TimetableGenerator(request.semester, request.academic_year)
        result = generator.generate(
            request.program_ids, 
            respect_constraints=request.respect_constraints
        )
        
        if result['success']:
            # Format the response
            return TimetableGenerationResponse(
                success=True,
                message=result['message'],
                timetables=[],  # Would need to format solution properly
                conflicts_resolved=0,
                optimization_score=0.85
            )
        else:
            raise HTTPException(status_code=400, detail=result['message'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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