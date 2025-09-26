from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, time, date
from uuid import UUID
from enum import Enum

class ProgramType(str, Enum):
    BED = "B.Ed."
    MED = "M.Ed."
    FYUP = "FYUP"
    ITEP = "ITEP"

class CourseType(str, Enum):
    CORE = "Core"
    ELECTIVE = "Elective"
    AEC = "AEC"
    SEC = "SEC"
    VAC = "VAC"

class RoomType(str, Enum):
    CLASSROOM = "Classroom"
    LAB = "Lab"
    SEMINAR_HALL = "Seminar Hall"

class SlotType(str, Enum):
    THEORY = "Theory"
    PRACTICAL = "Practical"
    TUTORIAL = "Tutorial"

class ActivityType(str, Enum):
    TEACHING_PRACTICE = "Teaching Practice"
    INTERNSHIP = "Internship"
    FIELD_WORK = "Field Work"

# Program Models
class ProgramBase(BaseModel):
    name: str
    code: str
    type: ProgramType
    duration_years: int
    total_credits: int

class ProgramCreate(ProgramBase):
    pass

class Program(ProgramBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Faculty Models
class FacultyBase(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    department: Optional[str] = None
    expertise: List[str] = []
    max_hours_per_week: int = 20
    availability: Optional[Dict[str, Any]] = None

class FacultyCreate(FacultyBase):
    pass

class Faculty(FacultyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Course Models
class CourseBase(BaseModel):
    code: str
    name: str
    program_id: UUID
    semester: int
    credits: int
    theory_hours: int = 0
    practical_hours: int = 0
    tutorial_hours: int = 0
    course_type: Optional[CourseType] = None
    prerequisites: List[str] = []

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Room Models
class RoomBase(BaseModel):
    room_number: str
    building: Optional[str] = None
    capacity: int
    room_type: RoomType
    facilities: List[str] = []
    is_available: bool = True

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Student Models
class StudentBase(BaseModel):
    student_id: str
    name: str
    email: EmailStr
    program_id: UUID
    semester: int
    enrolled_credits: int = 0

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Time Slot Models
class TimeSlotBase(BaseModel):
    day_of_week: int = Field(ge=1, le=7)  # 1=Monday, 7=Sunday
    start_time: time
    end_time: time
    slot_type: SlotType

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlot(TimeSlotBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Timetable Entry Models
class TimetableEntryBase(BaseModel):
    course_id: UUID
    faculty_id: UUID
    room_id: UUID
    time_slot_id: UUID
    semester: str
    academic_year: str
    section: Optional[str] = None

class TimetableEntryCreate(TimetableEntryBase):
    pass

class TimetableEntry(TimetableEntryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Constraint Models
class ConstraintBase(BaseModel):
    constraint_type: str
    entity_id: Optional[UUID] = None
    description: str
    priority: int = Field(ge=1, le=10, default=5)
    is_hard_constraint: bool = False
    metadata: Optional[Dict[str, Any]] = None

class ConstraintCreate(ConstraintBase):
    pass

class Constraint(ConstraintBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Field Activity Models
class FieldActivityBase(BaseModel):
    course_id: UUID
    activity_type: ActivityType
    duration_weeks: int
    start_date: date
    end_date: date
    location: Optional[str] = None
    supervisor_id: Optional[UUID] = None

class FieldActivityCreate(FieldActivityBase):
    pass

class FieldActivity(FieldActivityBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Timetable Generation Request
class TimetableGenerationRequest(BaseModel):
    semester: str
    academic_year: str
    program_ids: List[UUID]
    respect_constraints: bool = True
    optimize_for: str = "balanced"  # balanced, minimal_gaps, faculty_preference

# Timetable Response Models
class TimetableSlot(BaseModel):
    time_slot: TimeSlot
    course: Optional[Course] = None
    faculty: Optional[Faculty] = None
    room: Optional[Room] = None
    section: Optional[str] = None

class DaySchedule(BaseModel):
    day: int
    slots: List[TimetableSlot]

class WeeklyTimetable(BaseModel):
    program: Program
    semester: str
    academic_year: str
    schedule: List[DaySchedule]

class TimetableGenerationResponse(BaseModel):
    success: bool
    message: str
    timetables: List[WeeklyTimetable]
    conflicts_resolved: int = 0
    optimization_score: float = 0.0