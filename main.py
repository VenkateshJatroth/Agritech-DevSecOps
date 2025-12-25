from datetime import datetime
from flask import Flask, jsonify, render_template, request
import sqlite3
from sensor import Sensor  # <--- 1. IMPORT YOUR NEW FILE

app = Flask(__name__)


# Database Setup (Same as before)
def init_db():
    conn = sqlite3.connect('farm_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature INTEGER,
            humidity INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


init_db()

# 🔴 2. TURN ON THE SENSOR (Create the Object)
# This creates a "Sensor" in memory that remembers its battery level.
my_field_sensor = Sensor("North Field")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/sensors')
def get_sensors():
    # 1. Get new data from the sensor
    data = my_field_sensor.read_data()

    # 2. CONNECT TO DATABASE (These are the lines you were missing!)
    conn = sqlite3.connect('farm_data.db')
    cursor = conn.cursor()

    # 3. Get current time (The new logic)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 4. Save to Database
    cursor.execute(
        'INSERT INTO readings (temperature, humidity, timestamp) VALUES (?, ?, ?)', 
        (data['temp'], data['hum'], current_time)
    )
    
    # 5. Save and Close
    conn.commit()
    conn.close()

    # 6. Send data to the frontend
    return jsonify({
        "temperature": data['temp'],
        "humidity": data['hum'],
        "battery": data['battery'],
        "location": data['location']
    })


# History Route (Your secure version)
@app.route('/history')
def history():
    conn = sqlite3.connect('farm_data.db')
    cursor = conn.cursor()
    search_query = request.args.get('q')

    if search_query:
        query = "SELECT * FROM readings WHERE temperature = ?"
        cursor.execute(query, (search_query,))
    else:
        cursor.execute('SELECT * FROM readings ORDER BY id DESC LIMIT 10')

    data = cursor.fetchall()
    conn.close()
    return render_template('history.html', readings=data)


# Route 4: EMERGENCY ALERT SYSTEM
@app.route('/api/alert', methods=['POST'])
def receive_alert():
    # 1. Listen for the signal
    print("\n🚨🚨🚨 EMERGENCY SIGNAL RECEIVED! 🚨🚨🚨")
    print(f"SOURCE: Mobile Device ({request.remote_addr})")

    # 2. Log it in the database as a "Critical Event" (999)
    conn = sqlite3.connect('farm_data.db')
    cursor = conn.cursor()
    # We use '999' as the code for FIRE
    cursor.execute('INSERT INTO readings (temperature, humidity) VALUES (?, ?)', (999, 999))
    conn.commit()
    conn.close()

    return jsonify({"status": "ALERT_CONFIRMED"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
