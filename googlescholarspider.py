# -*- coding:utf-8 -*-
import re

import time

import copy

import requests

from bs4 import BeautifulSoup

from threads.spiderthread import ReferenceSpiderThread

from dbspider.acmspider import ACMSpider

from dbspider.ieeespider import IEEESpider

from dbspider.springerspider import SpringerSpider

from dbspider.sciencedirectspider import ScienceDirectSpider


class SpiderConfig(object):
    def __init__(self):
        self.config = {}
        self.config['keyword'] = ''
        self.config['depth'] = 0
        self.config['breadth'] = 0

        self.config['googlescholar_base'] = ''
        self.config['headers'] = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'c3.glgooo.top',
            'Referer': 'https://c3.glgooo.top/scholar/',
            'Upgrade-Insecure-Requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }

    def set_config(self, key, val):
        if key and val and key in self.config.keys():
            self.config[key] = val


class GoogleScholarSpider(object):
    def __init__(self, spiderconfig):
        self.spiderconfig = spiderconfig.config

        self.nextround_urls = {}
        self.nextround_urls['ScienceDirect'] = []
        self.nextround_urls['IEEE'] = []
        self.nextround_urls['Springer'] =[]
        self.nextround_urls['ACM'] = []

    def duplicateThisRoundUrls(self, thisround_urls):
        duplicate = lambda x,y:x if y in x else x + [y]
        for db in ['ScienceDirect','IEEE','Springer','ACM']:
            urls = thisround_urls[db]
            urls = reduce(duplicate, [[], ] + urls)
            thisround_urls[db] = urls 
        return thisround_urls

    def resetNextRoundUrls(self):
        self.nextround_urls['ScienceDirect'] = []
        self.nextround_urls['IEEE'] = []
        self.nextround_urls['Springer'] = []
        self.nextround_urls['ACM'] = []

    def sortUrl(self, url):
        ispdf = re.findall(r'.pdf$', url)
        if ispdf:
            return 'other'

        sort = re.findall(r'www\.sciencedirect\.com', url)
        if sort:
            return 'ScienceDirect'

        sort = re.findall(r'ieeexplore\.ieee\.org', url)
        if sort:
            return 'IEEE'

        sort = re.findall(r'link\.springer\.com', url)
        if sort:
            return 'Springer'

        sort = re.findall(r'dl\.acm\.org', url)
        if sort:
            return 'ACM'

        return 'other'

    def generateSpider(self, db, url):
        if db == 'ScienceDirect':
            referencespider = ScienceDirectSpider(url)
            return referencespider

        if db == 'IEEE':
            referencespider = IEEESpider(url)
            return referencespider

        if db == 'Springer':
            referencespider = SpringerSpider(url)
            return referencespider

        if db == 'ACM':
            referencespider = ACMSpider(url)
            return referencespider

    def getFirstRoundUrls(self):
        url_base = self.spiderconfig['googlescholar_base']
        url_base += '&q=' + self.spiderconfig['keyword']
        url_base += '&start='

        isfull = 0
        pagenum = 0
        urlnum = 0
        while True:
            url = url_base + str(pagenum * 10)
            time.sleep(3)
            response = requests.get(url, headers=self.spiderconfig['headers'], timeout=10)
            page = response.content
            soup = BeautifulSoup(page, 'html.parser')

            gsrt_list = soup.select('.gs_rt > a')
            for gsrt in gsrt_list:
                if urlnum < self.spiderconfig['breadth']:
                    url = gsrt['href']
                    sort = self.sortUrl(url)
                    if sort != 'other':
                        print url
                        self.nextround_urls[sort].append(url)
                        urlnum += 1
                else:
                    isfull = 1
                    break

            if not gsrt_list or isfull:
                break
            else:
                pagenum += 1

    def crawl(self, request):
        self.getFirstRoundUrls()

        i = 0
        lastroundflag = False
        for crawldepth in range(1, self.spiderconfig['depth']+1):
            if crawldepth == self.spiderconfig['depth']:
                lastroundflag = True

            thisround_urls = copy.deepcopy(self.nextround_urls)
            thisround_urls = self.duplicateThisRoundUrls(thisround_urls)
            self.resetNextRoundUrls()

            threads = []
            for db in ['ScienceDirect','IEEE','Springer','ACM']:
                urls = thisround_urls[db]
                for url in urls:
                    referencespider = self.generateSpider(db, url)
                    thread = ReferenceSpiderThread(referencespider, lastroundflag)
                    i += 1
                    thread.start()
                    threads.append(thread)
                    thread.join()

                    senddata = str(str(i) + '-' + referencespider.crawlresult['title'])
                    print senddata
                    # request.websocket.send(senddata)
                    
            for thread in threads:
                thread.join()

            referurls = []
            for thread in threads:
                referurls.extend(thread.referurls)

            for referurl in referurls:
                referurl = referurl
                sort = self.sortUrl(referurl)
                if sort != 'other':
                    self.nextround_urls[sort].append(referurl)


def webcrawl(request, keyword, breadth, depth):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    spiderconfig = SpiderConfig()
    spiderconfig.set_config('googlescholar_base', 'https://c3.glgooo.top/scholar?hl=zh-CN')
    spiderconfig.set_config('keyword', keyword)
    spiderconfig.set_config('breadth', breadth)
    spiderconfig.set_config('depth', depth)

    spider = GoogleScholarSpider(spiderconfig)
    spider.crawl(request)


if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    spiderconfig = SpiderConfig()
    spiderconfig.set_config('googlescholar_base', 'https://c3.glgooo.top/scholar?hl=zh-CN')
    spiderconfig.set_config('keyword', 'fire')
    spiderconfig.set_config('breadth', 3)
    spiderconfig.set_config('depth', 2)

    spider = GoogleScholarSpider(spiderconfig)
    spider.crawl(1)