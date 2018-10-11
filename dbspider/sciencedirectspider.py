# -*- coding: UTF-8 -*-
from referencespider import ReferenceSpider

from bs4 import BeautifulSoup

import re

import json
import requests

import urllib2
import cookielib


class ScienceDirectSpider(ReferenceSpider):
    def __init__(self, targeturl):
        super(ScienceDirectSpider, self).__init__(targeturl)

        self.entitledtoken = ''
        self.pii = re.findall(r'pii/.*?$', self.targeturl)[0].replace('pii/', '')
        self.refer_url_front = 'https://www.sciencedirect.com/sdfe/arp/pii/'
        self.refer_url_rear = '/references?entitledToken='

        self.crawlresult['id'] = 'SD-'+self.pii

    def getContent(self, soup):
        soup_title = soup.select('title')
        if soup_title:
            title = soup_title[0].string.replace(' - ScienceDirect', '')
            self.crawlresult['title'] = title

        str_authors = soup.select('span[class="content"]')
        for str_author in str_authors:
            author = ''
            author_names = str_author.select('.text')
            for name in author_names:
                author += name.text
            self.crawlresult['authors'].append(author)

        str_keywords = re.findall(r'"keyword".*?/span', str(soup))
        for str_keyword in str_keywords:
            keywords = re.sub(r'"keyword".*?<span>', '', str_keyword)
            keywords = keywords.replace('</span', '')
            self.crawlresult['keywords'].append(keywords)

        str_abstract = soup.select('div[class="abstract author"]')
        for sub_abstract in str_abstract:
            abstract = ''
            sub = sub_abstract.select('p')
            for s in sub:
                abstract += s.text
                self.crawlresult['abstract'] = abstract

        str_doi = soup.select('meta[name="citation_doi"]')
        if str_doi:
            doi = str_doi[0]['content']
            self.crawlresult['doi'] = doi

    def getRefer(self, soup):
        cookie = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(cookie)
        opener = urllib2.build_opener(handler)
        response = opener.open(self.targeturl)

        cookie_dict = {}
        cookies = ''
        for item in cookie:
            cookie_dict[item.name] = item.value
        for key, value in cookie_dict.items():
            cookies += key + '=' + value + '; '

        str_numbers = re.findall(r'"entitledToken":.*?,', str(response.read()))
        for str_number in str_numbers:
            str_num = re.sub(r'"entitledToken":.*?', '', str_number)
            str_num = str_num.replace('"', '').replace(',', '')
            self.entitledtoken += str_num

        url = self.refer_url_front + self.pii + self.refer_url_rear + self.entitledtoken

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'www.sciencedirect.com',
            'Referer': self.targeturl,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Cookie': cookies
        }

        response = requests.get(url, headers=headers)
        restinfo = response.content
        restinfo = json.loads(restinfo)

        if 'content' in restinfo:
            for item in restinfo['content'][0]['$$'][1]['$$']:
                refer = ''
                if len(item['$$'][1]['$$'][0]) > 2:
                    if len(item['$$'][1]['$$'][0]['$$']) > 1:
                        for author in item['$$'][1]['$$'][0]['$$'][0]['$$']:
                            if '$$' in author.keys():
                                for auth in author['$$']:
                                    refer += auth['_']
                                refer += ','
                        if len(item['$$'][1]['$$'][0]['$$'][1]['$$'][0]) <= 2:
                            if '$$' not in item['$$'][1]['$$'][0]['$$'][1]['$$'][0].keys():
                                paper = item['$$'][1]['$$'][0]['$$'][1]['$$'][0]['_']
                                refer += paper
                            else:
                                for papers in item['$$'][1]['$$'][0]['$$'][1]['$$'][0]['$$']:
                                    if '_' in papers.keys():
                                        paper = papers['_']
                                        refer += paper
                                    
                        self.crawlresult['referitems'].append(refer)
        else:
            self.crawlresult['referitems'] = ''