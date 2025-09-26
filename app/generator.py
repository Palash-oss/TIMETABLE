from ortools.sat.python import cp_model
from typing import List, Dict, Tuple, Any
import numpy as np
from datetime import time
from uuid import UUID
from .models import *
from .database import supabase

class TimetableGenerator:
    def __init__(self, semester: str, academic_year: str):
        self.semester = semester
        self.academic_year = academic_year
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
        # Load data from database
        self.courses = []
        self.faculty = []
        self.rooms = []
        self.time_slots = []
        self.constraints = []
        self.assignments = {}
        
    def load_data(self, program_ids: List[UUID]):
        """Load all necessary data from database"""
        try:
            # Load courses for specified programs
            for program_id in program_ids:
                response = supabase.table('courses').select("*").eq('program_id', str(program_id)).execute()
                self.courses.extend(response.data)
            
            # Load faculty
            response = supabase.table('faculty').select("*").execute()
            self.faculty = response.data
            
            # Load rooms
            response = supabase.table('rooms').select("*").eq('is_available', True).execute()
            self.rooms = response.data
            
            # Load time slots
            response = supabase.table('time_slots').select("*").execute()
            self.time_slots = response.data
            
            # Load constraints
            response = supabase.table('constraints').select("*").execute()
            self.constraints = response.data
            
            # Load faculty assignments
            response = supabase.table('faculty_assignments').select("*").eq('semester', self.semester).eq('academic_year', self.academic_year).execute()
            for assignment in response.data:
                if assignment['course_id'] not in self.assignments:
                    self.assignments[assignment['course_id']] = []
                self.assignments[assignment['course_id']].append(assignment['faculty_id'])
                
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def create_variables(self):
        """Create decision variables for the model"""
        self.schedule = {}
        
        for course in self.courses:
            course_id = course['id']
            total_hours = course['theory_hours'] + course['practical_hours'] + course['tutorial_hours']
            
            # Skip if no hours allocated
            if total_hours == 0:
                continue
                
            for slot in self.time_slots:
                slot_id = slot['id']
                
                for room in self.rooms:
                    room_id = room['id']
                    
                    # Check room capacity and type compatibility
                    if not self._is_room_suitable(course, room, slot):
                        continue
                    
                    # Get assigned faculty for this course
                    if course_id in self.assignments:
                        for faculty_id in self.assignments[course_id]:
                            # Create boolean variable
                            var_name = f"c{course_id}_s{slot_id}_r{room_id}_f{faculty_id}"
                            self.schedule[var_name] = {
                                'var': self.model.NewBoolVar(var_name),
                                'course_id': course_id,
                                'slot_id': slot_id,
                                'room_id': room_id,
                                'faculty_id': faculty_id,
                                'course': course,
                                'slot': slot,
                                'room': room
                            }
    
    def _is_room_suitable(self, course, room, slot):
        """Check if room is suitable for the course and slot type"""
        # Check capacity
        enrollments = supabase.table('enrollments').select("*").eq('course_id', course['id']).execute()
        student_count = len(enrollments.data) if enrollments.data else 30  # Default to 30
        
        if room['capacity'] < student_count:
            return False
        
        # Check room type compatibility
        if slot['slot_type'] == 'Practical' and room['room_type'] != 'Lab':
            return False
        
        if slot['slot_type'] == 'Theory' and room['room_type'] == 'Lab':
            return False  # Avoid using labs for theory classes
            
        return True
    
    def add_constraints(self):
        """Add all constraints to the model"""
        
        # 1. Each course must be scheduled for its required hours
        self._add_course_hours_constraint()
        
        # 2. No faculty can be in two places at once
        self._add_faculty_conflict_constraint()
        
        # 3. No room can be used for two courses at once
        self._add_room_conflict_constraint()
        
        # 4. Respect faculty availability
        self._add_faculty_availability_constraint()
        
        # 5. Apply custom constraints from database
        self._add_custom_constraints()
        
        # 6. Distribute course sessions across the week
        self._add_distribution_constraint()
        
        # 7. Limit consecutive hours for a course
        self._add_consecutive_hours_constraint()
    
    def _add_course_hours_constraint(self):
        """Ensure each course is scheduled for required hours"""
        course_hours = {}
        
        for key, data in self.schedule.items():
            course_id = data['course_id']
            course = data['course']
            
            if course_id not in course_hours:
                course_hours[course_id] = {
                    'vars': [],
                    'required_hours': 0
                }
            
            course_hours[course_id]['vars'].append(data['var'])
            
            # Calculate required weekly hours
            total_hours = course['theory_hours'] + course['practical_hours'] + course['tutorial_hours']
            course_hours[course_id]['required_hours'] = total_hours // 15  # Assuming 15-week semester
        
        # Add constraint for each course
        for course_id, info in course_hours.items():
            if info['required_hours'] > 0:
                self.model.Add(sum(info['vars']) == info['required_hours'])
    
    def _add_faculty_conflict_constraint(self):
        """No faculty can teach two courses at the same time"""
        faculty_slots = {}
        
        for key, data in self.schedule.items():
            faculty_id = data['faculty_id']
            slot_id = data['slot_id']
            
            key = f"{faculty_id}_{slot_id}"
            if key not in faculty_slots:
                faculty_slots[key] = []
            faculty_slots[key].append(data['var'])
        
        # At most one course per faculty per time slot
        for key, vars in faculty_slots.items():
            if len(vars) > 1:
                self.model.Add(sum(vars) <= 1)
    
    def _add_room_conflict_constraint(self):
        """No room can be used for two courses at the same time"""
        room_slots = {}
        
        for key, data in self.schedule.items():
            room_id = data['room_id']
            slot_id = data['slot_id']
            
            key = f"{room_id}_{slot_id}"
            if key not in room_slots:
                room_slots[key] = []
            room_slots[key].append(data['var'])
        
        # At most one course per room per time slot
        for key, vars in room_slots.items():
            if len(vars) > 1:
                self.model.Add(sum(vars) <= 1)
    
    def _add_faculty_availability_constraint(self):
        """Respect faculty availability preferences"""
        for key, data in self.schedule.items():
            faculty_id = data['faculty_id']
            slot = data['slot']
            
            # Find faculty data
            faculty_data = next((f for f in self.faculty if f['id'] == faculty_id), None)
            if faculty_data and faculty_data.get('availability'):
                availability = faculty_data['availability']
                
                # Check if this slot is available
                day = slot['day_of_week']
                start_time = slot['start_time']
                
                if str(day) in availability:
                    day_availability = availability[str(day)]
                    if not day_availability.get('available', True):
                        self.model.Add(data['var'] == 0)
    
    def _add_custom_constraints(self):
        """Apply custom constraints from database"""
        for constraint in self.constraints:
            if constraint['is_hard_constraint']:
                self._apply_hard_constraint(constraint)
    
    def _apply_hard_constraint(self, constraint):
        """Apply a specific hard constraint"""
        # Implementation depends on constraint type
        pass
    
    def _add_distribution_constraint(self):
        """Distribute course sessions across the week"""
        course_days = {}
        
        for key, data in self.schedule.items():
            course_id = data['course_id']
            day = data['slot']['day_of_week']
            
            if course_id not in course_days:
                course_days[course_id] = {}
            if day not in course_days[course_id]:
                course_days[course_id][day] = []
            course_days[course_id][day].append(data['var'])
        
        # Limit sessions per day for each course
        for course_id, days in course_days.items():
            for day, vars in days.items():
                if len(vars) > 2:  # Max 2 sessions per day
                    self.model.Add(sum(vars) <= 2)
    
    def _add_consecutive_hours_constraint(self):
        """Limit consecutive hours for a course"""
        # Group by course and day
        course_day_slots = {}
        
        for key, data in self.schedule.items():
            course_id = data['course_id']
            day = data['slot']['day_of_week']
            start_time = data['slot']['start_time']
            
            key = f"{course_id}_{day}"
            if key not in course_day_slots:
                course_day_slots[key] = []
            course_day_slots[key].append((start_time, data['var']))
        
        # Sort by time and check consecutive slots
        for key, slots in course_day_slots.items():
            slots.sort(key=lambda x: x[0])
            
            # Limit to max 3 consecutive hours
            for i in range(len(slots) - 2):
                consecutive_vars = [slots[i][1], slots[i+1][1], slots[i+2][1]]
                self.model.Add(sum(consecutive_vars) <= 2)
    
    def solve(self, time_limit=60):
        """Solve the timetable generation problem"""
        self.solver.parameters.max_time_in_seconds = time_limit
        status = self.solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return self._extract_solution()
        else:
            return None
    
    def _extract_solution(self):
        """Extract the solution from solved model"""
        solution = []
        
        for key, data in self.schedule.items():
            if self.solver.Value(data['var']) == 1:
                entry = {
                    'course_id': data['course_id'],
                    'faculty_id': data['faculty_id'],
                    'room_id': data['room_id'],
                    'time_slot_id': data['slot_id'],
                    'semester': self.semester,
                    'academic_year': self.academic_year,
                    'course': data['course'],
                    'slot': data['slot'],
                    'room': data['room']
                }
                solution.append(entry)
        
        return solution
    
    def save_to_database(self, solution):
        """Save the generated timetable to database"""
        try:
            # Clear existing entries for this semester
            supabase.table('timetable_entries').delete().eq('semester', self.semester).eq('academic_year', self.academic_year).execute()
            
            # Insert new entries
            for entry in solution:
                data = {
                    'course_id': entry['course_id'],
                    'faculty_id': entry['faculty_id'],
                    'room_id': entry['room_id'],
                    'time_slot_id': entry['time_slot_id'],
                    'semester': entry['semester'],
                    'academic_year': entry['academic_year']
                }
                supabase.table('timetable_entries').insert(data).execute()
            
            return True
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
            return False
    
    def generate(self, program_ids: List[UUID], respect_constraints: bool = True):
        """Main method to generate timetable"""
        try:
            # Load data
            self.load_data(program_ids)
            
            # Create variables
            self.create_variables()
            
            # Add constraints
            if respect_constraints:
                self.add_constraints()
            
            # Solve
            solution = self.solve()
            
            if solution:
                # Save to database
                self.save_to_database(solution)
                return {
                    'success': True,
                    'solution': solution,
                    'message': 'Timetable generated successfully'
                }
            else:
                return {
                    'success': False,
                    'solution': None,
                    'message': 'Could not find a feasible solution'
                }
        except Exception as e:
            return {
                'success': False,
                'solution': None,
                'message': f'Error generating timetable: {str(e)}'
            }