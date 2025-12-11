import sqlite3
import json
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from bcrypt import checkpw
from flask_socketio import SocketIO, emit
import threading
import random

# --- 1. CONFIGURATION ---
app = Flask(__name__)
# IMPORTANT: For security, a secret key is required for sessions (like login).
app.secret_key = 'your_super_secret_key' # CHANGE THIS IN A REAL PROJECT!
DB_NAME = 'app.db'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- 2. DATABASE HELPER ---
def get_db_connection():
    """Returns a connection object to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

# --- 3. AUTHENTICATION LOGIC ---

# Middleware: Simple decorator to restrict access to authenticated users
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            # For API requests, return 401. For HTML pages, redirect to login.
            if request.path.startswith('/api'):
                return jsonify({'message': 'Unauthorized'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT id, password FROM Users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = user['id']
            # Redirect to the main dashboard view after successful login
            return redirect(url_for('zone_overview'))
        
        return render_template('login.html', error='Invalid credentials')
    
    # GET request: render the login form
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# --- 4. API ENDPOINTS ---

@app.route('/api/zones', methods=['GET'])
@login_required
def get_zones():
    """GET /api/zones: Get all zones with aggregated motor health."""
    conn = get_db_connection()
    
    # 1. Get all zones
    zones = conn.execute('SELECT id, zone_name, location FROM Zones').fetchall()
    
    # 2. Get Motor Counts and Statuses for aggregation
    motors = conn.execute('SELECT zone_id, status FROM Motors').fetchall()
    
    zone_data = []
    for zone in zones:
        zone_id = zone['id']
        zone_dict = dict(zone)
        
        # Simple aggregation logic
        zone_motors = [m for m in motors if m['zone_id'] == zone_id]
        
        zone_dict['total_motors'] = len(zone_motors)
        zone_dict['status_counts'] = {
            'Normal': random.randint(3, 5), # MOCK DATA
            'Warning': random.randint(0, 2), # MOCK DATA
            'Critical': 0
        }
        # Overall status based on max count
        zone_dict['overall_status'] = 'Normal'
        if zone_dict['status_counts']['Warning'] > 0:
            zone_dict['overall_status'] = 'Warning'
        if zone_dict['status_counts']['Critical'] > 0:
            zone_dict['overall_status'] = 'Critical'
            
        zone_data.append(zone_dict)
    
    conn.close()
    return jsonify(zone_data)


@app.route('/api/motors/<int:zone_id>', methods=['GET'])
@login_required
def get_motors_in_zone(zone_id):
    """GET /api/motors/<zone_id>: Get all motors in a zone with latest reading."""
    conn = get_db_connection()
    
    # Get all motors in the zone
    motors = conn.execute('SELECT * FROM Motors WHERE zone_id = ?', (zone_id,)).fetchall()
    
    motor_data = []
    for motor in motors:
        motor_dict = dict(motor)
        motor_id = motor['id']
        
        # Get the latest sensor reading for this motor
        latest_reading = conn.execute(
            'SELECT timestamp, temperature_celsius, vibration_mm_s, sound_db FROM Sensor_Readings WHERE motor_id = ? ORDER BY timestamp DESC LIMIT 1', 
            (motor_id,)
        ).fetchone()
        
        # MOCK latest reading if none exists
        if not latest_reading:
            latest_reading = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'temperature_celsius': 65.5 + random.uniform(-5, 5),
                'vibration_mm_s': 3.5 + random.uniform(-1, 1),
                'sound_db': 65.0 + random.uniform(-5, 5)
            }
        
        motor_dict['latest_reading'] = dict(latest_reading)
        
        # Determine Health Status based on a simple threshold (Temperature > 80 is Critical)
        temp = motor_dict['latest_reading']['temperature_celsius']
        if temp >= 80:
             motor_dict['health_status'] = 'Critical'
        elif temp >= 70:
            motor_dict['health_status'] = 'Warning'
        else:
            motor_dict['health_status'] = 'Normal'
        
        motor_data.append(motor_dict)
        
    conn.close()
    return jsonify(motor_data)


# NEW ROUTE ADDED HERE (Step 5.4)
@app.route('/api/motors/<int:motor_id>/detail', methods=['GET'])
@login_required
def get_motor_detail(motor_id):
    """GET /api/motors/<motor_id>/detail: Get single motor details with latest reading."""
    conn = get_db_connection()
    
    # Get the motor details
    motor = conn.execute('SELECT * FROM Motors WHERE id = ?', (motor_id,)).fetchone()
    
    if not motor:
        conn.close()
        return jsonify([]), 404
        
    motor_dict = dict(motor)
    
    # Get the latest sensor reading for this motor
    latest_reading = conn.execute(
        'SELECT timestamp, temperature_celsius, vibration_mm_s, sound_db FROM Sensor_Readings WHERE motor_id = ? ORDER BY timestamp DESC LIMIT 1', 
        (motor_id,)
    ).fetchone()

    # MOCK latest reading if none exists
    if not latest_reading:
        latest_reading = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'temperature_celsius': 68.0, 
            'vibration_mm_s': 3.0,
            'sound_db': 63.0
        }
    
    motor_dict['latest_reading'] = dict(latest_reading)
    
    conn.close()
    # The frontend expects a list for consistency in the JS, so we wrap it
    return jsonify([motor_dict]) 


@app.route('/api/sensors/<int:motor_id>/history', methods=['GET'])
@login_required
def get_sensor_history(motor_id):
    """GET /api/sensors/<motor_id>/history: Get 24 hours of historical data."""
    # Since we don't have historical data seeded, we will MOCK it for the chart
    
    timestamps = []
    temperatures = []
    start_time = datetime.now() - timedelta(hours=24)
    
    for i in range(25): # 25 points for 24 hours (one per hour)
        current_time = start_time + timedelta(hours=i)
        temp_val = 60 + (i * 0.5) + random.uniform(-3, 3)
        
        # Introduce an anomaly near the end
        if i >= 20:
             temp_val += 15 # Simulate a temperature spike
             
        timestamps.append(current_time.strftime('%H:%M'))
        temperatures.append(round(temp_val, 2))
        
    return jsonify({
        'timestamps': timestamps,
        'temperature': temperatures
    })

# --- 5. HTML ROUTING (Dashboard Views) ---

@app.route('/')
@app.route('/zones')
@login_required
def zone_overview():
    """Level 1: Zone Overview Dashboard."""
    return render_template('zone_overview.html')

@app.route('/zone/<int:zone_id>/motors')
@login_required
def motor_list(zone_id):
    """Level 1.5: List all motors in a zone."""
    # Pass the zone_id to the template for the frontend JS to use
    return render_template('motor_list.html', zone_id=zone_id)

@app.route('/device/<int:motor_id>')
@login_required
def device_detail(motor_id):
    """Level 2: Device Detail View."""
    # Pass the motor_id to the template for the frontend JS to use
    return render_template('device_detail.html', motor_id=motor_id)


# --- 6. REAL-TIME SIMULATION (WebSocket) ---

def sensor_data_generator():
    """Simulates sensor data and broadcasts it every 2 seconds."""
    while True:
        time.sleep(2) 
        
        conn = get_db_connection()
        # Randomly select a motor to update
        motor_row = conn.execute('SELECT id, zone_id FROM Motors ORDER BY RANDOM() LIMIT 1').fetchone()
        
        if motor_row:
            motor_id = motor_row['id']
            # Generate new mock reading
            new_temp = round(random.uniform(65.0, 75.0), 2)
            new_vibration = round(random.uniform(3.0, 5.0), 2)
            new_sound = round(random.uniform(60.0, 70.0), 2)
            
            # Occasionally inject an anomaly (e.g., 10% chance)
            if random.random() < 0.1:
                new_temp = round(random.uniform(85.0, 95.0), 2) # Critical temp
            
            # Broadcast the new reading
            reading = {
                'motor_id': motor_id,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'temperature_celsius': new_temp,
                'vibration_mm_s': new_vibration,
                'sound_db': new_sound,
            }
            
            # Broadcast to all connected clients
            socketio.emit('new_reading', reading)
            
        conn.close()

# Start the background thread for data simulation
threading.Thread(target=sensor_data_generator, daemon=True).start()


# --- 7. RUN APP ---
if __name__ == '__main__':
    # Use socketio.run instead of app.run because we are using WebSockets
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)