#!/usr/local/bin/env python3
# encoding: utf-8

from setting import headers, wait_sec, domain
from bs4 import BeautifulSoup
import requests
import time

def get_cars(brand_name, start_url):
    print('start_url: ', start_url)
    cars = []

    headers['referer'] = start_url
    now_url = start_url # 设置起始抓取页面
    next_url = '' # next_url 为空时结束抓取, 返回数据的条件

    while True:
        result = requests.get(now_url, headers=headers)
        print(result.request.headers)
        html_content = result.content.decode('gb18030').encode('utf-8')
        html_content_soup = BeautifulSoup(html_content, 'html.parser')
        cars_tag = html_content_soup.find_all(class_='list-cont-bg')
        # 结束逻辑
        # 1. 一开始就没有翻页
        # 2. 唯一获取 page-item-next
        # 3. 循环
        if html_content_soup.find(class_="price-page") is None:
            next_url = ''
        else:
            next_url_tag = html_content_soup.find(class_="price-page").find(class_="page-item-next")
            # 结束翻页
            if next_url_tag['href'] == 'javascript:void(0)':
                next_url = ''
            else:
                next_url = domain + next_url_tag['href']
        print('next_url is ', next_url)
        for car_tag in cars_tag:
            car = {}
            car['brand'] = brand_name
            car['url'] = now_url
            car['name'] = car_tag.find(class_='main-title').get_text(strip=True)
            car['price'] = car_tag.find(class_='font-arial').get_text(strip=True)
            # @TODO 颜色还有问题
            for car_attr_tag in car_tag.find('ul', class_='lever-ul').find_all('li'):
                car_attr = car_attr_tag.get_text(',',strip=True)
                if len(car_attr.split(u'：')) < 2 :
                    continue
                car_attr_key = car_attr.split(u'：')[0]
                car_attr_value = car_attr.split(u'：')[1]
                # 直接空格无效，因为 gbk 无法转换 '\xa0' 字符(http://www.educity.cn/wenda/350839.html)
                car_attr_key = car_attr_key.replace(u'\xa0', '')
                car[car_attr_key] = car_attr_value.strip(',')
            cars.append(car)
        time.sleep(wait_sec)
        # 抓取结束, 返回数据
        if next_url == '':
            return cars

        # 更换页面
        now_url = next_url
