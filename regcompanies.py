import sqlite3,csv

import_file = input(f"Enter Import file location : ")

dblock = input(f"Enter Database location : ")

db = sqlite3.connect(dblock)
cursor = db.cursor()



Data_array = []
with open(import_file,'r',encoding='utf-8') as fll:
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


cursor.executemany("Insert or ignore into Companies(Product_type,AFM,Company_name) values (?,?,?)",Data_array)
db.commit()
db.close()


