import re
import datetime
import json
import random

import threading
import requests
import pymysql
from faker import Factory
from bs4 import BeautifulSoup

# IP池
proxies = []


def get_proxies():
    global proxies
    mysql = {
        'user': 'root',
        'password': '123456',
        'host': '127.0.0.1',
        'port': 3306,
        'db': 'spider',
        'charset': 'utf8'
    }
    conn = pymysql.connect(**mysql)
    cursor = conn.cursor()
    execute = cursor.execute
    sql = 'select ip, port, types from proxies limit 500'
    execute(sql)
    proxies = cursor.fetchall()
    cursor.close()
    conn.close()


# 随机选择IP
def get_proxy():
    proxy = random.choice(proxies)
    ip = proxy[0]
    port = proxy[1]
    types = proxy[2]
    proxy = '{}://{}:{}'.format(ip, port, types)
    proxy = {types: proxy}
    return (ip, port, types, proxy)


def get_data_from(url, date):
    global dct_all, form_data
    num = 0
    dct_each_day = {}
    headers = {
        'User-Agent': Factory().create().user_agent(),
        'Referer': 'https://booking.airasia.com/',
        'Cookie': 'LanguageSelect=cn/zh; true_loc=cn; X-CDN-Geo-Country=CN; X-CDN-Geo-City=SHANGHAI; _gcl_au=1.1.3512672.1539829882; currencySelect=CNY; __airasiaga=GA1.2.1508029182.1539829884; __airasiaga_gid=GA1.2.873579685.1539829884; acw_tc=65e300cc15398301995174164ea2cae773b3c677a90de1ad8bfefbbeb3; ASP.NET_SessionId=3baxaazmk1u1xkgsz1bqjc03; appID=W001; __RequestVerificationToken=ujANo7banTdpdPmhbLua4CPC-u-WtSxcV3uYerYz7IQhxaknfTi1koEqMcMsdXT85TPZBjtszVbTI47Tl7UZzSUhN_F56xjF8L5kGELkeGMJlK3gtdMa0gfjImvabp7Uh5HRmw2; dotrez=1343415306.20480.0000; rxVisitor=1539830193977I0TJLG6B2E67DKU5QTNL4UBQQG18CRT5; displaySSR=%7B%22meal%22:%22%22,%22departureDate%22:%222019-1-18%22,%22bookingDate%22:%222018-10-18%22%7D; flightSelect=PEK|DPS|2019-01-18|N|1|0|0|O|N; displayFare=%7B%22displayFare%22%3A1463.59%2C%22resultsLink%22%3A%22https%3A//booking.airasia.com/Flight/Select%3Fo1%3DPEK%26d1%3DDPS%26culture%3Dzh-CN%26dd1%3D2019-01-18%26ADT%3D1%26s%3Dtrue%26mon%3Dtrue%26cc%3DCNY%26c%3Dfalse%22%2C%22currency%22%3A%22CNY%22%2C%22destinationCity%22%3A%22%25E5%25B7%25B4%25E5%258E%2598%25E5%25B2%259B%2520%28DPS%29%22%2C%22departureCity%22%3A%22%25E5%258C%2597%25E4%25BA%25AC%2520%28PEK%29%22%7D; nearest_airports={"city":"KYOTO","airports":"KIX|NGO|HND"}; jaceToken=; dotRezSignature=WVlaRUhnUkNEb1k9bXphYXhhYjN8MzBjanFiMXpkRjBmVkkvOFdtelU2T3gxeXpuSEtZU2hzb1M1Qlg0bzVDcGNzZ2t4MXUxa2I2S3l3a2VuODkycStDRDk5MDAyQkNGTXREZ0c5Tm9ZMnNmcEVkMDlNcWpKTnY0NTFjTWdOcWM3K3Q5UzNoK1FGWnp1dExJU2hDc2MrOTYySnpNNHcvbEhQOEJuS2lQTC9DLzBvUVpvSStGNVRHND0=; userSession=cc=en-GB&mcc=MYR&rc=WWWA&ad=3baxaazmk1u1xkgsz1bqjc03&p=&st=1539831432.60542; dtPC=5$231425785_933h-vDLFUKHINQOOHOJLJQLOILVOLKLHGNJLK; rxvt=1539833295154|1539830193980; dtLatC=2; lastOrigin=PEK; lastDestination=SYD; lastDepartureDate=17/01/2019; lastReturnDate=19/01/2019; dtCookie=5$2F6E248DAE7078FBA3E8BDE2E263F03A|booking.airasia.com|1; dtSa=true%7CC%7C-1%7CSearch%7C-%7C1539831498211%7C231425785_933%7Chttps%3A%2F%2Fbooking.airasia.com%2F%7CAirAsia%20%5Ep%20Booking%20%5Ep%20Book%20low%20fares%20online%20-%20Search%7C1539831495156%7C'
    }
    response = requests.get(url, headers=headers, verify=False, proxies=get_proxy()[-1], data=form_data)
    response.encoding = 'utf-8'
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select('table.avail-table-info')

    for item in items:
        lst = []
        for i in range(2):
            try:
                # 起飞地
                depAirport = item.select('tr.fare-dark-row')[i].select('div.text-center > div')[1].text
                # 起飞时间
                depTime = item.select('tr.fare-dark-row')[i].select('div.avail-table-bold')[0].text
                # 落地城市
                arrAirport = item.select('tr.fare-dark-row')[i].select('div.text-center > div')[3].text
                # 落地时间
                arrTime = item.select('tr.fare-dark-row')[i].select('div.avail-table-bold')[1].text
                # 航班型号
                flight_info = item.select('div.carrier-hover-bold')[i].text.split()
                carrier = flight_info[0]
                # 航班编号
                flightNumber = flight_info[1]
            except:
                depAirport = item.select('tr.fare-light-row')[i].select('div.text-center > div')[1].text
                depTime = item.select('tr.fare-light-row')[i].select('div.avail-table-bold')[0].text
                arrAirport = item.select('tr.fare-light-row')[i].select('div.text-center > div')[3].text
                arrTime = item.select('tr.fare-light-row')[i].select('div.avail-table-bold')[1].text
                flight_info = item.select('div.carrier-hover-bold')[i].text.split()
                carrier = flight_info[0]
                flightNumber = flight_info[1]
            depAirport = ''.join(re.findall('\w', depAirport))
            arrAirport = ''.join(re.findall('\w', arrAirport))
            dct = {
                'depAirport%d' % i: depAirport + ' 从{}起飞'.format(depAirport),
                'depTime%d' % i: depTime + ' 起飞时间',
                'arrAirport%d' % i: arrAirport + ' 落地城市为{}'.format(arrAirport),
                'arrTime%d' % i: arrTime + ' 落地时间',
                'carrier%d' % i: carrier + ' 航班型号',
                'flightNumber%d' % i: flightNumber + ' 航班编号',
            }
            lst.append(dct)
        dct_each_day[num] = lst
        num += 1
    dct_all[date] = dct_each_day


