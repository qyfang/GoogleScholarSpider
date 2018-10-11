# -*- coding: UTF-8 -*-
from referencespider import ReferenceSpider

from bs4 import BeautifulSoup

import re

import json

import requests


class ACMSpider(ReferenceSpider):
    def __init__(self, targeturl):
        super(ACMSpider, self).__init__(targeturl)
        self.acmid = re.findall(r'id=.*?$', self.targeturl)[0].replace('id=', '')
        self.clientid = ''
        self.abstract_url_front = 'https://dl.acm.org/tab_abstract.cfm?id='
        self.abstract_url_rear = '&type=Article&usebody=tabbody&_cf_containerId=cf_layoutareaabstract&_cf_nodebug=true&_cf_nocache=true&_cf_rc=0&_cf_clientid='
        self.refer_url_front = 'https://dl.acm.org/tab_references.cfm?id='
        self.refer_url_rear = '&type=article&usebody=tabbody&_cf_containerId=cf_layoutareareferences&_cf_nodebug=true&_cf_nocache=true&_cf_rc=1&_cf_clientid='
        
        self.crawlresult['id'] = 'ACM-' + self.acmid

    def getContent(self, soup):
        soup_title = soup.select('meta[name="citation_title"]')
        if soup_title:
            title = soup_title[0]['content']
            self.crawlresult['title'] = title
        
        soup_authors = soup.select('a[title="Author Profile Page"]')
        for soup_author in soup_authors:
            author = soup_author.string
            self.crawlresult['authors'].append(author)

        soup_keywords = soup.select('div[id="authortags"] > a')
        for soup_keyword in soup_keywords:
            keyword = soup_keyword.text
            self.crawlresult['keywords'].append(keyword)

        clientid = re.findall(r'_cf_clientid=.*?;', str(soup))
        if clientid:
            self.clientid = clientid[0].replace('_cf_clientid=\'', '').replace('\';', '')
        url = self.abstract_url_front + self.acmid + self.abstract_url_rear + self.clientid
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': self.targeturl,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        }
        for t in range(self.maxtryloadnum):
            try:
                response = requests.get(url, headers=headers)
            except:
                if t < (self.maxtryloadnum-1):  
                    continue
                else:
                    # print 'fail to load acm abstract'
                    return
        page_abstract = response.content
        soup_abstract = BeautifulSoup(page_abstract, 'html.parser')
        soup_abstract = soup_abstract.select('div[style="display:inline"]')
        if soup_abstract:
            abstract = soup_abstract[0].text
            self.crawlresult['abstract'] = abstract

        soup_doi = soup.select('meta[name="citation_doi"]')
        if soup_doi:
            doi = soup_doi[0]['content']
            self.crawlresult['doi'] = doi

    def getRefer(self, soup):
        url = self.refer_url_front + self.acmid + self.refer_url_rear + self.clientid
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': self.targeturl,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        }

        for t in range(self.maxtryloadnum):
            try:
                response = requests.get(url, headers=headers)
            except:
                if t < (self.maxtryloadnum-1):  
                    continue
                else:
                    # print 'fail to get refer'
                    return
        
        page_refer = response.content
        soup_refer = BeautifulSoup(page_refer, 'html.parser')
        referlist = soup_refer.select('td > div')
        
        for str_refer in referlist:
            if str_refer.get('class'):
                continue
            a = str_refer.select('a')
            if a:
                str_refer = a[0]

            refer = str_refer.string
            if refer:
                refer = refer.replace('\n', '')
                self.crawlresult['referitems'].append(refer)
