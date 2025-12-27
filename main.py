from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime
import os
import random # Kept only for fallback if database is empty

app = Flask(__name__)

# =========================================================
# DATABASE SETUP
# =========================================================
def init_db():
    try:
        conn = sqlite3.connect('farm_data.db')
        c = conn.cursor()
        # Create table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS readings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      temperature REAL,
                      humidity REAL,
                      soil_moisture INTEGER,
                      motor_status TEXT,
                      timestamp TEXT)''')
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database Error: {e}")

# Initialize DB on startup
init_db()

# =========================================================
# ROUTES
# =========================================================

# 1. Home Page (Frontend)
@app.route('/')
def index():
    return render_template('index.html')

# 2. RECEIVER API (ESP32 Sends Data Here)
@app.route('/api/update_sensor', methods=['POST'])
def update_sensor():
    try:
        # Get JSON data from ESP32
        data = request.get_json()
        
        # Extract values (with defaults if missing)
        temp = data.get('temperature', 0.0)
        hum = data.get('humidity', 0.0)
        soil = data.get('soil_moisture', 0)
        motor = data.get('motor_status', 'OFF')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Save to SQLite Database
        conn = sqlite3.connect('farm_data.db')
        c = conn.cursor()
        c.execute("INSERT INTO readings (temperature, humidity, soil_moisture, motor_status, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (temp, hum, soil, motor, timestamp))
        conn.commit()
        conn.close()
        
        print(f"✅ Data Saved: Temp={temp}, Hum={hum}")
        return jsonify({"status": "success", "message": "Data saved"}), 200

    except Exception as e:
        print(f"❌ Error Saving Data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. DASHBOARD API (Frontend Reads Data Here)
@app.route('/api/sensors')
def get_sensors():
    try:
        conn = sqlite3.connect('farm_data.db')
        c = conn.cursor()
        # Get the LATEST reading
        c.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        conn.close()

        if row:
            # Row format: (id, temp, hum, soil, motor, time)
            return jsonify({
                "temperature": row[1],
                "humidity": row[2],
                "soil_moisture": row[3],
                "motor_status": row[4],
                "timestamp": row[5]
            })
        else:
            # FALLBACK: If DB is empty (new app), return Waiting status
            return jsonify({
                "temperature": 0,
                "humidity": 0,
                "soil_moisture": 0,
                "motor_status": "WAITING...",
                "timestamp": "No Data Yet"
            })

    except Exception as e:
        return jsonify({"error": str(e)})

# =========================================================
# RUN SERVER
# =========================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
