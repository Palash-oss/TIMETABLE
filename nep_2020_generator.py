"""
NEP 2020 Compliant Timetable Generator
Handles multidisciplinary courses, flexible credit system, and choice-based curriculum
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import json

@dataclass
class NEPCourse:
    """NEP 2020 compliant course structure"""
    id: int
    name: str
    code: str
    credits: int
    nep_category: str  # MAJOR, MINOR, AEC, SEC, VAC, MDC, OE, PROJECT
    semester: int
    is_skill_based: bool = False
    is_research_component: bool = False
    prerequisite_courses: List[str] = None
    
class NEP2020TimetableGenerator:
    """
    Timetable generator compliant with NEP 2020 guidelines
    """
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.nep_credit_distribution = {
            'MAJOR': 80,      # Major discipline courses
            'MINOR': 40,      # Minor/Optional courses  
            'AEC': 8,         # Ability Enhancement Courses
            'SEC': 12,        # Skill Enhancement Courses
            'VAC': 4,         # Value Added Courses
            'MDC': 16,        # Multidisciplinary Courses
            'PROJECT': 8      # Research/Project work
        }
    
    def get_nep_compliant_curriculum(self, program_id: int, semester: int) -> Dict:
        """Get NEP 2020 compliant curriculum for a semester"""
        
        # Get subjects by NEP category
        subjects = self.supabase.table('subjects').select("""
            *,
            semesters!inner(semester_number, programs!inner(id))
        """).eq('semesters.programs.id', program_id).eq('semesters.semester_number', semester).execute()
        
        curriculum = {
            'semester': semester,
            'courses': subjects.data,
            'credit_distribution': self._calculate_credit_distribution(subjects.data),
            'nep_compliance': self._check_nep_compliance(subjects.data, semester)
        }
        
        return curriculum
    
    def _calculate_credit_distribution(self, subjects: List[Dict]) -> Dict:
        """Calculate credit distribution by NEP categories"""
        distribution = {}
        for subject in subjects:
            category = subject.get('nep_category', 'MAJOR')
            distribution[category] = distribution.get(category, 0) + subject.get('credits', 0)
        
        return distribution
    
    def _check_nep_compliance(self, subjects: List[Dict], semester: int) -> Dict:
        """Check if curriculum meets NEP 2020 requirements"""
        total_credits = sum(subject.get('credits', 0) for subject in subjects)
        
        compliance = {
            'total_credits': total_credits,
            'recommended_credits_per_semester': 20,
            'is_compliant': total_credits >= 18 and total_credits <= 22,
            'has_multidisciplinary': any(s.get('nep_category') == 'MDC' for s in subjects),
            'has_skill_component': any(s.get('is_skill_based') for s in subjects),
            'semester': semester
        }
        
        # Check final year research requirement
        if semester >= 7:
            compliance['has_research_component'] = any(s.get('is_research_component') for s in subjects)
        
        return compliance
    
    def generate_nep_timetable(self, program_id: int, semester: int) -> Dict:
        """Generate NEP 2020 compliant timetable"""
        
        # Get curriculum data
        curriculum = self.get_nep_compliant_curriculum(program_id, semester)
        
        # Get available resources
        teachers = self.supabase.table('teachers').select('*').execute()
        classrooms = self.supabase.table('classrooms').select('*').execute()
        time_slots = self.supabase.table('time_slots').select('*').execute()
        
        # Generate timetable with NEP considerations
        timetable = self._create_balanced_schedule(
            curriculum['courses'], 
            teachers.data, 
            classrooms.data, 
            time_slots.data,
            semester
        )
        
        return {
            'semester': semester,
            'curriculum': curriculum,
            'timetable': timetable,
            'nep_compliance_report': self._generate_compliance_report(curriculum)
        }
    
    def _create_balanced_schedule(self, courses, teachers, classrooms, time_slots, semester):
        """Create a balanced schedule considering NEP requirements"""
        schedule = {}
        
        # Prioritize courses by NEP category importance
        priority_order = ['MAJOR', 'AEC', 'SEC', 'MDC', 'MINOR', 'VAC', 'PROJECT']
        
        sorted_courses = sorted(courses, 
                              key=lambda x: priority_order.index(x.get('nep_category', 'MAJOR')))
        
        for day in range(5):  # Monday to Friday
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][day]
            schedule[day_name] = []
            
            # Balance different NEP categories throughout the week
            daily_slots = [slot for slot in time_slots if slot['day_of_week'] == day]
            
            for i, slot in enumerate(daily_slots[:6]):  # Max 6 periods per day
                if i < len(sorted_courses):
                    course = sorted_courses[i % len(sorted_courses)]
                    
                    # Assign teacher and classroom
                    assigned_teacher = self._assign_teacher(course, teachers)
                    assigned_classroom = self._assign_classroom(course, classrooms)
                    
                    schedule[day_name].append({
                        'time_slot': f"{slot['start_time']}-{slot['end_time']}",
                        'course': course,
                        'teacher': assigned_teacher,
                        'classroom': assigned_classroom,
                        'nep_category': course.get('nep_category', 'MAJOR'),
                        'is_skill_based': course.get('is_skill_based', False)
                    })
        
        return schedule
    
    def _assign_teacher(self, course, teachers):
        """Smart teacher assignment based on specialization"""
        for teacher in teachers:
            if (teacher.get('department', '').lower() in course.get('name', '').lower() or
                course.get('code', '')[:3] in teacher.get('specialization', '')):
                return teacher
        return teachers[0] if teachers else None
    
    def _assign_classroom(self, course, classrooms):
        """Smart classroom assignment based on course type"""
        course_name = course.get('name', '').lower()
        
        # Lab courses need lab rooms
        if 'lab' in course_name or 'practical' in course_name:
            for classroom in classrooms:
                if classroom.get('room_type') == 'lab':
                    return classroom
        
        # Regular courses need lecture halls
        for classroom in classrooms:
            if classroom.get('room_type') == 'lecture':
                return classroom
                
        return classrooms[0] if classrooms else None
    
    def _generate_compliance_report(self, curriculum):
        """Generate NEP 2020 compliance report"""
        compliance = curriculum['nep_compliance']
        credit_dist = curriculum['credit_distribution']
        
        report = {
            'overall_compliance': compliance['is_compliant'],
            'credit_analysis': {
                'total_credits': compliance['total_credits'],
                'target_range': '18-22 per semester',
                'distribution': credit_dist
            },
            'nep_requirements': {
                'multidisciplinary_courses': compliance.get('has_multidisciplinary', False),
                'skill_based_learning': compliance.get('has_skill_component', False),
                'research_component': compliance.get('has_research_component', False)
            },
            'recommendations': self._get_recommendations(compliance, credit_dist)
        }
        
        return report
    
    def _get_recommendations(self, compliance, credit_dist):
        """Get recommendations for NEP compliance"""
        recommendations = []
        
        if compliance['total_credits'] < 18:
            recommendations.append("Add more courses to meet minimum 18 credits per semester")
        
        if compliance['total_credits'] > 22:
            recommendations.append("Consider reducing course load to stay within 22 credits")
        
        if not compliance.get('has_multidisciplinary'):
            recommendations.append("Add multidisciplinary courses (MDC) for holistic education")
        
        if not compliance.get('has_skill_component'):
            recommendations.append("Include skill enhancement courses (SEC) for employability")
        
        if credit_dist.get('MAJOR', 0) < 8:
            recommendations.append("Increase major discipline courses for depth")
        
        return recommendations

# Usage example
def create_nep_compliant_sample():
    """Create sample NEP 2020 compliant data"""
    return {
        "sample_courses": [
            {
                "name": "Data Structures and Algorithms",
                "code": "CS201", 
                "credits": 4,
                "nep_category": "MAJOR",
                "is_skill_based": True
            },
            {
                "name": "Environmental Science",
                "code": "EVS101",
                "credits": 2, 
                "nep_category": "VAC",
                "is_skill_based": False
            },
            {
                "name": "Communication Skills",
                "code": "ENG101",
                "credits": 3,
                "nep_category": "AEC", 
                "is_skill_based": True
            },
            {
                "name": "Digital Marketing",
                "code": "MKT201",
                "credits": 3,
                "nep_category": "SEC",
                "is_skill_based": True
            },
            {
                "name": "Psychology of Learning",
                "code": "PSY101", 
                "credits": 3,
                "nep_category": "MDC",
                "is_skill_based": False
            },
            {
                "name": "Research Methodology",
                "code": "RES401",
                "credits": 4,
                "nep_category": "PROJECT",
                "is_research_component": True
            }
        ]
    }

if __name__ == "__main__":
    print("NEP 2020 Compliant Timetable Generator Ready!")
    sample = create_nep_compliant_sample()
    print(f"Sample courses: {len(sample['sample_courses'])}")
    print("Categories covered:", set(course['nep_category'] for course in sample['sample_courses']))