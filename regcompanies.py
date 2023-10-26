import sqlite3,csv

db = sqlite3.connect("Database.db")
cursor = db.cursor()

Data_array = []
with open('file2.csv','r',encoding='utf-8') as fll:
    arr = csv.reader(fll)
    for d in arr:
        try:
            rec = d[0].split("\t")
            Data_array.append((rec[1],rec[2],rec[3]))
        except:
            continue

for d in Data_array:
    if len(d[1])<9:
        print(f"\n\nWrong AFM :{d[1]}")
#    else:
#        print(d)

#q = f"Insert or ignore into Company values ({afm},{name},{ptype},{gemi});"

cursor.executemany("Insert or ignore into Companies(Product_type,AFM,Company_name) values (?,?,?)",Data_array)
db.commit()
db.close()