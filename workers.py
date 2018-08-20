from model import Page
from utils import session_scope
import random
import logging
import urllib
from sqlalchemy.sql import exists
from bs4 import BeautifulSoup
import re
import sys

class Processor(object):
    def __init__(self, application):
        self.application = application

    def process(self, page_id):
        with session_scope(self.application.Session) as session:
            page = session.query(Page).get(page_id)
            if page.state == Page.State.UNFETCHED:
                self.fetch(page)
                self.application.queue.add_page(page_id)
            elif page.state == Page.State.FETCHED:
                self.parse(page)
                self.application.queue.add_page(page_id)
            elif page.state == Page.State.PARSED:
                if page.page_type == Page.PageType.LIST:
                    self.process_list(page)

    def parse(self, page):
        soup = BeautifulSoup(page.get_raw_contents(), 'html.parser')
        if 'Top 1000' in soup.title.string:
            logging.debug('Parsing list %s' % page.url)
            doc = []
            for movie in soup.find_all('span', attrs={'class': 'lister-item-header'}):
                url = movie.find('a')['href'].split("?")[0]
                doc.append(url)
            next_page = soup.find('a', attrs={'class': 'lister-page-next next-page'})
            if next_page:
                root = self.application.config.ROOT_NODES[0]
                end_idx = root.find('?')
                doc.append(root[:end_idx]+next_page['href'])
            with session_scope(self.application.Session) as session:
                page.state = Page.State.PARSED
                page.page_type = Page.PageType.LIST
            logging.debug('Parsed list %s' % page.url)
        else:
            logging.debug('Parsing detail %s' % page.url)
            page_type = Page.PageType.DETAIL
            doc = {}
            title_div = soup.find('div', attrs={'class': 'title_wrapper'}).h1.text.split('\xa0')
            doc['title'] = title_div[0]
            doc['year'] = int(title_div[1][title_div[1].find('(')+1:title_div[1].find(')')])
            try:
                doc['director'] = soup.find('h4', text=re.compile('Director:')).parent.a.text
            except AttributeError:
                pass
            doc['writers'] = []
            try:
                for writer in soup.find('h4', text=re.compile('Writers:')).parent.findAll('a'):
                    doc['writers'].append(writer.text)
            except AttributeError:
                pass
            doc['stars'] = []
            try:
                for writer in soup.find('h4', text=re.compile('Stars:')).parent.findAll('a'):
                    doc['stars'].append(writer.text)
            except AttributeError:
                pass
            doc['cast'] = []
            doc['characters'] = []
            try:
                for n, cast in enumerate(soup.find(attrs={'class': 'cast_list'}).findAll('a')):
                    if n % 3 == 1:
                        doc['cast'].append(cast.text.replace('\n', ''))
                    elif n % 3 == 2:
                        doc['characters'].append(cast.text)
            except AttributeError:
                pass
            with session_scope(self.application.Session) as session:
                page.state = Page.State.PROCESSED
                page.page_type = Page.PageType.DETAIL
            logging.debug('Parsed detail %s' % page.url)
        page.set_contents(doc)

    def fetch(self, page):
        logging.debug('Fetching %s' % page.url)
        try:
            resource = urllib.request.urlopen(page.url)
        except Exception as e:
            print('COULD NOT OPEN', page.url)
            raise(e)
        with session_scope(self.application.Session) as session:
            contents = resource.read().decode(resource.headers.get_content_charset())
            page.save_raw_contents(contents)
            page.state = Page.State.FETCHED
        logging.debug('Fetched %s' % page.url)

    def process_list(self, page):
        queue = self.application.queue
        logging.debug('Processing list %s' % page.url)
        processed = 0
        if page.state == Page.State.PARSED:
            with session_scope(self.application.Session) as session:
                for url in page.get_contents():
                    (page_exists, ), = session.query(exists().where(Page.url==url))
                    if not page_exists:
                        if 'http' not in url:
                            url = self.application.config.SCRAPE_ROOT_PATH+url
                        subpage = Page(url=url)

                        session.add(subpage)
                        session.commit()
                        queue.add_page(subpage.page_id)
                        processed += 1
                page.state = Page.State.PROCESSED
            logging.debug('Processed list %s' % page.url)
            print('Processed %s urls! Fetching movies & getting more movie urls...' % processed)
        else:
            logging.debug('Aleady processed list %s' % page.url)