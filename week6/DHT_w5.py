#!/home/weijun/iot_lab/env/bin/python3
import board
import adafruit_dht
import sqlite33
from datetime import datetime
import time
import socket
import BlynkLib

# --- CONFIGURATION ---
# Absolute path ensures systemd service executes perfectly on boot (Week 8) [cite: 96, 1008]
DB_FILE = "/home/weijun/iot_lab/sensor_data.db"
BLYNK_AUTH = "nw-qbti8X22KZHqp6GRDp7yK_gltZt3A"

# Initialize Blynk cloud parameters
blynk = BlynkLib.Blynk(BLYNK_AUTH, server="blynk.cloud", port=80)

# State 2 represents a completely authenticated Blynk session
BLYNK_CONNECTED = 2

def init_database():
    """Initializes table schema and handles migration for network failures"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Baseline Week 5 Local Data Persistence table [cite: 77, 556]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL
        )
    ''')
    
    # WEEK 9 UPGRADE: Dynamically inject the synced status column if missing [cite: 1089, 1111]
    # synced=0 means buffered/offline; synced=1 means uploaded [cite: 1113]
    try:
        cursor.execute("ALTER TABLE readings ADD COLUMN synced INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        # Catch and pass error gracefully if column already exists
        pass
    conn.close()

def save_reading(temperature, humidity):
    """Saves new records locally as UNSYNCED (0) to local buffer storage [cite: 97, 1115]"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # New readings always enter the system as 0 (not uploaded yet) [cite: 1115]
    cursor.execute(
        "INSERT INTO readings (timestamp, temperature, humidity, synced) VALUES (?, ?, ?, 0)",
        (timestamp, temperature, humidity)
    )
    conn.commit()
    # Grab unique row primary key ID to track sync status updates [cite: 1135, 1136]
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def mark_as_synced(reading_id):
    """Updates a unique row flag status to 1 upon cloud confirmation [cite: 1117, 1136]"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE readings SET synced=1 WHERE id=?", (reading_id,))
    conn.commit()
    conn.close()

def is_wifi_connected():
    """Verifies internet socket pipeline availability without stalling"""
    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except socket.error:
        return False

def resend_unsynced():
    """Queries SQLite buffer and pushes historical entries to cloud [cite: 97, 1119, 1155]"""
    # Guard clause: Stop immediately if local network interface or cloud server is down 
    if not is_wifi_connected() or blynk.state != BLYNK_CONNECTED:
        return
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Gather all unsent rows sequentially [cite: 1159]
    cursor.execute("SELECT id, temperature, humidity FROM readings WHERE synced=0")
    unsynced_rows = cursor.fetchall()
    
    # Process the backlog if any entries are found [cite: 1119, 1161]
    if unsynced_rows:
        print(f"[Recovery Buffer] Found {len(unsynced_rows)} unsent logs. Backfilling...")
        for row in unsynced_rows:
            r_id, temp, hum = row
            try:
                # Synchronize historical entry back onto Blynk cloud dashboard streams [cite: 1164]
                blynk.virtual_write(0, temp)
                blynk.virtual_write(1, hum)
                # Mark as uploaded in local database [cite: 1146, 1164]
                mark_as_synced(r_id)
                print(f"[Recovery Buffer] Successfully synced historical log ID: {r_id}")
                time.sleep(0.1)  # Brief 100ms pause protects against server-side flood kicks
            except Exception:
                print(f"[Recovery Buffer] Cloud dropped during sync. Backlog remaining in buffer.")
                break
    conn.close()

# --- MAIN EXECUTION PIPELINE ---
if __name__ == "__main__":
    init_database()
    
    # Initialize hardware layout configuration interface pins
    dhtDevice = adafruit_dht.DHT11(board.D4)
    print("Resilient IoT Failure-Recovery Node Active. Press Ctrl+C to stop.")
    
    last_read_time = 0
    READ_INTERVAL = 5.0  # Take a reading every 5 seconds

    try:
        while True:
            # Check physical connection topology status
            wifi_active = is_wifi_connected()
            
            if wifi_active:
                try:
                    # FIX AUTO SHUT DOWN: This runs every single 10ms loop iteration.
                    # It feeds the background cloud heartbeat loop constantly to prevent disconnects.
                    blynk.run()
                except Exception:
                    pass 
            
            # Non-blocking clock evaluation logic checks if interval has expired
            current_time = time.time()
            if current_time - last_read_time >= READ_INTERVAL:
                last_read_time = current_time
                
                try:
                    # Gather environment data properties from sensor
                    temp = dhtDevice.temperature
                    hum = dhtDevice.humidity
                    
                    if temp is not None and hum is not None:
                        temp_formatted = float(temp)
                        hum_formatted = float(hum)
                        
                        print(f"Temperature: {temp_formatted:.1f}C, Humidity: {hum_formatted:.1f}%")
                        
                        # Step 1: Always store locally first (Week 5 philosophy: Never lose data!) [cite: 99, 1103, 1115]
                        reading_id = save_reading(temp_formatted, hum_formatted)
                        
                        # Step 2: Try live synchronization 
                        if wifi_active and blynk.state == BLYNK_CONNECTED:
                            try:
                                blynk.virtual_write(0, temp_formatted)  # V0: Temperature
                                blynk.virtual_write(1, hum_formatted)   # V1: Humidity
                                mark_as_synced(reading_id)  # Immediately mark as uploaded 
                                print("Data sent to Blynk!")
                            except Exception:
                                print("Blynk transmission timeout. Kept in database buffer.")
                        else:
                            print("Wi-Fi offline. Saved to local database only.")
                            
                        # Step 3: Run backfill recovery loop to clean up any old un-uploaded data rows 
                        resend_unsynced()
                        
                    else:
                        print("Failed to read sensor: Data is None")

                except RuntimeError:
                    # Catch loosely timed standard DHT11 hardware interface polling glitches safely
                    pass
                except Exception as e:
                    print(f"Sensor exception handled: {e}")
            
            # 10ms pause prevents high CPU usage while maintaining cloud sync loops
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nProgram stopped safely via user request.")
    finally:
        dhtDevice.exit()  # Release GPIO hardware reference layers smoothly
