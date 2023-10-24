import sqlite3 

db = sqlite3.connect("Database.db")
cursor = db.cursor()

q = f"Insert or ignore into Company values ({afm},{name},{ptype},{gemi});"

cursor.execute(q);