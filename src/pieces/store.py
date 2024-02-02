### TODO need to implement caching for the cli version and more advanced caching strategies ###

import sqlite3
import pieces_os_client as pos_client


# Function to create a database connection
def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    try:
        return sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return None

def create_table(conn):
    """ Create a table if it does not exist yet """
    try:
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
    except Exception as e:
        print(e)

# Function to insert application data
def insert_application(conn, app):
    """ Insert a new application into the applications table """
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO applications VALUES (:id, :name, :version, :platform, :onboarded, :privacy)",
                       {'id': app.id, 'name': app.name, 'version': app.version, 'platform': app.platform, 'onboarded': app.onboarded, 'privacy': app.privacy})
        conn.commit()
    except Exception as e:
        print(e)

# Function to get an application by id
def get_application(conn, app_id):
    """ Fetch an application by id """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications WHERE id=:id", {'id': app_id})
        result = cursor.fetchone()
        if result:
            configuration = pos_client.Configuration(host="http://localhost:1000")

            with pos_client.ApiClient(configuration) as api_client:
                application = pos_client.Application()

                return application(
                    id=result[0],
                    name=result[1],
                    version=result[2],
                    platform=result[3],
                    onboarded=bool(result[4]),
                    privacy=result[5],
                )
        return None
    except Exception as e:
        print(e)
        return None