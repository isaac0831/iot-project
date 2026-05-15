import sqlite3

DB_FILE = "sensor_data.db"

def get_summary_stats():
    """Compute summary statistics (min, max, average) from time-series data"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # SQL does the heavy lifting - no need to loop in Python!
    query = """
    SELECT 
        COUNT(*) as total_readings,
        AVG(temperature) as avg_temp,
        MIN(temperature) as min_temp,
        MAX(temperature) as max_temp,
        AVG(humidity) as avg_humidity
    FROM readings;
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    
    return {
        'count': row[0],
        'avg_temp': round(row[1], 1) if row[1] else 0,
        'min_temp': row[2],
        'max_temp': row[3],
        'avg_humidity': round(row[4], 1) if row[4] else 0
    }

if __name__ == "__main__":
    stats = get_summary_stats()
    print("=== Sensor Data Summary ===")
    print(f"Total readings: {stats['count']}")
    print(f"Temperature: {stats['avg_temp']}C (Range: {stats['min_temp']} - {stats['max_temp']})")
    print(f"Humidity: {stats['avg_humidity']}%")
