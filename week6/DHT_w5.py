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
    """Save the current sensor reading to the local database with a timestamp"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Capture the exact time for the database record
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save into the database file
    cursor.execute(
        "INSERT INTO readings (timestamp, temperature, humidity) VALUES (?, ?, ?)",
        (timestamp, temperature, humidity)
    )
    
    conn.commit()
    conn.close()
    
    # PRINT LINE 2: Confirmation with timestamp
    print(f"[{timestamp}] Data saved to database: {temperature}C, {humidity}%")

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
            # Capture short time for the first print line
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # PRINT LINE 1: The raw sensor data
            print(f"[{current_time}] Temp: {temp}C, Humidity: {hum}%")
            
            # Call the function to save to DB and print the second line
            save_reading(temp, hum)
        else:
            print("Failed to read sensor: Data is None")

    except Exception as e:
        # DHT sensors often fail on single reads; this catches those errors
        print(f"Sensor read failed: {e}")
    finally:
        dhtDevice.exit() # Clean up the hardware pins
