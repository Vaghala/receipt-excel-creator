import time
import tkinter as tk
from tkinter import ttk,Label,messagebox
from tkinter.filedialog import askopenfilename
from threading import Thread
import requests,openpyxl,csv,json,sqlite3
from bs4 import BeautifulSoup
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

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

def Openfile():
    filepath = askopenfilename(filetypes=[("csv Files", "*.csv"), ("All Files", "*.*")])
    if not filepath:
        return None
    with open(filepath,'r',encoding='utf-8') as fl:
        doc = csv.reader(fl)
        for row in doc:
            Urls.append(row[4])
    Urls.pop(0)
    label.config(text=f"Opened File :\n{filepath}")
    return Urls

def Execute(U):
    DATA_ARRAY = []
    errors = []
    Rs = []
    for url in Urls:
        try:
            r = requests.get(url)
        except:
            errors.append(url)
            continue
        soup = BeautifulSoup(r.text,'lxml')
        table = soup.find('table',"info")
        if table is None:
            errors.append(url)
            continue
        tr = table.findAll('tr')
        DictArray = {}
        for row in tr:
            x = row.findAll('td')
            x = x[0].text , x[1].text
            DictArray[x[0]]= x[1]
        try:
            date_time = DictArray["Ημερομηνία, ώρα"].split(" ")[0]
            eidos_parastatikou = DictArray["Είδος παραστατικού"]
            receipt_number = DictArray["Αριθμός παραστατικού"]
            sum_net = str(round(float(DictArray['Καθαρή αξία Α'].replace("€ ","")) + float(DictArray['Καθαρή αξία Β'].replace("€ ","")) + float(DictArray['Καθαρή αξία Γ'].replace("€ ","")) + float(DictArray['Καθαρή αξία Δ'].replace("€ ","")) + float(DictArray['Καθαρή αξία Ε'].replace("€ ","")),2))+"€"
            sum_fpa = str(round(float(DictArray['ΦΠΑ Α'].replace("€ ","")) +float(DictArray['ΦΠΑ Β'].replace("€ ","")) + float(DictArray['ΦΠΑ Γ'].replace("€ ","")) + float(DictArray['ΦΠΑ Δ'].replace("€ ","")),2))+"€"
            sun_axia = str(round(float(DictArray[' Συνολική αξία '].rstrip(" ").replace("€ ","")),2))+"€"
            _afm = DictArray["ΑΦΜ εκδότη"]
        except:
            errors.append(url)
            continue
        cursor.execute(f"select Company_Name from Companies where AFM ='{_afm}';")
        company_name = cursor.fetchone()
        if company_name is not None:
            company_name = company_name[0]
            
        if company_name is None:
            company_name = search_company_name(_afm)
            if company_name is not None:
                cursor.execute(f"insert Into Companies(AFM,Company_name) values(?,?);",(_afm,company_name))

        if company_name is None:
            company_name = get_company_name(_afm)
            if company_name is not None:
                cursor.execute(f"insert Into Companies(AFM,Company_name) values(?,?);",(_afm,company_name))

        cursor.execute(f"select Product_Type from Companies where AFM ='{_afm}';")
        eidos_proiontos = cursor.fetchone()
        if eidos_proiontos is not None:
            eidos_proiontos = eidos_proiontos[0]

        Reciept_Object = Reciept(date_time,sum_net,sum_fpa,eidos_parastatikou,sun_axia,receipt_number,eidos_proiontos,_afm,company_name)
        Rs.append(Reciept_Object)
        url = url.rstrip('\x00')
        DATA_ARRAY.append(
            (2,date_time,sum_net,sum_fpa," "," ",1," ",eidos_parastatikou,receipt_number,eidos_proiontos,"998727941","ΤΑΝΤΕΜ ΑΣΤΙΚΗ ΜΗ ΚΕΡΔΟΣΚΟΠΙΚΗ ΕΤΑΙΡΕΙΑ",1,_afm,company_name,sun_axia,"=HYPERLINK(\""+url+"\")"))




    import pickle
    with open("class_data.pckl",'wb') as fll:
        pickle.dump(Rs,fll)

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    for row in DATA_ARRAY:
        worksheet.append(row)
    worksheet.append(("","",""))
    worksheet.append(("","","ERRORS"))

    for e in errors:
        e = ILLEGAL_CHARACTERS_RE.sub(r'',e)
        worksheet.append((" "," ","=HYPERLINK(\""+e+"\")"))

    workbook.save("OUTPUT.xlsx")






def Start():
    print(Urls)
    if Urls == []:
        messagebox.showinfo("showinfo", "Please Choose File")
        return None
    Execute(Urls)
    for u in Urls:
        time.sleep(0.1)
        progressbar['value'] += 100/len(Urls)
        Window.update_idletasks()
    messagebox.showinfo("showinfo", "About to Exit") 
    Window.destroy()

Urls = []
db = sqlite3.connect("Database.db")
cursor = db.cursor()

#region WINDOW
Window = tk.Tk()
Window.title("Create excell file from reciepts")


tk.Label(Window, text="Number Of Volunteers:").pack()
num_volunt = tk.Entry(Window)
num_volunt.place(x=50,y=100)

tk.Label(Window, text="Max Money Value:").pack()
max_money = tk.Entry(Window)
max_money.place(x=250,y=100)


label=Label(Window, text="", font=('Aerial 18'),wraplength=300, justify="center")
label.pack()

Choose_file = ttk.Button(text="Choose File", command= Openfile)
Choose_file.place(x=100, y=250)

Startbtn = ttk.Button(text="Start", command= Start)
Startbtn.place(x=300, y=250)

progressbar = ttk.Progressbar(Window) 
progressbar.place(x=10, y=400, width=470)

Window.geometry("500x500")
Window.bind("<Control-w>",lambda e:Window.destroy())
Window.mainloop()
#endregion