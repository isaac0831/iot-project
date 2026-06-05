#!/home/weijun/iot_lab/env/bin/python3
import board
import adafruit_dht
import sqlite3
from datetime import datetime
import time
import socket
import BlynkLib

# 1. Configuration
DB_FILE = "sensor_data.db"
BLYNK_AUTH = "nw-qbti8X22KZHqp6GRDp7yK_gltZt3A"

# Initialize Blynk with modern cloud server parameters
blynk = BlynkLib.Blynk(BLYNK_AUTH, server="blynk.cloud", port=80)

# In Blynk Python library, state 2 means connected/authenticated
BLYNK_CONNECTED = 2

def init_database():
    """Initialize database schema to store sensor readings"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(
        "INSERT INTO readings (timestamp, temperature, humidity) VALUES (?, ?, ?)",
        (timestamp, temperature, humidity)
    )
    conn.commit()
    conn.close()

def is_wifi_connected():
    """Check if the Raspberry Pi has an active internet connection"""
    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except socket.error:
        return False

# --- Main Execution ---
if __name__ == "__main__":
    init_database()
    
    # Initialize DHT11 on GPIO 4
    dhtDevice = adafruit_dht.DHT11(board.D4)
    
    print("Blynk automated connection initializing... Press Ctrl+C to stop.")
    
    last_read_time = 0
    READ_INTERVAL = 5.0  # Take a reading every 5 seconds

    try:
        while True:
            wifi_active = is_wifi_connected()
            
            if wifi_active:
                try:
                    # FIXED: Use the integer state 2 to verify if connection is established
                    if blynk.state != BLYNK_CONNECTED:
                        print("Wi-Fi detected. Automatically connecting to Blynk Cloud...")
                        blynk.connect()
                    
                    # Keep network connection alive
                    blynk.run()
                except Exception:
                    pass 
            
            # Check if 5 seconds have passed
            current_time = time.time()
            if current_time - last_read_time >= READ_INTERVAL:
                last_read_time = current_time
                
                try:
                    # Read values from sensor
                    temp = dhtDevice.temperature
                    hum = dhtDevice.humidity
                    
                    if temp is not None and hum is not None:
                        temp_formatted = float(temp)
                        hum_formatted = float(hum)
                        
                        # PRINT LINE 1: Temperature: XX.XC, Humidity: XX.X%
                        print(f"Temperature: {temp_formatted:.1f}C, Humidity: {hum_formatted:.1f}%")
                        
                        # Always save locally
                        save_reading(temp_formatted, hum_formatted)
                        
                        # Send to Blynk if online and authenticated
                        if wifi_active and blynk.state == BLYNK_CONNECTED:
                            try:
                                blynk.virtual_write(0, temp_formatted)  # V1: Temperature
                                blynk.virtual_write(1, hum_formatted)   # V2: Humidity
                                print("Data sent to Blynk!")
                            except Exception:
                                print("Blynk transmission failed (Server unreachable).")
                        else:
                            print("Wi-Fi offline. Saved to local database only.")
                        
                    else:
                        print("Failed to read sensor: Data is None")

                except RuntimeError as error:
                    pass
                except Exception as e:
                    print(f"Sensor error: {e}")
            
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    finally:
        dhtDevice.exit()
