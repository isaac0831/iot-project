import sqlite3
from datetime import datetime

DB_FILE = "sensor_data.db"

def get_daily_summary(target_date):
    """Compute summary statistics for a specific date (YYYY-MM-DD)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # We use date(timestamp) to ignore the HH:MM:SS part
    query = """
    SELECT 
        COUNT(*) as total_readings,
        AVG(temperature) as avg_temp,
        MIN(temperature) as min_temp,
        MAX(temperature) as max_temp,
        AVG(humidity) as avg_humidity
    FROM readings
    WHERE date(timestamp) = ?;
    """
    
    cursor.execute(query, (target_date,))
    row = cursor.fetchone()
    conn.close()
    
    # If there's no data for today, row[0] will be 0
    if not row or row[0] == 0:
        return None
    
    return {
        'count': row[0],
        'avg_temp': round(row[1], 1),
        'min_temp': row[2],
        'max_temp': row[3],
        'avg_humidity': round(row[4], 1)
    }

if __name__ == "__main__":
    # Automatically get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")
    
    stats = get_daily_summary(today)
    
    print(f"=== Analysis for Today: {today} ===")
    if stats:
        print(f"Total readings: {stats['count']}")
        print(f"Temperature: {stats['avg_temp']}C (Min: {stats['min_temp']}C, Max: {stats['max_temp']}C)")
        print(f"Avg Humidity: {stats['avg_humidity']}%")
    else:
        print(f"No data has been recorded yet for today ({today}).")
