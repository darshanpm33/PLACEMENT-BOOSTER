from app import app, db
import sqlite3
import os

def migrate():
    # Path to the database
    db_path = os.path.join('instance', 'placement_booster.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Let Flask handle it.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Add results_json to test_record table
    try:
        cursor.execute("ALTER TABLE test_record ADD COLUMN results_json TEXT")
        print("Successfully added results_json column to test_record table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("results_json column already exists.")
        else:
            print(f"Error adding column: {e}")

    conn.commit()
    conn.close()

    # 2. Let SQLAlchemy create any entirely new tables (like CompletedCoding)
    with app.app_context():
        db.create_all()
        print("Database sync (create_all) completed.")

if __name__ == '__main__':
    migrate()
