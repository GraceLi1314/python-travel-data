import re

import numpy
from bs4 import BeautifulSoup
import urllib.request, urllib.error
import ssl
import sqlite3
from geopy.geocoders import Nominatim
import xlwt
import requests
ssl._create_default_https_context = ssl._create_unverified_context
from wordcloud import WordCloud
import jieba
import matplotlib.pyplot as plt

country = input("which country do you want to visit?")
dbpath = 'travelTest.db'
def main():
    baseurl = "http://www.mafengwo.cn/search/q.php?q="+country
    getData(baseurl)
    #init_db()
    #add_data()
    addData_toDB()
    showWord()

def askUrl(url):
    head={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15"
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("UTF-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html

visitList = []
def getData(baseurl):
    html = askUrl(baseurl)
    #file = open("travel.html", 'r', encoding='utf-8')
    bs = BeautifulSoup(html, "html.parser")
    item = bs.select(".hot-att > ul.clearfix > li > a")
    for link in item:
        data = []
        visitUrl = link["href"]
        url = askUrl(visitUrl)
        #rfile = open("fisherman.html", 'r', encoding="utf-8")
        bs = BeautifulSoup(url, "html.parser")
        findcName = bs.find("h1").get_text()
        data.append(country)
        data.append(visitUrl)
        data.append(findcName)
        findSummary = bs.find("div", {"class": "summary"})
        if (findSummary == None):
            findSummary = bs.find_all("dd")[0]
        findSummary = findSummary.get_text().replace("\n", "")
        eName = re.findall(r'\（.*?\）', str(findSummary))
        if (len(eName) == 0):
            eName = re.findall(r'\(.*?\)', str(findSummary))
        if (len(eName) > 0):
            eName = eName[0]
            findeName = re.sub("[（ ）]", " ", str(eName))
            data.append(findeName)
        else:
            findeName = bs.find("div", {"class": "en"}).get_text()
            data.append(findeName)
        findTicket = bs.find_all("dd")[1].get_text().replace("\n", "")
        if (findTicket == '上亿旅行者共同打造的"旅行神器"'):
            findTicket = ' \ '
        findLocation = bs.find("p", {"class": "sub"})
        if findLocation != None:
            findLocation = findLocation.get_text().replace("\n", "")
        string = bs.find_all("a", {"title": "蜂蜂点评"})
        reviews = re.compile(r'<a title="蜂蜂点评">蜂蜂点评<span>（(\d*)条）</span></a>')
        findReviews = re.findall(reviews, str(string))[0]
        data.append(findReviews)
        data.append(findTicket)
        print("findLocation="+findLocation)
        if findLocation != None:
            data.append(findLocation)
        script = bs.find_all('script', {'type': 'text/javascript'})[7]
        keys = re.compile(r'\'data-content\', \'(.*)\'', re.S)
        findKeys = re.findall(keys, str(script))[0]
        data.append(findKeys)
        data.append(findSummary.replace("                    ", ""))

        #if the location's format is not valid, insert a ',' before the first digit
        geolocator = Nominatim(user_agent="main.py")
        location = geolocator.geocode(f"{findeName}, {country}")
        if location == None:
            location = ""
            first= False
            for item in str(findLocation):
                if (item.isdigit()):
                    if (not first):
                        location += " "
                        first = True
                location+=item
            print(location)
            location = geolocator.geocode(location)
        print(location)
        data.append(str(location.longitude))
        data.append(str(location.latitude))
        visitList.append(data)
        print(data)
    return visitList

def init_db():
    sql = '''
        create table travel(id integer primary key autoincrement, country varchar,
        info_link text, cname varchar, ename varchar, score numeric, ticket text, location text,
        keywords text, info text, longitude float, latitude float)
    '''
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

def add_data():
    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet('travelguide', cell_overwrite_ok=True)

    col = ('country',"info_link","chineseName","englishName","reviews","ticket","location","keywords", "info")
    for i in range(0, 9):
        sheet.write(0, i, col[i])
    for i in range(0, len(visitList)):
        print("第%d条" % (i+1))
        data = visitList[i]
        for j in range(0, 9):
            sheet.write(i+1, j, data[j])
    book.save('travel.xls')

def addData_toDB():
    #init_db()
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    for visit in visitList:
        for index in range(len(visit)):
            if index == 4 or index == 9 or index == 10:
                continue
            visit[index] = '"'+str(visit[index])+'"'
        print(visit)
        sql='''
            insert into travel
            (country, info_link, cname, ename, score, ticket, location, keywords, info, latitude, longitude) values (%s) 
        ''' % ",".join(visit)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()

def showWord():
    con = sqlite3.connect(dbpath)
    cur = con.cursor()
    sql = "select keywords from travel where country='"+country+"'"
    data = cur.execute(sql)
    text = ""
    for item in data:
        text = text + item[0]
    cur.close()
    con.close()
    cut = text.replace("，", " ")
    #cut = jieba.cut(cut)
   #string = ' '.join(cut)

    x, y = numpy.ogrid[:700, :700]
    mask = (x - 300) ** 2 + (y - 300) ** 2 > 220 ** 2
    mask = 275 * mask.astype(int)

    wc = WordCloud(background_color="white", repeat=True, mask=mask, font_path="/System/Library/AssetsV2/com_apple_MobileAsset_Font6/fedef1896002be99406da1bf1a1a6104a1737b39.asset/AssetData/Xingkai.ttc")
    wc.generate(cut)
    fig = plt.figure(1)
    plt.axis("off")
    plt.imshow(wc, interpolation="bilinear")
    #plt.show()
    plt.savefig(r'./static/images/'+country+'.jpg', dpi=700)
    plt.show()
if __name__ == "__main__":
    main()
