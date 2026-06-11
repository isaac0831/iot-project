#!/home/weijun/iot_lab/env/bin/python3
import sqlite3

DB_FILE = "/home/weijun/iot_lab/sensor_data.db"

def get_summary_stats():
    """Compute summary statistics directly using SQL aggregation functions"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Let SQL do the heavy lifting instead of looping rows in Python (Page 53)
    query = """
    SELECT 
        COUNT(*) as count,
        AVG(temperature) as avg_temp,
        MIN(temperature) as min_temp,
        MAX(temperature) as max_temp,
        AVG(humidity) as avg_hum
    FROM readings
    """
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()
        
        return {
            'count': row[0],
            'avg_temp': round(row[1], 1) if row[1] else 0,
            'min_temp': row[2] if row[2] else 0,
            'max_temp': row[3] if row[3] else 0,
            'avg_humidity': round(row[4], 1) if row[4] else 0
        }
    except sqlite3.OperationalError as e:
        conn.close()
        print(f"Database error: {e}. Make sure the table exists and has data.")
        return None

if __name__ == "__main__":
    stats = get_summary_stats()
    if stats:
        print("\n=== Sensor Data Summary ===")
        print(f"Total readings tracked: {stats['count']}")
        print(f"Temperature Range : {stats['min_temp']}C - {stats['max_temp']}C")
        print(f"Average Temperature: {stats['avg_temp']}C")
        print(f"Average Humidity   : {stats['avg_humidity']}%")
        print("===========================\n")
