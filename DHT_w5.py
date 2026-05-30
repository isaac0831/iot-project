#!/home/weijun/iot_lab/env/bin/python3
import board
import adafruit_dht
import sqlite3
from datetime import datetime
import time

# 1. Configuration
DB_FILE = "sensor_data.db"

def init_database():
    """Initialize database schema to store sensor readings"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # The schema: id (auto), timestamp, temperature, and humidity
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_reading(temperature, humidity):
    """Save the current sensor reading to the local database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # ISO format provides clear, sortable time-series data
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO readings (timestamp, temperature, humidity) VALUES (?, ?, ?)",
        (timestamp, temperature, humidity)
    )
    
    conn.commit()
    conn.close()
    print(f"Data saved to database: {temperature}C, {humidity}%")

# --- Main Execution ---
if __name__ == "__main__":
    init_database()
    
    # Initialise the dht device on GPIO 4
    dhtDevice = adafruit_dht.DHT11(board.D4)

    try:
        # Read values from sensor
        temp = dhtDevice.temperature
        hum = dhtDevice.humidity
        
        if temp is not None and hum is not None:
            print(f"Temp: {temp}C, Humidity: {hum}%")
            save_reading(temp, hum)
        else:
            print("Failed to read sensor")

    except Exception as e:
        # DHT sensors often fail on single reads; this catches those errors
        print(f"Sensor read failed: {e}")
    finally:
        dhtDevice.exit() # Clean up the hardware pins
