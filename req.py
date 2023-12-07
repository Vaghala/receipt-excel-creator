import requests,json

afm = "094173365"
url = "https://publicity.businessportal.gr/api/search"

headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
}

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
        print(rec["id"],rec["name"])
