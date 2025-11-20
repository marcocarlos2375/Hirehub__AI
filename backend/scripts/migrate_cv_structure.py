"""
Database migration script to convert old CV structure to new structure.

Old Structure:
- personal_info: {name, email, phone, location, linkedin, github, portfolio}
- skills: {technical_skills: [], tools: [], soft_skills: []}
- experience: [{company, role, duration, location, achievements}]
- years_of_experience: int

New Structure:
- personalInfo: {firstName, lastName, jobTitle, email, phone, address, socialLinks: []}
- skills: [{skill, level, category}]
- employmentHistory: [{position, company, startDate, endDate, currentlyWorking, responsibilities}]
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import CVAnalysis
from app.config import get_settings
import json

settings = get_settings()

# Create database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def parse_name(full_name):
    """Split full name into first and last name"""
    if not full_name:
        return None, None

    parts = full_name.strip().split()
    if len(parts) == 0:
        return None, None
    elif len(parts) == 1:
        return parts[0], None
    else:
        return parts[0], ' '.join(parts[1:])

def convert_skills(old_skills):
    """Convert old skills structure to new array format"""
    new_skills = []

    if not old_skills:
        return new_skills

    # Technical skills
    for skill in old_skills.get('technical_skills', []):
        new_skills.append({
            'skill': skill,
            'level': 'Intermediate',
            'category': 'Programming Languages'
        })

    # Tools
    for tool in old_skills.get('tools', []):
        new_skills.append({
            'skill': tool,
            'level': 'Intermediate',
            'category': 'DevOps & Tools'
        })

    # Soft skills
    for soft_skill in old_skills.get('soft_skills', []):
        new_skills.append({
            'skill': soft_skill,
            'level': 'Advanced',
            'category': 'Soft Skills'
        })

    return new_skills

def parse_duration(duration_str):
    """Parse duration string like '2020 - 2023' into startDate and endDate"""
    if not duration_str:
        return None, None, False

    duration_str = duration_str.strip()

    # Check if currently working
    currently_working = 'present' in duration_str.lower() or 'current' in duration_str.lower()

    # Split by dash or hyphen
    parts = duration_str.replace('–', '-').replace('—', '-').split('-')

    if len(parts) >= 2:
        start_date = parts[0].strip()
        end_date = parts[1].strip() if not currently_working else None
        return start_date, end_date, currently_working
    elif len(parts) == 1:
        return parts[0].strip(), None, False

    return None, None, False

def convert_experience_to_employment_history(old_experience):
    """Convert old experience structure to new employmentHistory"""
    employment_history = []

    if not old_experience:
        return employment_history

    for exp in old_experience:
        start_date, end_date, currently_working = parse_duration(exp.get('duration', ''))

        employment_history.append({
            'position': exp.get('role', ''),
            'company': exp.get('company', ''),
            'location': exp.get('location', None),
            'startDate': start_date,
            'endDate': end_date,
            'currentlyWorking': currently_working,
            'description': None,
            'responsibilities': exp.get('achievements', [])
        })

    return employment_history

def convert_languages(old_languages):
    """Convert old languages array to new structure"""
    if not old_languages:
        return []

    return [
        {
            'language': lang,
            'level': 'Intermediate'
        }
        for lang in old_languages
    ]

def convert_education(old_education):
    """Convert education to new structure with dates"""
    if not old_education:
        return []

    new_education = []
    for edu in old_education:
        year = edu.get('year', '')
        gpa = edu.get('gpa', None)

        description = None
        if gpa:
            description = f"<p>GPA: {gpa}</p>"

        new_education.append({
            'school': edu.get('institution', ''),
            'degree': edu.get('degree', ''),
            'location': None,
            'startDate': None,
            'endDate': year,
            'current': False,
            'description': description
        })

    return new_education

def migrate_cv_parsed(old_cv):
    """Migrate a single CV from old structure to new structure"""
    if not old_cv:
        return old_cv

    # Check if already migrated (has personalInfo instead of personal_info)
    if 'personalInfo' in old_cv:
        print("  Already migrated, skipping")
        return old_cv

    # Extract personal info
    old_personal_info = old_cv.get('personal_info', {})
    first_name, last_name = parse_name(old_personal_info.get('name', ''))

    # Build social links array
    social_links = []
    if old_personal_info.get('linkedin'):
        social_links.append({'type': 'linkedin', 'url': old_personal_info['linkedin']})
    if old_personal_info.get('github'):
        social_links.append({'type': 'github', 'url': old_personal_info['github']})
    if old_personal_info.get('portfolio'):
        social_links.append({'type': 'portfolio', 'url': old_personal_info['portfolio']})

    # Build new structure
    new_cv = {
        'personalInfo': {
            'jobTitle': None,
            'firstName': first_name,
            'lastName': last_name,
            'email': old_personal_info.get('email', None),
            'phone': old_personal_info.get('phone', None),
            'address': old_personal_info.get('location', None),
            'website': None,
            'birthDate': None,
            'nationality': None,
            'relationshipStatus': None,
            'availability': None,
            'socialLinks': social_links
        },
        'professionalSummary': old_cv.get('professional_summary', ''),
        'employmentHistory': convert_experience_to_employment_history(old_cv.get('experience', [])),
        'education': convert_education(old_cv.get('education', [])),
        'skills': convert_skills(old_cv.get('skills', {})),
        'languages': convert_languages(old_cv.get('languages', [])),
        'courses': [],
        'publications': [],
        'projects': old_cv.get('projects', []),
        'references': [],
        'hobbies': [],
        'internships': [],
        'customSections': {
            'awards': [],
            'volunteering': []
        }
    }

    return new_cv

def migrate_database():
    """Migrate all CV records in the database"""
    session = SessionLocal()

    try:
        # Get all analyses
        analyses = session.query(CVAnalysis).all()
        total = len(analyses)

        print(f"Found {total} CV analyses to migrate")

        migrated = 0
        skipped = 0
        errors = 0

        for i, analysis in enumerate(analyses, 1):
            try:
                print(f"\n[{i}/{total}] Migrating analysis ID: {analysis.id}")

                # Migrate cv_parsed
                if analysis.cv_parsed:
                    old_cv = analysis.cv_parsed
                    new_cv = migrate_cv_parsed(old_cv)

                    if new_cv == old_cv:
                        skipped += 1
                    else:
                        analysis.cv_parsed = new_cv
                        migrated += 1
                        print(f"  ✓ Migrated cv_parsed")

                # Migrate optimized_cv if exists
                if analysis.optimized_cv:
                    old_optimized = analysis.optimized_cv
                    new_optimized = migrate_cv_parsed(old_optimized)

                    if new_optimized != old_optimized:
                        analysis.optimized_cv = new_optimized
                        print(f"  ✓ Migrated optimized_cv")

                session.commit()

            except Exception as e:
                print(f"  ✗ Error migrating analysis {analysis.id}: {e}")
                session.rollback()
                errors += 1

        print(f"\n" + "="*60)
        print(f"Migration complete!")
        print(f"  Total records: {total}")
        print(f"  Migrated: {migrated}")
        print(f"  Already migrated (skipped): {skipped}")
        print(f"  Errors: {errors}")
        print("="*60)

    finally:
        session.close()

if __name__ == "__main__":
    print("="*60)
    print("CV Structure Migration Script")
    print("="*60)
    print("\nThis script will migrate all CV records from old structure to new structure.")
    print("Old structure will be converted to new structure.")
    print("\nWARNING: Make sure you have a backup of your database!")

    response = input("\nProceed with migration? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        migrate_database()
    else:
        print("Migration cancelled.")
