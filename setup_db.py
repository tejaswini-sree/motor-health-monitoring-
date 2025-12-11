import sqlite3
from bcrypt import hashpw, gensalt

# 1. Define the Database File and Connection
DB_NAME = 'app.db'
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# 2. Define the Hashing Function for Passwords
# Note: bcrypt automatically uses a random salt, making it secure.
def get_hashed_password(password):
    return hashpw(password.encode('utf-8'), gensalt())

# --- 3. CREATE TABLES ---

# A. Users Table
print("Creating Users table...")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) DEFAULT 'user@example.com',
        role VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# B. Zones Table
print("Creating Zones table...")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Zones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zone_name VARCHAR(100) NOT NULL,
        location VARCHAR(255) NOT NULL,
        status VARCHAR(20) DEFAULT 'active'
    )
''')

# C. Motors Table
print("Creating Motors table...")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Motors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        motor_name VARCHAR(100) NOT NULL,
        zone_id INTEGER,
        motor_type VARCHAR(50) NOT NULL,
        rated_power_kw DECIMAL(5,2) NOT NULL,
        installation_date DATE,
        status VARCHAR(20) DEFAULT 'running',
        FOREIGN KEY (zone_id) REFERENCES Zones(id)
    )
''')

# D. Sensor_Readings Table (Focusing on Temperature for our first chart)
print("Creating Sensor_Readings table...")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sensor_Readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        motor_id INTEGER,
        timestamp TIMESTAMP NOT NULL,
        temperature_celsius DECIMAL(5,2) NOT NULL,
        vibration_mm_s DECIMAL(5,2),
        sound_db DECIMAL(5,2),
        FOREIGN KEY (motor_id) REFERENCES Motors(id)
    )
''')

# --- 4. SEED DATA ---

# A. Seed Users (with Hashed Passwords)
print("Seeding Users...")
users_to_seed = [
    ('admin', get_hashed_password('admin123'), 'Administrator'),
    ('operator', get_hashed_password('operator123'), 'Operator')
]
cursor.executemany("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", users_to_seed)

# B. Seed a Test Zone
print("Seeding Zones...")
cursor.execute("INSERT INTO Zones (zone_name, location) VALUES (?, ?)", ('Assembly Line 1', 'Building A, Floor 1'))
zone_id = cursor.lastrowid # Get the ID of the new zone

# C. Seed Test Motors for the Zone
print("Seeding Motors...")
motors_to_seed = [
    (zone_id, 'Motor A-1', 'AC Induction', 5.5),
    (zone_id, 'Motor A-2', 'DC Brushless', 7.5),
    (zone_id, 'Motor A-3', 'AC Induction', 10.0),
    (zone_id, 'Motor A-4', 'DC Brushless', 3.0),
    (zone_id, 'Motor A-5', 'AC Induction', 15.0),
]
for zone_id, name, type, power in motors_to_seed:
    cursor.execute("INSERT INTO Motors (zone_id, motor_name, motor_type, rated_power_kw) VALUES (?, ?, ?, ?)", (zone_id, name, type, power))

# 5. Commit Changes and Close
conn.commit()
conn.close()
print("Database 'app.db' created, tables defined, and users seeded successfully!")