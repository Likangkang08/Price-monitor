#!/usr/bin/env python3
# coding=utf-8
import re
import logging
from json import decoder

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException,NoSuchWindowException
from selenium.webdriver.chrome.options import Options
import time
import json


class Crawler(object):

    def __init__(self, proxy=None):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu') #关闭硬件加速器
        chrome_options.add_argument('--no-sandbox') #取消沙盒模式
        chrome_options.add_argument('--start-maximized ')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        if proxy:
            proxy_address = proxy['https']
            chrome_options.add_argument('--proxy-server=%s' % proxy_address)
            logging.info('Chrome using proxy: %s', proxy['https'])
        self.chrome = webdriver.Chrome(chrome_options=chrome_options)
        # wait 5 seconds for start session (may delete)
        self.chrome.implicitly_wait(5)
        # set timeout like requests.get()
        # jd sometimes load google pic takes much time
        self.chrome.set_page_load_timeout(20)
        # set timeout for script
        self.chrome.set_script_timeout(20)

    def get_jd_item(self, item_id):
        # 这个方法的功能：
        #                参数说明：itme_id 是要爬取京东网页的后三位。
        #                1.主要是爬取商品的名字、价格、会员价格、标题
        #                2.再将获取到的内容添加到一个集合中
        #                3.返回这个集合。
        item_info_dict = {"name": None, "price": None, "plus_price": None, "subtitle": None}
        #变量url
        url = 'https://item.jd.com/' + item_id + '.html'

        try:
            self.chrome.get(url)
        except TimeoutException as e:
            logging.warning('Crawl failure: {}'.format(e))
            return item_info_dict
        except NoSuchWindowException as e:
            logging.warning('Crawl failure: {}'.format(e))
            return  item_info_dict

        # 提取商品名称
        try:
            #获取商品名称并且储存到集合
            name = self.chrome.find_element_by_xpath("//*[@class='sku-name']").text
            item_info_dict['name'] = name
        except AttributeError as e:
            logging.warning('Crawl name failure: {}'.format(e))
        except NoSuchElementException:
            try:
                # 加油卡(如200117841739）需要改为提取name
                name = self.chrome.find_element_by_xpath("//*[@class='name']").text
                item_info_dict['name'] = name
            except NoSuchElementException as e:
                logging.warning('Crawl name failure: {}'.format(e))

        # 提取商品PLUS价格
        try:  # 海外购(32533649560)页面无p-price-plus元素，直接保留为None
            plus_price = self.chrome.find_element_by_xpath("//*[@class='p-price-plus']").text
            if plus_price:
                plus_price_xpath = re.findall(r'-?\d+\.?\d*e?-?\d*?', plus_price)
                item_info_dict['plus_price'] = plus_price_xpath[0]  # 提取浮点数
        except AttributeError as e:
            logging.warning('Crawl plus_price failure: {}'.format(e))
        except NoSuchElementException as e:
            logging.warning('Crawl plus_price failure: {}'.format(e))

        # 提取商品副标题
        try:
            subtitle = self.chrome.find_element_by_xpath("//*[@id='p-ad']").text
            item_info_dict['subtitle'] = subtitle
        except AttributeError as e:
            logging.warning('Crawl subtitle failure: {}'.format(e))
        except NoSuchElementException:
            try:
                # 加油卡200117841739需要改为提取name-s
                subtitle = self.chrome.find_element_by_xpath("//*[@class='name-s']").text
                item_info_dict['subtitle'] = subtitle
            except NoSuchElementException as e:
                logging.warning('Crawl subtitle failure: {}'.format(e))

        # 提取商品价格
        try:
            price = self.chrome.find_element_by_xpath("//*[@class='p-price']").text
            if price:
                price_xpath = re.findall(r'-?\d+\.?\d*e?-?\d*?', price)
                if price_xpath:  # 若能提取到值
                    item_info_dict['price'] = price_xpath[0]  # 提取浮点数
        except AttributeError as e:
            logging.warning('Crawl price failure: {}'.format(e))
        except NoSuchElementException as e:
            logging.warning('Crawl price failure: {}'.format(e))
            return item_info_dict

        logging.info('Crawl SUCCESS: {}'.format(item_info_dict))
        self.chrome.quit()
        return item_info_dict

    def get_huihui_item(self, item_id):
        huihui_info_dict = {"max_price": None, "min_price": None}
        url = 'https://zhushou.huihui.cn/productSense?phu=https://item.jd.com/' + item_id + '.html'
        try:
            self.chrome.get(url)
            url_text = self.chrome.find_element_by_tag_name('body').text
            info = json.loads(url_text)
            huihui_info_dict = {"max_price": info['max'], "min_price": info['min']}
            logging.info(huihui_info_dict)
        except decoder.JSONDecodeError as e:
            logging.warning('Crawl failure: {}'.format(e))
        except NoSuchElementException as e:
            logging.warning('Crawl failure: {}'.format(e))
        except TimeoutException as e:
            logging.warning('Crawl failure: {}'.format(e))
        self.chrome.quit()
        return huihui_info_dict


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start = time.time()
    c = Crawler()
    # c = Crawler({'http': '125.105.32.168:7305', 'https': '171.211.32.79:2456'})
    logging.debug(c.get_jd_item('5544068'))
    # logging.debug(c.get_huihui_item('2777811'))
    end = time.time()
    print(end - start)
