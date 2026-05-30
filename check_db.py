import sqlite3

# This uses the built-in library, no internet needed [cite: 572]
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

print("--- Week 5: Local Database Verification ---")
try:
    # Query your stored sensor readings [cite: 658]
    cursor.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 5")
    for row in cursor.fetchall():
        # Display: ID | Timestamp | Temperature | Humidity [cite: 578]
        print(f"ID: {row[0]} | Time: {row[1]} | Temp: {row[2]}C | Hum: {row[3]}%")
except Exception as e:
    print(f"Database error: {e}")
finally:
    conn.close()
