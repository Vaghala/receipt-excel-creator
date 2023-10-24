import requests,openpyxl,csv,json
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
A=[]
with open("codes.csv",'r',encoding='utf-8') as fl:
    doc = csv.reader(fl)
    for row in doc:
        A.append(row[4])

A.pop(0)
urls = A
DATA_ARRAY = []
errors = []
for url in urls:
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
    Dick = {}
    for row in tr:
        x = row.findAll('td')
        x = x[0].text , x[1].text
        Dick[x[0]]= x[1]
    try:
        sum_net = str(round(float(Dick['Καθαρή αξία Α'].replace("€ ","")) + float(Dick['Καθαρή αξία Β'].replace("€ ","")) + float(Dick['Καθαρή αξία Γ'].replace("€ ","")) + float(Dick['Καθαρή αξία Δ'].replace("€ ","")) + float(Dick['Καθαρή αξία Ε'].replace("€ ","")),2))+"€"
        sum_fpa = str(round(float(Dick['ΦΠΑ Α'].replace("€ ","")) +float(Dick['ΦΠΑ Β'].replace("€ ","")) + float(Dick['ΦΠΑ Γ'].replace("€ ","")) + float(Dick['ΦΠΑ Δ'].replace("€ ","")),2))+"€"
        sun_axia = str(round(float(Dick[' Συνολική αξία '].rstrip(" ").replace("€ ","")),2))+"€"
        _afm = Dick["ΑΦΜ εκδότη"]
        company_name = search_company_name(_afm)
        if company_name is None:
            company_name = get_company_name(_afm)

        url = url.rstrip('\x00')
        DATA_ARRAY.append((2,Dick["Ημερομηνία, ώρα"].split(" ")[0],sum_net,sum_fpa," "," ",1," ",Dick["Είδος παραστατικού"],Dick["Αριθμός παραστατικού"]," ","998727941","ΤΑΝΤΕΜ ΑΣΤΙΚΗ ΜΗ ΚΕΡΔΟΣΚΟΠΙΚΗ ΕΤΑΙΡΕΙΑ",1,_afm,company_name,sun_axia,"=HYPERLINK(\""+url+"\")"))
    except:
        errors.append(url)
        continue

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

