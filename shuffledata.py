import pickle,random

class Reciept:
    def __init__(self,hmerominia,katharo_sunolo,sunolo_fpa,eidos_parastatikou,sunolo,arithmos_parastatikou,eidos_proiontos,afm,eponumia,url):
        self.Date_time = hmerominia
        self.Sum_of_net_price = katharo_sunolo
        self.Sum_of_fpa = sunolo_fpa
        self.R_type = eidos_parastatikou
        self.Total = float(sunolo.replace("€",""))
        self.Number = arithmos_parastatikou
        self.Type_of_goods = eidos_proiontos
        self.Company_afm = afm
        self.Company_Name = eponumia
        self.AADE_Url = url
    def set_id(self,_id):
        self.ID = _id
    
    def __repr__(self):
        return f"{self.Number}\t{self.ID}\t{self.Total}"

    def To_tuple(self):
        return (self.ID,self.Total)

    def fix_num(self):
        self.Total = float(self.Total.replace("€",""))

    def convert_to_record(self):
        return (2,self.Date_time,self.Sum_of_net_price,self.Sum_of_fpa," "," ",1," ",self.R_type,self.Number,self.Type_of_goods,"998727941","ΤΑΝΤΕΜ ΑΣΤΙΚΗ ΜΗ ΚΕΡΔΟΣΚΟΠΙΚΗ ΕΤΑΙΡΕΙΑ",1,self.Company_afm,self.Company_Name,self.Total,"=HYPERLINK(\""+self.AADE_Url+"\")")

class Person:
    def __init__(self,n,aor,tl):
        self.Name = n
        self.Array_Of_receipts = aor
        self.Total = tl
    
    def __repr__(self):
        return f"{self.Name} {self.Array_Of_receipts} {self.Total}"

def associate (Receipts,People,Max_Cost):
    N_Receipts = Receipts.copy()

    for p in People:

        for r in N_Receipts:
            if (r.Total > Max_Cost) or (r.Total< 0) or (p.Total + r.Total > Max_Cost) :
                continue
            p.Total += r.Total
            p.Array_Of_receipts.append(r)
            N_Receipts.remove(r)
    print("ended")

R = None
Hashed_Receipts = {}
with open("class_data.pckl","rb") as fll:
    R = pickle.load(fll)
    for r in R:
        r.set_id(hash(r))
        r.fix_num()
        Hashed_Receipts[r.ID] = r

items = [(r.ID,r.Total) for r in R]
MAX_COST = 155
No_of_candidates = int(input("Enter Number of Candidates :  "))

Person_array = [Person(chr(i+65),[],0) for i in range(0,No_of_candidates)]
R.sort(key=lambda r:r.Total,reverse=True)

Food_Receipts = [obj for obj in R if obj.Type_of_goods=="Τρόφιμα"]
associate(Food_Receipts,Person_array,MAX_COST)

for p in Person_array:
    print(p.Name,p.Total)
    print(f"Len: {len(p.Array_Of_receipts)}")
    for rec in p.Array_Of_receipts:
        print(rec.ID,rec.Total,f"\n{Hashed_Receipts[rec.ID]}")

Used_Reciepts = []
for p in Person_array:
    for rec in p.Array_Of_receipts:
        Used_Reciepts.append(rec)

Remaining = [obj for obj in R if obj not in Used_Reciepts]
print(f"All receipts len : {len(R)}\n Remaining reciepts {len(Remaining)}") 
#*[item for item in R if item not in other]