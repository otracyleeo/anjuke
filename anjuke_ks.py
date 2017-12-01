import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import csv
import codecs
from multiprocessing import Pool
import random
import time
import sys

ua_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        ]

headers = {'User-agent': random.choice(ua_list)}

def my_soup(url):
    response = requests.get(url, headers=headers, timeout=0.5)
    bs = BeautifulSoup(response.text, 'lxml')
    return bs

def get_page(url):
    try:
        soup = my_soup(url)
        result_li = soup.find_all('li', class_='list-item')
        # print(str(result_li[1]))
        for i in result_li:
            # print(type(i))   <class 'bs4.element.Tag'>
            # i里是每个li标签下的内容  将i转化为字符串形式
            page_text = str(i)
            page_soup = BeautifulSoup(page_text, 'lxml')
            result_href = page_soup.find_all('a', class_='houseListTitle')
            # result_href为a标签的列表，故只有第0个内容,即一个参数。获取每一个房源的url
            # print(result_href[0].attrs['href'])
            get_page_detail(result_href[0].attrs['href'])
        #判断下一页的标签是否为空，不为空则递归得到所有页面的url
        result_nextpage = soup.find_all('a', class_='aNxt')
        if len(result_nextpage) != 0:
            get_page(result_nextpage[0].attrs['href'])
        else:
            print('没有下一页了')
            # result_li获得包含所有li的list，[0][1]……可以取出各个li
    except RequestException:
        return ('bad requests')
        # print(type(response.text))   <class 'str'>

def my_strip(s):
    return str(s).replace(' ', '').replace('\n', '').replace('\t', '').strip()


def find_info(response):
    info = BeautifulSoup(str(response), 'lxml')
    detail = info.find_all('dd')
    return detail


def write_info(result):
    with codecs.open('aaaa.csv', 'a', 'utf_8_sig') as f:
        writer = csv.writer(f)
        writer.writerow(result)
        f.close()

def get_url(quyu, m, a, b):
    url = 'https://ks.anjuke.com/sale/' + quyu + '/a' + str(a) + '-b' + str(b) + '-m' + str(m) + '/'
    return url

# 详细页面的爬取
def get_page_detail(url):
    try:
        soup = my_soup(url)
        result_list = []
        house_title = soup.find_all('h3', class_='long-title')[0]
        house_price = soup.find_all('span', class_='light info-tag')[0]
        detail_1 = soup.find_all('div', class_='first-col detail-col')
        detail_2 = soup.find_all('div', class_='second-col detail-col')
        detail_3 = soup.find_all('div', class_='third-col detail-col')
        col_1 = find_info(detail_1)
        col_2 = find_info(detail_2)
        col_3 = find_info(detail_3)
        # print(type(my_strip(house_title.text)))  <class 'str'>
        title = my_strip(house_title.text)
        price = my_strip(house_price.text[:-1])
        community = my_strip(col_1[0].text)
        address = my_strip(col_1[1].find_all('p')[0].text)
        time = my_strip(col_1[2].text[:-1])
        style = my_strip(col_1[3].text)
        house_type = my_strip(col_2[0].text)
        floor_area = my_strip(col_2[1].text[:-3])
        orientation = my_strip(col_2[2].text)
        floor = my_strip(col_2[3].text)
        decoration = my_strip(col_3[0].text)
        unit_price = my_strip(col_3[1].text[:-4])
        result = [title, price, community, address, time, style, house_type, floor_area, orientation, floor, decoration,
                  unit_price]
        '''
        ['世茂东外滩景观在卖房中小区*，全新毛坯有钥匙看房方便', '140', '世茂东外滩', '玉山－城东－东城大道与景王路交汇处', '2016', '普通住宅', '3室2厅1卫', '96', '南北', '高层(共33层)', '毛坯', '14583']
        '''
        result_list.append(result)
        print(result)
        # with open('1.txt', 'a', encoding='UTF-8') as f:
        # f.write(str(result)+'\n')
        # f.close()
        write_info(result)
    except RequestException:
        return ('bad requests')


if __name__ == '__main__':
    start = time.clock()
    # quyu：地区 m：价格 a：面积 b：房型
    list = []
    for quyu in ('chengxikunshan', 'chengnankunshan', 'chengbeikunshan', 'kunshanchengdong', 'shiqukunshan', 'zhoushia',
                 'bachenga', 'zhangpua', 'lujiab', 'huaqiaob', 'qiandengb', 'zhouzhuanga', 'jinxig', 'dianshanhua'):
        for m in (345, 346, 347, 348, 349, 350, 351, 352, 353, 699):
            for a in range(307, 315):
                for b in range(267, 273):
                    url = get_url(quyu, m, a, b)
                    #list.append(url)
                    get_page(url)

    '''
    pool = Pool(30)
    pool.map(get_page, list)
    pool.close()
    pool.join()
    '''
    end = time.clock()
    print('程序运行时长为 %f 秒' % (end - start))










