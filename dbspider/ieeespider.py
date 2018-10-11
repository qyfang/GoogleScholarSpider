# -*- coding: UTF-8 -*-
from referencespider import ReferenceSpider

from bs4 import BeautifulSoup

import re

import json

import requests


class IEEESpider(ReferenceSpider):
    def __init__(self, targeturl):
        super(IEEESpider, self).__init__(targeturl)

        self.articlenumber = re.findall(r'document/.*?$', self.targeturl)[0].replace(r'document/', '').replace(r'/', '')
        self.refer_url_front = 'https://ieeexplore.ieee.org/rest/document/'
        self.refer_url_rear = '/references'

        self.crawlresult['id'] = 'IEEE-' + self.articlenumber

    def getContent(self, soup):
        soup_title = soup.select('title')
        if soup_title:
            title = soup_title[0].string.replace(' - IEEE Journals & Magazine', '').replace(' - IEEE Conference Publication', '')
            self.crawlresult['title'] = title

        str_authors = re.findall(r'{"name":.*?,', str(soup))
        for str_author in str_authors:
            author = str_author.replace('{"name":', '').replace('"', '').replace(',', '')
            self.crawlresult['authors'].append(author)

        str_keywords = re.findall(r'Author Keywords .*?]', str(soup))
        if str_keywords:
            str_keywords = str_keywords[0].replace('Author Keywords ","kwd":[', '').replace(']', '').replace('"', '')
            keywords = str_keywords.split(',')
            self.crawlresult['keywords'] = keywords

        str_abstract = re.findall(r',"abstract".*?","', str(soup))
        if str_abstract:
            abstract = str_abstract[0].replace(',"abstract":"', '').replace('","', '')
            self.crawlresult['abstract'] = abstract

        str_doi = re.findall(r'"doi":.*?,', str(soup))
        if str_doi:
            doi = str_doi[0].replace('"doi":"', '').replace('",','')
            self.crawlresult['doi'] = doi

    def getRefer(self, soup):
        url = self.refer_url_front + self.articlenumber + self.refer_url_rear
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'ieeexplore.ieee.org',
            'If-Modified-Since': '0',
            'Referer': self.targeturl,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        }

        for t in range(self.maxtryloadnum):
            try:
                response = requests.get(url,headers=headers)
            except:
                if t < (self.maxtryloadnum-1):  
                    continue
                else:
                    return

        restinfo = response.content
        restinfo = json.loads(restinfo)
        if restinfo.has_key('references'):
            references = restinfo['references']
            for x in references:
                refer = x['text']
                refer = refer.replace('<em>', '').replace('</em>', '').replace('\n', '')
                refer = refer.replace(' [online]  ', '')

                self.crawlresult['referitems'].append(refer) 
