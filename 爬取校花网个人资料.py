import os
import time
import random
import pymongo
import requests
import threading

from bs4 import BeautifulSoup
from urllib.request import urlretrieve

"""
爬取校花网个人信息
要求：文件夹以标题命名，
      文件夹内包含，照片，个人信息（以txt格式存储）
"""


def get_soup(url):
    response = requests.get(url)
    response.encoding = 'GBK'
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def get_url(url):
    soup = get_soup(url)
    # 观察网页结构，发现链接全部放在<li>标签内
    info = soup.select('#list_img > div.newsboxlist > ul > li > a')
    return info


def download(url, path, file_name):
    soup = get_soup(url)
    info = soup.select('div.content_wrap > p > span')
    imgs = soup.select('div.content_wrap > p > img')
    words = ''
    for i in info:
        words += i.contents[0] + '\n'
    print(words)
    file = open(path + '\\' + file_name + '.txt', 'wb')
    file.write(words.encode())
    file.close()

    for i in range(len(imgs)):
        src = r'http://www.xiaohuar.com' + imgs[i].get('src')
        urlretrieve(src, path + '\\' + str(i) + '.jpg')


def main():
    url = r'http://www.xiaohuar.com/2014.html'
    url_list = get_url(url)
    # 存储路径
    file_path = r'G:\爬虫--图片\校花网\\'
    for i in url_list:
        file_name = i.contents[0]
        url = i.get('href')
        os.makedirs(file_path + file_name, exist_ok=True)
        path = file_path + file_name
        print('开始下载', file_name, path)
        sem = threading.Semaphore(80)
        time.sleep(random.uniform(0.5, 2))
        with sem:
            th = threading.Thread(target=download, args=(url, path, file_name))
            th.start()


if __name__ == '__main__':
    main()
