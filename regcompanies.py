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


'''
ΚΑΔ για τρόφημα:

46.38   Χονδρικό εμπόριο άλλων τροφίμων, συμπεριλαμβανομένων ψαριών, καρκινοειδών και μαλακίω
46.39   Μη εξειδικευμένο χονδρικό εμπόριο τροφίμων, ποτών και καπνο
47.29   Λιανικό εμπόριο άλλων τροφίμων σε εξειδικευμένα καταστήματ
47.81   Λιανικό εμπόριο τροφίμων, ποτών και καπνού, σε υπαίθριους πάγκους και αγορέ
84.13.15 Διοικητικές υπηρεσίες που σχετίζονται με το διανεμητικό εμπόριο και την τροφοδοσία με τρόφιμα, με τα ξενοδοχεία και τα εστιατόρ
46.17   Εμπορικοί αντιπρόσωποι που μεσολαβούν στην πώληση τροφίμων, ποτών και καπνού, εκτός α
10.71 Αρτοποιία παραγωγή νωπών ειδών ζαχαροπλαστικής
47.24 Λιανικό εμπόριο ψωμιού, αρτοσκευασμάτων και λοιπών ειδών αρτοποιίας και ζαχαροπλ


'''