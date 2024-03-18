### TODO need to implement caching for the cli version and more advanced caching strategies ###

import sqlite3
from pieces.api.config import applications_db_path

def create_table():
    with sqlite3.connect(applications_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            name TEXT,
            version TEXT,
            platform TEXT,
            onboarded BOOLEAN,
            privacy TEXT
        )
        ''')

# Function to insert application data
def insert_application(app):
    """ Insert a new application into the applications table """
    try:
        with sqlite3.connect(applications_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO applications VALUES (:id, :name, :version, :platform, :onboarded, :privacy)",
                        {'id': app.id, 'name': app.name, 'version': app.version, 'platform': app.platform, 'onboarded': app.onboarded, 'privacy': app.privacy})
            conn.commit()
    except sqlite3.OperationalError: # There is no table created!
        create_table()
        insert_application(app)
    except sqlite3.IntegrityError: # The application already exists
        pass
