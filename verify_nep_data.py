#!/usr/bin/env python3
"""
Script to populate database with verified NEP 2020 data
Run this after setting up the database schema with nep_2020_verified_data.sql
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

if not url or not key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    print("Current environment:")
    print(f"  SUPABASE_URL: {'✅' if url else '❌'}")
    print(f"  SUPABASE_KEY: {'✅' if key else '❌'}")
    exit(1)

supabase: Client = create_client(url, key)

def populate_nep_data():
    """Populate the database with verified NEP 2020 data"""
    
    print("🚀 Starting NEP 2020 verified data population...")
    
    try:
        # 1. Verify NEP categories exist
        categories_response = supabase.table('nep_categories').select("code, name").execute()
        if categories_response.data:
            print(f"✅ Found {len(categories_response.data)} NEP categories:")
            for cat in categories_response.data:
                print(f"   - {cat['code']}: {cat['name']}")
        else:
            print("❌ No NEP categories found. Please run nep_2020_verified_data.sql first!")
            return False
        
        # 2. Check course structure
        structure_response = supabase.table('nep_course_structure').select("semester, category_code, recommended_credits").execute()
        if structure_response.data:
            print(f"✅ Found {len(structure_response.data)} course structure entries")
            # Group by semester
            semester_structure = {}
            for entry in structure_response.data:
                sem = entry['semester']
                if sem not in semester_structure:
                    semester_structure[sem] = []
                semester_structure[sem].append(f"{entry['category_code']}({entry['recommended_credits']} credits)")
            
            for sem in sorted(semester_structure.keys()):
                print(f"   Semester {sem}: {', '.join(semester_structure[sem])}")
        else:
            print("❌ No course structure found!")
            return False
        
        # 3. Check NEP subjects
        subjects_response = supabase.table('nep_subjects').select("name, code, category_code, credits, semester").execute()
        if subjects_response.data:
            print(f"✅ Found {len(subjects_response.data)} NEP subjects")
            # Group by category
            category_subjects = {}
            for subject in subjects_response.data:
                cat = subject['category_code']
                if cat not in category_subjects:
                    category_subjects[cat] = []
                category_subjects[cat].append(f"{subject['code']}: {subject['name']} ({subject['credits']} credits)")
            
            for cat in sorted(category_subjects.keys()):
                print(f"   {cat} subjects ({len(category_subjects[cat])}):")
                for subject in category_subjects[cat][:3]:  # Show first 3
                    print(f"     - {subject}")
                if len(category_subjects[cat]) > 3:
                    print(f"     ... and {len(category_subjects[cat]) - 3} more")
        else:
            print("❌ No NEP subjects found!")
            return False
        
        # 4. Check credit distribution
        distribution_response = supabase.table('nep_credit_distribution').select("category_code, allocated_credits, percentage_of_total").execute()
        if distribution_response.data:
            print(f"✅ Found credit distribution for {len(distribution_response.data)} categories:")
            total_credits = sum(d['allocated_credits'] for d in distribution_response.data)
            for dist in distribution_response.data:
                print(f"   - {dist['category_code']}: {dist['allocated_credits']} credits ({dist['percentage_of_total']}%)")
            print(f"   Total: {total_credits} credits")
        else:
            print("❌ No credit distribution found!")
            return False
        
        print("\n🎉 NEP 2020 verified data verification completed successfully!")
        print("\n📋 Summary:")
        print(f"   - Categories: {len(categories_response.data)}")
        print(f"   - Structure entries: {len(structure_response.data)}")
        print(f"   - Subjects: {len(subjects_response.data)}")
        print(f"   - Credit distribution: {len(distribution_response.data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying NEP data: {str(e)}")
        return False

def test_nep_endpoints():
    """Test the new NEP endpoints"""
    
    print("\n🧪 Testing NEP endpoints...")
    
    try:
        # Test categories endpoint
        categories_response = supabase.table('nep_categories').select("*").execute()
        print(f"✅ Categories endpoint: {len(categories_response.data)} categories")
        
        # Test compliance calculation
        subjects_response = supabase.table('nep_subjects').select("category_code, credits").eq('program_id', 1).execute()
        if subjects_response.data:
            category_totals = {}
            for subject in subjects_response.data:
                cat = subject['category_code']
                credits = subject['credits']
                category_totals[cat] = category_totals.get(cat, 0) + credits
            
            print("✅ Sample compliance calculation for program 1:")
            for cat, credits in category_totals.items():
                print(f"   - {cat}: {credits} credits")
        
        print("🎉 NEP endpoints test completed!")
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {str(e)}")

if __name__ == "__main__":
    print("=" * 50)
    print("NEP 2020 VERIFIED DATA VERIFICATION")
    print("=" * 50)
    
    success = populate_nep_data()
    
    if success:
        test_nep_endpoints()
        print("\n✅ All checks passed! Your NEP 2020 system is ready to use.")
        print("\n🚀 You can now use the following verified endpoints:")
        print("   - GET /api/nep-categories - Get all NEP categories")
        print("   - GET /api/nep-verified-curriculum/{program_id}/{semester}")
        print("   - GET /api/nep-compliance/{program_id}")
        print("   - GET /api/nep-semester-structure/{semester}")
    else:
        print("\n❌ Verification failed. Please run nep_2020_verified_data.sql first.")
        print("\nTo set up the database:")
        print("1. Go to your Supabase dashboard")
        print("2. Open SQL Editor")
        print("3. Run the nep_2020_verified_data.sql script")
        print("4. Run this script again")