# -*- coding: UTF-8 -*-
from referencespider import ReferenceSpider

from bs4 import BeautifulSoup

import re

import json

import requests


class SpringerSpider(ReferenceSpider):
    def __init__(self, targeturl):
        super(SpringerSpider, self).__init__(targeturl)

    def getContent(self, soup):
        soup_title = soup.select('title')
        if soup_title:
            title = soup_title[0].string
            title = title.replace(' | SpringerLink', '')
            self.crawlresult['title'] = title

        soup_authors = soup.select('meta[name="citation_author"]')
        for soup_author in soup_authors:
            author = soup_author['content']
            self.crawlresult['authors'].append(author)

        soup_keywords = soup.select('span[class="Keyword"]')
        for soup_keyword in soup_keywords:
            keyword = soup_keyword.string
            if keyword is not None:
                keyword = keyword[:-1]
                self.crawlresult['keywords'].append(keyword)

        soup_abstract = soup.select('p[class="Para"]')
        if soup_abstract:
            abstract = soup_abstract[0].text
            self.crawlresult['abstract'] = abstract

        soup_doi = soup.select('meta[name="citation_doi"]')
        if soup_doi:
            doi = soup_doi[0]['content']
            self.crawlresult['doi'] = doi
            self.crawlresult['id'] = 'Springer-' + doi

    def getRefer(self, soup):
        soup_refers = soup.select('div[class="CitationContent"]')
        for soup_refer in soup_refers:

            refer = soup_refer.text
            refer = refer.replace('\n', '').replace('Google Scholar', '')
            self.crawlresult['referitems'].append(refer)
