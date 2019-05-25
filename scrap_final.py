from lxml import html  
import csv,os,json
import requests
from builtins import ValueError
from time import sleep
from bs4 import BeautifulSoup as bsp
from urllib.request import urlopen as uReq
from selenium import webdriver
def AmzonParser1(url,i,extracted_data1):
    driver = webdriver.Chrome(executable_path=r'g:/chromedriver.exe')
    driver.get(url)
    html1=driver.page_source
    page1=bsp(html1,"html.parser")
    container=page1.findAll(class_="a-section celwidget")
    driver.quit()
    data={}
    for j in container:
        uid=j.find(class_="a-profile-name").text if j.find(class_="a-profile-name")!=None else None
        rev=j.find('span',class_="").text if j.find('span',class_="")!=None else None
        rating=j.find(class_="a-icon-alt").text.split()[0] if j.find(class_="a-icon-alt")!=None else None
        helpful=j.find('span',class_="a-size-base a-color-tertiary cr-vote-text").text.split()[0] if j.find('span',class_="a-size-base a-color-tertiary cr-vote-text")!=None else None
        data = {
            'PID':i,
            'USERID':uid,
            'REVIEW':rev,
            'RATING':rating,
            'HELPFUL':helpful,
                }
        extracted_data1.append(data)
    return data
 
def AmzonParser(url,i):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623 Safari/537.36'}
    page = requests.get(url,headers=headers)
    while True:
        sleep(3)
        try:
            doc = html.fromstring(page.content)
            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
            XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            XPATH_AVAILABILITY = '//div[@id="availability"]//text()'
            XPATH_RATING='//span[@class="a-icon-alt"]//text()'
            XPATH_REVIEW='//span[@id="acrCustomerReviewText"]//text()'
 
            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            RAw_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
            RAW_RATING=doc.xpath(XPATH_RATING)
            RAW_REVIEW=doc.xpath(XPATH_REVIEW)
 
            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            AVAILABILITY = ''.join(RAw_AVAILABILITY).strip() if RAw_AVAILABILITY else None
            RATING = ' '.join(''.join(RAW_RATING).split()) if RAW_RATING else None
            REVIEW = ' '.join(''.join(RAW_REVIEW).split()) if RAW_REVIEW else None
            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE
 
            if page.status_code!=200:
                raise ValueError('captha')
            data = {
                    'PID':i,
                    'NAME':NAME,
                    'SALE_PRICE':SALE_PRICE,
                    'CATEGORY':CATEGORY,
                    'ORIGINAL_PRICE':ORIGINAL_PRICE,
                    'AVAILABILITY':AVAILABILITY,
                    'OARATING':RATING,
                    'TREVIEW':REVIEW,
                    'URL':url,
                    }
 
            return data
        except Exception as e:
            print (e)
 
def ReadAsin():
    # AsinList = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
    driver = webdriver.Chrome(executable_path=r'g:/chromedriver.exe')
    my_url="https://www.amazon.com/s?k=pants&ref=nb_sb_noss_2"
    driver.get(my_url)
    html=driver.page_source
    page=bsp(html,"html.parser")
    AsinList = []
    containers=page.findAll(class_="sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32")
    for i in containers:
        if i["data-asin"]:
            AsinList.append(i["data-asin"])
    driver.quit()

    extracted_data = []
    extracted_data1=[]
    for i in AsinList:
        url = "http://www.amazon.com/dp/"+i
        print ("Processing: "+url)
        extracted_data.append(AmzonParser(url,i))
        sleep(1)
    f=open('data2.json','w')
    json.dump(extracted_data,f,indent=4)
    for i in AsinList:
        url = "http://www.amazon.com/dp/"+i
        print ("Processing: "+url)
        extracted_data1.append(AmzonParser1(url,i,extracted_data1))
        sleep(1)
    f=open('data.json','w')
    json.dump(extracted_data1,f,indent=4)
 
 
if __name__ == "__main__":
    ReadAsin()