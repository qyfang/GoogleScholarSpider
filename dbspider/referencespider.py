# -*- coding: UTF-8 -*-
import requests

from bs4 import BeautifulSoup

class ReferenceSpider(object):
    def __init__(self, targeturl):
        self.maxtryloadnum = 3

        self.targeturl = targeturl
        self.targetheaders = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        }

        self.crawlresult = {}
        self.crawlresult['url'] = targeturl
        self.crawlresult['id'] = ''
        self.crawlresult['doi'] = ''
        self.crawlresult['title'] = ''
        self.crawlresult['authors'] = []
        self.crawlresult['keywords'] = []
        self.crawlresult['abstract'] = '' 
        self.crawlresult['referitems'] = []

    def showGeneralInfo(self):
        print self.crawlresult['id']
        print self.crawlresult['url']
        print self.crawlresult['title']
        print ''

    def loadPage(self):
        for t in range(self.maxtryloadnum):
            try:
                response = requests.get(self.targeturl, headers=self.targetheaders,timeout=10)
                page = response.content
                soup = BeautifulSoup(page, 'html.parser')
                return soup
            except:
                if t < self.maxtryloadnum - 1:  
                    continue
                else:
                    return None 

    def getContent(self, soup):
        pass

    def getRefer(self, soup):
        pass

    def analyzePage(self):
        soup = self.loadPage()
        if soup:
            self.getContent(soup)
            self.getRefer(soup)
            return True
        else:
            return False