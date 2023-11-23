import pickle,random

class Reciept:
    def __init__(self,hmerominia,katharo_sunolo,sunolo_fpa,eidos_parastatikou,sunolo,arithmos_parastatikou,eidos_proiontos,afm,eponumia):
        self.Date_time = hmerominia
        self.Sum_of_net_price = katharo_sunolo
        self.Sum_of_fpa = sunolo_fpa
        self.R_type = eidos_parastatikou
        self.Total = float(sunolo.replace("€",""))
        self.Number = arithmos_parastatikou
        self.type_of_goods = eidos_proiontos
        self.Company_afm = afm
        self.Company_Name = eponumia
    def set_id(self,_id):
        self.ID = _id
    
    def __repr__(self):
        return f"{self.ID}\t{self.Total}"

    def To_tuple(self):
        return (self.ID,self.Total)

    def fix_num(self):
        self.Total = float(self.Total.replace("€",""))

class Person:
    def __init__(self,n,aor,tl):
        self.Name = n
        self.Array_Of_receipts = aor
        self.Total = tl
    
    def __repr__(self):
        return f"{self.Name} {self.Array_Of_receipts} {self.Total}"

def associate (Reciepts,People,Max_Cost):
    N_Reciepts = Reciepts
    for p in People:

        for r in N_Reciepts[:]:
            if r.Total > Max_Cost:
                continue
            if p.Total + r.Total > Max_Cost:
                continue
            p.Total += r.Total
            p.Array_Of_receipts.append(r)
            N_Reciepts.remove(r)
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
MAX_COST = 150
No_of_candidates = int(input("Enter Number of Candidates :  "))

Person_array = [Person(chr(i+65),[],0) for i in range(0,No_of_candidates)]
R.sort(key=lambda r:r.Total,reverse=True)

print(str(R))

associate(R,Person_array,150)

for p in Person_array:
    print(p.Name,p.Total)
    for rec in p.Array_Of_receipts:
        print(rec.ID,rec.Total)