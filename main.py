import time
import tkinter as tk
from tkinter import ttk,Label,messagebox
from tkinter.filedialog import askopenfilename
from threading import Thread
import requests,openpyxl,csv,json,sqlite3
from bs4 import BeautifulSoup
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import PatternFill

def search_company_name(afm):
    url = "https://publicity.businessportal.gr/api/search"
    headers={
        "Host":"publicity.businessportal.gr",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
        "Accept":"application/json, text/plain, */*",
        "Accept-Language":"en-US,en;q=0.5",
        "Accept-Encoding":"gzip, deflate, br",
        "Content-Type":"application/json",
        "Content-Length":"496",
        "Origin":"https://publicity.businessportal.gr",
        "Connection":"keep-alive",
        "Referer":"https://publicity.businessportal.gr/"
        }
    data={"dataToBeSent":{"inputField":afm,"city":None,"postcode":None,"legalType":[],"status":[],"suspension":[],"category":[],"specialCharacteristics":[],"employeeNumber":[],"armodiaGEMI":[],"kad":[],"recommendationDateFrom":None,"recommendationDateTo":None,"closingDateFrom":None,"closingDateTo":None,"alterationDateFrom":None,"alterationDateTo":None,"person":[],"personrecommendationDateFrom":None,"personrecommendationDateTo":None,"radioValue":"all","places":[]},"token":None,"language":"el"}
    response = requests.request('post',url, headers=headers,json=data)

    j = json.loads(response.text)
    lst = j['company']['hits']
    no_gemi = ""
    for rec in lst :
        suffix_gemi = rec["id"][-3:]
        if suffix_gemi in "000":
            return rec["name"]

def get_company_name(afm):
    base_url = "https://publicity.businessportal.gr/api/autocomplete/"
    url = base_url+afm

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Origin": "https://publicity.businessportal.gr",
    "Referer": "https://publicity.businessportal.gr/",
    "Cookie": "next-i18next=el"
    }
    data = {"token":"null","language":"el"}
    response = requests.post(url, headers=headers)
    j = json.loads(response.text)
    lst = j['payload']['autocomplete']
    no_gemi = ""
    for rec in lst :
        if not rec.get("branchType"):
            no_gemi = str(rec['arGemi'])

    url = "https://publicity.businessportal.gr/api/company/details"
    payload = {"query":{"arGEMI":no_gemi},"language":"el"}
    response = requests.post(url, headers=headers,json=payload)
    j2 = json.loads(response.text)
    if j2['message'] in 'Company not found':
        return None
    company_name = j2['companyInfo']['payload']["company"]["name"]
    return company_name

def associate (Receipts,People,Max_Cost):
    N_Receipts = Receipts.copy()

    for p in People:

        for r in N_Receipts:
            if (r.Total > Max_Cost) or (r.Total< 0) or (p.Total + r.Total > Max_Cost) :
                continue
            p.Total += r.Total
            p.Array_Of_receipts.append(r)
            N_Receipts.remove(r)

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
        return f"{self.ID}\t{self.Total}"

    def To_tuple(self):
        return (self.ID,self.Total)

    def fix_num(self):
        if type(self.Total) is type("1.1"):
            self.Total = float(self.Total.replace("€",""))

    def convert_to_record(self):
        return (2,self.Date_time,self.Sum_of_net_price,self.Sum_of_fpa," "," ",1," ",self.R_type,self.Number,self.Type_of_goods,"998727941","ΤΑΝΤΕΜ ΑΣΤΙΚΗ ΜΗ ΚΕΡΔΟΣΚΟΠΙΚΗ ΕΤΑΙΡΕΙΑ",1,self.Company_afm,self.Company_Name,"{:.2f}".format(self.Total),"=HYPERLINK(\""+self.AADE_Url+"\")")

class Person:
    def __init__(self,n,aor,tl):
        self.Name = n
        self.Array_Of_receipts = aor
        self.Total = tl
    
    def __repr__(self):
        return f"{self.Name} {self.Array_Of_receipts} {self.Total}"



def Openfile():
    filepath = askopenfilename(filetypes=[("csv Files", "*.csv"), ("All Files", "*.*")])
    if not filepath:
        return None
    with open(filepath,'r',encoding='utf-8') as fl:
        doc = csv.reader(fl)
        for row in doc:
            Urls.append(row[4])
    ltitle.config(text=f"Opened File :\n{filepath}")
    return Urls

