import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io
from typing import List, Dict
from .database import supabase

class TimetableExporter:
    def __init__(self):
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        self.time_slots = []
        self.load_time_slots()
    
    def load_time_slots(self):
        """Load time slots from database"""
        response = supabase.table('time_slots').select("*").order('start_time').execute()
        if response.data:
            # Get unique time slots
            unique_slots = {}
            for slot in response.data:
                key = f"{slot['start_time']}-{slot['end_time']}"
                if key not in unique_slots:
                    unique_slots[key] = slot
            self.time_slots = list(unique_slots.values())
    
    def get_timetable_data(self, program_id: str, semester: str, academic_year: str):
        """Get timetable data for a specific program and semester"""
        # Get all courses for the program
        courses_response = supabase.table('courses').select("*").eq('program_id', program_id).eq('semester', int(semester)).execute()
        course_ids = [c['id'] for c in courses_response.data] if courses_response.data else []
        
        # Get timetable entries
        entries = []
        for course_id in course_ids:
            response = supabase.table('timetable_entries').select(
                "*, courses(*), faculty(*), rooms(*), time_slots(*)"
            ).eq('course_id', course_id).eq('semester', semester).eq('academic_year', academic_year).execute()
            
            if response.data:
                entries.extend(response.data)
        
        return entries
    
    def create_timetable_matrix(self, entries):
        """Create a matrix representation of the timetable"""
        # Initialize matrix
        matrix = {}
        for day in range(1, 7):  # Monday to Saturday
            matrix[day] = {}
            for slot in self.time_slots:
                slot_key = f"{slot['start_time']}-{slot['end_time']}"
                matrix[day][slot_key] = None
        
        # Fill matrix with entries
        for entry in entries:
            if entry.get('time_slots'):
                slot_data = entry['time_slots']
                day = slot_data['day_of_week']
                slot_key = f"{slot_data['start_time']}-{slot_data['end_time']}"
                
                if day in matrix and slot_key in matrix[day]:
                    course = entry.get('courses', {})
                    faculty = entry.get('faculty', {})
                    room = entry.get('rooms', {})
                    
                    matrix[day][slot_key] = {
                        'course_code': course.get('code', ''),
                        'course_name': course.get('name', ''),
                        'faculty_name': faculty.get('name', ''),
                        'room': room.get('room_number', ''),
                        'type': slot_data.get('slot_type', '')
                    }
        
        return matrix
    
    def export_to_excel(self, program_id: str, semester: str, academic_year: str, filename: str = None):
        """Export timetable to Excel format"""
        entries = self.get_timetable_data(program_id, semester, academic_year)
        matrix = self.create_timetable_matrix(entries)
        
        # Create DataFrame
        df_data = []
        time_slot_headers = [f"{slot['start_time']}-{slot['end_time']}" for slot in self.time_slots]
        
        for day_num in range(1, 7):
            row = [self.days[day_num - 1]]
            for slot in self.time_slots:
                slot_key = f"{slot['start_time']}-{slot['end_time']}"
                cell_data = matrix[day_num].get(slot_key)
                if cell_data:
                    cell_text = f"{cell_data['course_code']}\n{cell_data['course_name'][:30]}\n{cell_data['faculty_name']}\nRoom: {cell_data['room']}"
                else:
                    cell_text = ""
                row.append(cell_text)
            df_data.append(row)
        
        df = pd.DataFrame(df_data, columns=['Day'] + time_slot_headers)
        
        # Export to Excel
        if not filename:
            filename = f"timetable_{program_id}_{semester}_{academic_year}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Timetable', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Timetable']
            
            # Format cells
            for row in worksheet.iter_rows(min_row=2):
                for cell in row:
                    cell.alignment = cell.alignment.copy(wrap_text=True, vertical='center')
            
            # Adjust column widths
            worksheet.column_dimensions['A'].width = 15
            for col in worksheet.iter_cols(min_col=2, max_col=len(time_slot_headers) + 1):
                worksheet.column_dimensions[col[0].column_letter].width = 20
            
            # Adjust row heights
            for row in worksheet.iter_rows(min_row=2):
                worksheet.row_dimensions[row[0].row].height = 60
        
        return filename
    
    def export_to_pdf(self, program_id: str, semester: str, academic_year: str, filename: str = None):
        """Export timetable to PDF format"""
        entries = self.get_timetable_data(program_id, semester, academic_year)
        matrix = self.create_timetable_matrix(entries)
        
        if not filename:
            filename = f"timetable_{program_id}_{semester}_{academic_year}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filename,
            pagesize=landscape(A4),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=16,
            spaceAfter=30
        )
        
        # Get program details
        program_response = supabase.table('programs').select("*").eq('id', program_id).execute()
        program_name = program_response.data[0]['name'] if program_response.data else "Unknown Program"
        
        title = Paragraph(
            f"<b>{program_name} - Semester {semester}</b><br/>Academic Year: {academic_year}",
            title_style
        )
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Create table data
        table_data = [['Day/Time'] + [f"{slot['start_time'][:5]}-{slot['end_time'][:5]}" for slot in self.time_slots]]
        
        for day_num in range(1, 7):
            row = [self.days[day_num - 1]]
            for slot in self.time_slots:
                slot_key = f"{slot['start_time']}-{slot['end_time']}"
                cell_data = matrix[day_num].get(slot_key)
                if cell_data:
                    cell_content = Paragraph(
                        f"<b>{cell_data['course_code']}</b><br/>"
                        f"{cell_data['course_name'][:25]}<br/>"
                        f"<i>{cell_data['faculty_name']}</i><br/>"
                        f"Room: {cell_data['room']}",
                        styles['Normal']
                    )
                else:
                    cell_content = ""
                row.append(cell_content)
            table_data.append(row)
        
        # Create table
        table = Table(table_data, repeatRows=1)
        
        # Apply table style
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ])
        
        # Apply alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (1, i), (-1, i), colors.lightgrey)
        
        table.setStyle(table_style)
        elements.append(table)
        
        # Add footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=8,
            textColor=colors.grey
        )
        
        footer = Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            footer_style
        )
        elements.append(Spacer(1, 20))
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        return filename
    
    def export_faculty_timetable(self, faculty_id: str, semester: str, academic_year: str, format: str = 'excel'):
        """Export timetable for a specific faculty member"""
        # Get faculty details
        faculty_response = supabase.table('faculty').select("*").eq('id', faculty_id).execute()
        faculty = faculty_response.data[0] if faculty_response.data else None
        
        if not faculty:
            return None
        
        # Get timetable entries for faculty
        entries_response = supabase.table('timetable_entries').select(
            "*, courses(*), rooms(*), time_slots(*)"
        ).eq('faculty_id', faculty_id).eq('semester', semester).eq('academic_year', academic_year).execute()
        
        entries = entries_response.data if entries_response.data else []
        
        # Create matrix for faculty
        matrix = {}
        for day in range(1, 7):
            matrix[day] = {}
            for slot in self.time_slots:
                slot_key = f"{slot['start_time']}-{slot['end_time']}"
                matrix[day][slot_key] = None
        
        for entry in entries:
            if entry.get('time_slots'):
                slot_data = entry['time_slots']
                day = slot_data['day_of_week']
                slot_key = f"{slot_data['start_time']}-{slot_data['end_time']}"
                
                if day in matrix and slot_key in matrix[day]:
                    course = entry.get('courses', {})
                    room = entry.get('rooms', {})
                    
                    matrix[day][slot_key] = {
                        'course_code': course.get('code', ''),
                        'course_name': course.get('name', ''),
                        'room': room.get('room_number', ''),
                        'type': slot_data.get('slot_type', '')
                    }
        
        # Export based on format
        if format == 'excel':
            return self._export_faculty_excel(faculty, matrix, semester, academic_year)
        else:
            return self._export_faculty_pdf(faculty, matrix, semester, academic_year)
    
    def _export_faculty_excel(self, faculty, matrix, semester, academic_year):
        """Export faculty timetable to Excel"""
        df_data = []
        time_slot_headers = [f"{slot['start_time']}-{slot['end_time']}" for slot in self.time_slots]
        
        for day_num in range(1, 7):
            row = [self.days[day_num - 1]]
            for slot in self.time_slots:
                slot_key = f"{slot['start_time']}-{slot['end_time']}"
                cell_data = matrix[day_num].get(slot_key)
                if cell_data:
                    cell_text = f"{cell_data['course_code']}\n{cell_data['course_name'][:30]}\nRoom: {cell_data['room']}"
                else:
                    cell_text = ""
                row.append(cell_text)
            df_data.append(row)
        
        df = pd.DataFrame(df_data, columns=['Day'] + time_slot_headers)
        
        filename = f"faculty_timetable_{faculty['employee_id']}_{semester}_{academic_year}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=faculty['name'], index=False)
            
            # Format the Excel file
            workbook = writer.book
            worksheet = writer.sheets[faculty['name']]
            
            for row in worksheet.iter_rows(min_row=2):
                for cell in row:
                    cell.alignment = cell.alignment.copy(wrap_text=True, vertical='center')
            
            worksheet.column_dimensions['A'].width = 15
            for col in worksheet.iter_cols(min_col=2, max_col=len(time_slot_headers) + 1):
                worksheet.column_dimensions[col[0].column_letter].width = 20
            
            for row in worksheet.iter_rows(min_row=2):
                worksheet.row_dimensions[row[0].row].height = 50
        
        return filename