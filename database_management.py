from DayData import DayData

import sqlite3
import datetime

class Database:
    def __init__(self) -> None:
        db_path = "database.db"

        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
                date TEXT PRIMARY KEY,
                value REAL
            )
            ''')
        
        self.connection.commit()

    def add_day_telegram_addition(self, unixTime, value):
        date = datetime.datetime.fromtimestamp(unixTime-60*60*4).strftime("%Y-%m-%d")
        self.add_day_addition(date, value)

    def add_day_addition(self, date, value):
        try:
            db_path = "database.db"
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            cursor.execute('''
                INSERT INTO data (date, value) VALUES (?, ?)
                ''', (date, value))
            connection.commit()
        except sqlite3.IntegrityError:
            cursor.execute('''UPDATE data SET value = value + ? WHERE date = ?''', (value, date))
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def add_day(self, date, value):
        try:
            db_path = "database.db"
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            cursor.execute('''
                INSERT INTO data (date, value) VALUES (?, ?)
                ''', (date, value))
            connection.commit()
        except sqlite3.IntegrityError:
            cursor.execute('''UPDATE data SET value = ? WHERE date = ?''', (value, date))
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    
    def get_day(self, date):
        db_path = "database.db"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
    
        cursor.execute('''
            SELECT * FROM data WHERE date = ?
            ''', (date,))
        data = cursor.fetchone()
    
        dayData = DayData()
    
        if data == None:
            dayData.set_exists(False)
            
        else:
            dayData.set_value(data[1])
            dayData.set_exists(True)
            if data[1] == 0:
                dayData.set_exists(False)
    
        cursor.close()
        connection.close()
    
        return dayData
    

    def get_last_weeks(self, numberOfWeeks):
        today = datetime.datetime.now()
        days = []
        numberOfDays = numberOfWeeks * 7
        weekday = today.weekday()
        days_to_subtract = (weekday) % 7 + numberOfDays
        start_date = today - datetime.timedelta(days=days_to_subtract)

        for i in range(days_to_subtract + 1):
            date = start_date + datetime.timedelta(days=i)
            date = date.strftime("%Y-%m-%d")
            dayData = self.get_day(date)
            days.append(dayData)
        
        return days