def main():
    global dct_all
    today = datetime.datetime.now()
    th_lst = []  # 线程池
    sem = threading.Semaphore(20)  # 最大线程数20

    for i in range(180):
        date = str(today + datetime.timedelta(days=i)).split()[0]
        print(date)
        form_data['dd1'] = date
        th = threading.Thread(target=get_data_from, args=(host, date))
        th_lst.append(th)
        # get_data_from(host, date)

    for th in th_lst:
        with sem:
            th.start()

    for th in th_lst:
        th.join()

    # 排序
    keys = [i for i in dct_all.keys()]
    keys.sort()
    dct_all = {key: dct_all[key] for key in keys}
    with open('亚航数据.json', 'a', encoding='utf-8') as f:
        json.dump(dct_all, f, ensure_ascii=False)


if __name__ == '__main__':
    # 获取IP池
    get_proxies()
    # 临时存储数据
    dct_all = {}
    # dep = input('出发地')
    # arr = input('目的地')
    # year = input('年份')
    # mon = input('月份')
    # day = input('日期')
    # adt = input('成人数量')
    # chd = input('儿童数量')
    dep = 'JHB'  # 出发地
    arr = 'SYD'  # 目的地
    year = 2018  # 年份
    mon = 10  # 月份
    day = 18  # 日期
    adt = '1'  # 成年人数量
    chd = '0'  # 儿童数量
    form_data = {
        'o1': dep,
        'd1': arr,
        # 'dd1': '{}-{}-{}'.format(year, mon, day),
        'ADT': adt,
        'CHD': chd,
        'inl': '0',
        's': 'false',
        'mon': 'true',
        'cc': 'MYR'
    }
    host = 'https://booking.airasia.com/Flight/Select'
    main()