def Execute(U):
    db = sqlite3.connect("Database.db")
    cursor = db.cursor()
    Urls.pop(0)
    DATA_ARRAY = []
    errors = []
    Rs = []
    MAX_COST = float(max_money.get())
    No_of_candidates = int(num_volunt.get())
    for url in Urls:
        progressbar['value'] += 100/len(Urls)
        Window.update_idletasks()
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
        url = url.rstrip('\x00')
        Reciept_Object = Reciept(date_time,sum_net,sum_fpa,eidos_parastatikou,sun_axia,receipt_number,eidos_proiontos,_afm,company_name,url)
        Rs.append(Reciept_Object)
        DATA_ARRAY.append(
            (2,date_time,sum_net,sum_fpa," "," ",1," ",eidos_parastatikou,receipt_number,eidos_proiontos,"998727941","ΤΑΝΤΕΜ ΑΣΤΙΚΗ ΜΗ ΚΕΡΔΟΣΚΟΠΙΚΗ ΕΤΑΙΡΕΙΑ",1,_afm,company_name,sun_axia,"=HYPERLINK(\""+url+"\")"))
    db.commit()


    Hashed_Receipts = {}

    for r in Rs:
        r.set_id(hash(r))
        r.fix_num()
        Hashed_Receipts[r.ID] = r

    items = [(r.ID,r.Total) for r in Rs]

    Rs.sort(key=lambda r:r.Total,reverse=True)

    Person_array = [Person(chr(i+65),[],0) for i in range(0,No_of_candidates)]
    Food_Receipts = [obj for obj in Rs if obj.Type_of_goods=="Τρόφιμα"]
    associate(Food_Receipts,Person_array,MAX_COST)
    Used_Reciepts = []
    for p in Person_array:
        for rec in p.Array_Of_receipts:
            Used_Reciepts.append(rec)

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    for row in DATA_ARRAY:
        worksheet.append(row)

    worksheet.append(("","",""))
    for rows in worksheet.iter_rows(min_row=worksheet.max_row, max_row=worksheet.max_row, min_col=None):
        for cell in rows:
            cell.fill = PatternFill(start_color="9aec9f", end_color="9aec9f", fill_type = "solid")
    worksheet.append(("","","Grouped Reciepts","Food"))

    for p in Person_array:
        worksheet.append(("","Volunteer :"+p.Name,"Total","{:.2f}".format(p.Total)))
        for rec in p.Array_Of_receipts:
            worksheet.append(Hashed_Receipts[rec.ID].convert_to_record())
        worksheet.append(("","",""))

    for rows in worksheet.iter_rows(min_row=worksheet.max_row, max_row=worksheet.max_row, min_col=None):
        for cell in rows:
            cell.fill = PatternFill(start_color="619df9", end_color="619df9", fill_type = "solid")
    worksheet.append(("","","Grouped Reciepts","Non-Food"))
    del Person_array

    Person_array = [Person(chr(i+65),[],0) for i in range(0,No_of_candidates)]
    Remaining_Reciepts = [obj for obj in Rs if obj not in Used_Reciepts]
    associate(Remaining_Reciepts,Person_array,MAX_COST)

    for p in Person_array:
        worksheet.append(("","Volunteer :"+p.Name,"Total","{:.2f}".format(p.Total)))
        for rec in p.Array_Of_receipts:
            worksheet.append(Hashed_Receipts[rec.ID].convert_to_record())
        worksheet.append(("","",""))

    for rows in worksheet.iter_rows(min_row=worksheet.max_row, max_row=worksheet.max_row, min_col=None):
        for cell in rows:
            cell.fill = PatternFill(start_color="FF0000", end_color="ff0000", fill_type = "solid")

    worksheet.append((" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","ERRORS"))

    for e in errors:
        e = ILLEGAL_CHARACTERS_RE.sub(r'',e)
        worksheet.append((" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","=HYPERLINK(\""+e+"\")"))
    workbook.save("OUTPUT.xlsx")
    print("Ended")


def Start():
    print("Started")
    if Urls == []:
        messagebox.showinfo("showinfo", "Please Choose File")
        return None

    t = Thread(target=Execute,args=(Urls,))
    t.start()
    if not t.is_alive() :
        messagebox.showinfo("showinfo", "Completed click ok to close") 
        Window.destroy()
    #Execute(Urls)


Urls = []

#region WINDOW
Window = tk.Tk()
Window.title("Create excel file from reciepts")


tk.Label(Window, text="Number Of Volunteers:").grid(row=2,column=0)
num_volunt = tk.Entry(Window, width=3)
num_volunt.grid(row=3,column=0)

tk.Label(Window, text="Max Money Value:").grid(row=2,column=4)
max_money = tk.Entry(Window, width=5)
max_money.grid(row=3,column=4)


ltitle = Label(Window, text="", font=('Aerial 12'),wraplength=200, justify="center")
ltitle.grid(row=1,column=2)
Choose_file = tk.Button(text="Choose File", command= Openfile)
Choose_file.place(x=100, y=250)

Startbtn = tk.Button(text="Start", bg="green",command= Start)
Startbtn.place(x=300, y=250)

progressbar = ttk.Progressbar(Window) 
progressbar.place(x=10, y=400, width=470)

Window.geometry("500x500")
Window.bind("<Control-w>",lambda e:Window.destroy())
Window.mainloop()
#endregion