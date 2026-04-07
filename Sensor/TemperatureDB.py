from Sensor.temp_reading import *
import sqlite3
from datetime import datetime

class TemperatureDB:
    def __init__(self):
        # 1. Connect to SQLite DB (creates file if not exists)
        self.conn = sqlite3.connect("temperature.db")
        self.cursor = self.conn.cursor()

        # 2. Create table (only runs once)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            timestamp TEXT
        )
        """)
        self.conn.commit()


    def insert_temperature(self, temp):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO temperature_log (temperature, timestamp) VALUES (?, ?)",
            (temp, timestamp)
        )
        self.conn.commit()


    def close(self):
        self.conn.close()

if __name__ == "__main__":
    temp_db = TemperatureDB()
    for _ in range(5):
        temp = read_temperature()
        temp_db.insert_temperature(temp)
        print(f"Saved: {temp} at {datetime.now()}")
        time.sleep(1)

    temp_db.close()