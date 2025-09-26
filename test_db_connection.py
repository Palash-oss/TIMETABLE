#!/usr/bin/env python3
"""
Test database connection and verify setup
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()

def test_database():
    """Test database connection and data"""
    
    try:
        # Connect to Supabase
        supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )
        print("✅ Connected to Supabase successfully!")
        
        # Test each table
        tables = [
            'institutions', 'programs', 'semesters', 'subjects', 
            'teachers', 'classrooms', 'time_slots', 'subject_teacher_assignments'
        ]
        
        for table in tables:
            try:
                result = supabase.table(table).select('*').limit(5).execute()
                print(f"✅ {table}: {len(result.data)} records found")
                
                # Show first record for verification
                if result.data:
                    print(f"   Sample record: {result.data[0]}")
                    
            except Exception as e:
                print(f"❌ {table}: Error - {e}")
        
        print("\n🎯 Database setup verification complete!")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_database()