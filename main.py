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
    # 🔴 3. ASK THE SENSOR FOR DATA
    data = my_field_sensor.read_data()  # This drains 1% battery

    # Save to Database
    conn = sqlite3.connect('farm_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO readings (temperature, humidity) VALUES (?, ?)',
                   (data['temp'], data['hum']))
    conn.commit()
    conn.close()

    # Send to Frontend (Now including Battery!)
    return jsonify({
        "temperature": data['temp'],
        "humidity": data['hum'],
        "battery": data['battery'],  # <--- New Data!
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