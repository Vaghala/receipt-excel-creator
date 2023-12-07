import requests,openpyxl,csv,json,sqlite3
from bs4 import BeautifulSoup
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

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

class Reciept:
    def __init__(self,hmerominia,katharo_sunolo,sunolo_fpa,eidos_parastatikou,sunolo,arithmos_parastatikou,eidos_proiontos,afm,eponumia,url):
        self.Date_time = hmerominia
        self.Sum_of_net_price = katharo_sunolo
        self.Sum_of_fpa = sunolo_fpa
        self.R_type = eidos_parastatikou
        self.Total = sunolo
        self.Number = arithmos_parastatikou
        self.Type_of_goods = eidos_proiontos
        self.Company_afm = afm
        self.Company_Name = eponumia
        self.AADE_Url = url
    '''
    self.Date_time
    self.Sum_of_net_price
    self.Sum_of_fpa
    self.R_type
    self.Total
    self.Number
    self.Type_of_goods
    self.Company_afm
    self.Company_Name
    '''

db = sqlite3.connect("Database.db")
cursor = db.cursor()
Urls =[]
with open("codes.csv",'r',encoding='utf-8') as fl:
    doc = csv.reader(fl)
    for row in doc:
        Urls.append(row[4])

Urls.pop(0)
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
    url = url.rstrip('\x00')
    Reciept_Object = Reciept(date_time,sum_net,sum_fpa,eidos_parastatikou,sun_axia,receipt_number,eidos_proiontos,_afm,company_name,url)
    Rs.append(Reciept_Object)
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

