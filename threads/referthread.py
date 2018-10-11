# -*- coding:utf-8 -*-
import re

import requests

import threading

from bs4 import BeautifulSoup

class BaiduScholarThread(threading.Thread):
    def __init__(self, referitem):
        super(BaiduScholarThread, self).__init__()
        self.referitem = referitem
        self.referurl = ''

    def run(self):
        referitem = self.referitem
        url_search = 'http://xueshu.baidu.com/s?wd='
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'xueshu.baidu.com',
            'Upgrade-Insecure-Requests': '1',
            'refer': 'http://xueshu.baidu.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        wd = referitem.replace(' ', '+').replace(',', '%2C').replace(':', '%3A')
        bdurl = url_search + wd

        try:
            response = requests.get(bdurl, headers=headers, timeout=10)
            page = response.content
            soup = BeautifulSoup(page, 'html.parser')
        except:
            pass

        searchresults = soup.select('div[class="sc_content"]')
        for res in searchresults:
            title = res.select('h3 > a')
            if not title:
                continue
            else:
                title = title[0].text

            authors = []
            aus = res.select('a[data-click="{\'button_tp\':\'author\'}"]')
            for au in aus:
                author = au.text
                authors.append(author)
            
            try:
                pattern = re.compile(title, re.I|re.M)
                match1 = pattern.findall(referitem)
                match2 = True
            except:
                continue

            # for author in authors:
            #     pattern = re.compile(author, re.I|re.M)
            #     match = pattern.findall(referitem)
            #     if not match:
            #         match2 = False
            #         break

            if match1 and match2:
                url = ''
                source = res.select('a[class="v_source"]')
                for s in source:
                    sname = s['title']

                    if sname == 'Springer':
                        href = s['href']
                        flag = re.findall(r'http://link.springer.com/chapter/', href)
                        if flag:
                            href = href.replace(' ', '')
                            url = href
                            break

                    if sname == 'IEEEXplore':
                        href = s['href']
                        href = re.findall(r'document%2F.*?%2F', href)
                        if href:
                            ieeeid = href[0].replace('%2F', '').replace('document', '')
                            url = 'http://ieeexplore.ieee.org/abstract/document/'+ieeeid
                            break

                    if sname == 'ACM':
                        href = s['href']
                        href = re.findall(r'id%3D.*?%|id%3D.*?&', href)
                        if href:
                            acmid = href[0].replace('id%3D', '').replace('&', '').replace('%', '')
                            url = 'https://dl.acm.org/citation.cfm?id='+acmid
                            break

                    if sname == 'Elsevier':
                        href = s['href']
                        href = re.findall(r'pii%2F.*?&', href)
                        if href:
                            pii = href[0].replace('pii%2F', '').replace('&', '')
                            url = 'https://www.sciencedirect.com/science/article/pii/'+pii
                            break

                if url:
                    self.referurl = url
                    break
