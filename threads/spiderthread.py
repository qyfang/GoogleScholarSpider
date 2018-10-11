# -*- coding:utf-8 -*-
import re

import threading

from referthread import BaiduScholarThread

class ReferenceSpiderThread(threading.Thread):
    def __init__(self, referencespider, lastroundflag):
        super(ReferenceSpiderThread, self).__init__()
        self.referencespider = referencespider
        self.lastroundflag = lastroundflag
        self.referurls = []

    def getReferId(self, referurl):
        ispdf = re.findall(r'.pdf$', referurl)
        if ispdf:
            return

        sort = re.findall(r'www\.sciencedirect\.com', referurl)
        if sort:
            pii = re.findall(r'pii/.*?$', referurl)[0].replace('pii/', '')
            referid = 'SD-' + pii
            return referid

        sort = re.findall(r'ieeexplore\.ieee\.org', referurl)
        if sort:
            articlenumber = re.findall(r'document/.*?$', referurl)[0].replace(r'document/', '').replace(r'/', '')
            referid = 'IEEE-' + articlenumber
            return referid
            
        sort = re.findall(r'link\.springer\.com', referurl)
        if sort:
            doi = re.findall(r'chapter.*?$', referurl)[0].replace(r'chapter/','')
            referid = 'Springer-' + doi
            return referid

        sort = re.findall(r'dl\.acm\.org', referurl)
        if sort:
            acmid = re.findall(r'id=.*?$', referurl)[0].replace('id=', '')
            referid = 'ACM-' + acmid
            return referid

    def getReferUrls(self, referitems):
        threads = []
        referids = []
        for referitem in referitems:
            thread = BaiduScholarThread(referitem)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
            referurl = thread.referurl
            if referurl:
                referid = self.getReferId(referurl)
                if referid:
                    self.referurls.append(referurl)
                    referids.append(referid)

        duplicate = lambda x,y:x if y in x else x + [y]
        referids = reduce(duplicate, [[], ] + referids)
        return referids

    def saveModel(self, crawlresult, rids):
        selfid = crawlresult['id']
        
        title = crawlresult['title']
        
        authors = ''
        for au in crawlresult['authors']:
            authors += au + ','
        authors = authors[:-1]

        keywords = ''
        for kw in crawlresult['keywords']:
            keywords += kw + ','
        keywords = keywords[:-1]

        referids = ''
        for r in rids:
            referids += r + ','
        referids =  referids[:-1]

        url = crawlresult['url']

        # obj,created = Reference.objects.get_or_create(selfid=selfid, 
        #     title=title, authors=authors, keywords=keywords, referids=referids, url=url)

    def run(self):
        loadflag = self.referencespider.analyzePage()
        
        if loadflag:
            crawlresult = self.referencespider.crawlresult
            referids = []
            if not self.lastroundflag:
                referitems = crawlresult['referitems']
                referids = self.getReferUrls(referitems)
            self.saveModel(crawlresult, referids)
