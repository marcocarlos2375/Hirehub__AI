"""
Database migration script to add missing columns to cv_analyses table.

This script adds three new columns that were introduced in Phases 7-9:
- cover_letter: JSON (Phase 7 - Cover Letter Generation)
- learning_path: JSON (Phase 8 - Learning Path Recommendations)
- interview_prep: JSON (Phase 9 - Interview Preparation)
"""

import sqlite3
import os

# Database path
db_path = '/app/data/hirehub.db'

# Check if running in Docker container or on host
if not os.path.exists(db_path):
    db_path = './backend/data/hirehub.db'

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit(1)

print(f"📊 Connecting to database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

columns_added = 0
columns_existed = 0

# Add cover_letter column
try:
    cursor.execute("ALTER TABLE cv_analyses ADD COLUMN cover_letter JSON")
    print("✅ Added 'cover_letter' column")
    columns_added += 1
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️  'cover_letter' column already exists")
        columns_existed += 1
    else:
        print(f"❌ Error adding 'cover_letter': {e}")

# Add learning_path column
try:
    cursor.execute("ALTER TABLE cv_analyses ADD COLUMN learning_path JSON")
    print("✅ Added 'learning_path' column")
    columns_added += 1
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️  'learning_path' column already exists")
        columns_existed += 1
    else:
        print(f"❌ Error adding 'learning_path': {e}")

# Add interview_prep column
try:
    cursor.execute("ALTER TABLE cv_analyses ADD COLUMN interview_prep JSON")
    print("✅ Added 'interview_prep' column")
    columns_added += 1
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️  'interview_prep' column already exists")
        columns_existed += 1
    else:
        print(f"❌ Error adding 'interview_prep': {e}")

# Commit changes
conn.commit()

# Verify the schema
cursor.execute("PRAGMA table_info(cv_analyses)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

print("\n" + "="*60)
print("📋 Current cv_analyses table schema:")
print("="*60)
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()

print("\n" + "="*60)
print("✅ Migration Complete!")
print(f"   Columns added: {columns_added}")
print(f"   Columns already existed: {columns_existed}")
print(f"   Total columns in table: {len(columns)}")
print("="*60)
