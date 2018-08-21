from model import Page
from utils import session_scope
from utils import find_ngrams
from collections import defaultdict
import math

class Search(object):
    # tf-idf
    # no length normalization
    def __init__(self, application):
        self.application = application

    def search(self, search_str, top_n=20):
        # relevance:
        # tf-idf
        # boost matches that contain all words
        # boost title, director, and stars fields in text
        search_str = search_str.lower().strip()
        if self.application.index.built is False:
            print('Index missing!')
            self.build_index()
        doc_scores = defaultdict(float)
        wc_index = self.application.index.wc
        global_wc_index = self.application.index.global_wc
        doc_count = self.application.index.docs_count

        for n in range(11):
            for ngram in find_ngrams(search_str.split(' '), n):
                if ngram in wc_index:
                    for doc in wc_index[ngram]:
                        doc_scores[doc] += wc_index[ngram][doc]*math.log(doc_count/len(global_wc_index.get(ngram, [1])))

        # every word in search query needs to be in a returned doc
        missing_filter = set()
        for doc in list(doc_scores.keys()):
            for word in search_str.split(' '):
                if doc not in wc_index[word]:
                    missing_filter.add(doc)

        top_results = [x[1] for x in 
            sorted([(doc_scores[doc], doc) for doc in doc_scores], reverse=True)[:top_n]]
        second_pass = []
        for doc in top_results:
            if doc not in missing_filter:
                second_pass.append(doc)
        for doc in top_results:
            if doc in missing_filter:
                second_pass.append(doc)

        with session_scope(self.application.Session) as session:
            top_results_pages = session.query(Page).filter(Page.page_id.in_(second_pass)).all()
            top_results_full = [x.get_contents()['title'] for x in top_results_pages]

            print("Search results:")
            for title in top_results_full:
                print('-', title)

    def build_index(self):
        print('Building index...')
        with session_scope(self.application.Session) as session:
            for page in session.query(Page).filter(
                Page.state == Page.State.PROCESSED).filter(
                Page.page_type == Page.PageType.DETAIL).all():
                self.ingest(page)
        self.application.index.built = True
        print('Index built!')

    def ingest(self, page):
        boost = {
            'title': 2.0,
            'director': 1.5,
            'stars': 1.5
        }

        contents = page.get_contents()

        wc_index = self.application.index.wc
        global_wc_index = self.application.index.global_wc

        for field in ['title',
            'year',
            'director',
            'writers',
            'stars',
            'cast',
            'characters']:
            cur_field = contents.get(field, '')
            weight = boost.get(field, 1)
            if type(cur_field) == list:
                for words in cur_field:
                    words = words.lower().split(' ')
                    for n in range(11):
                        for ngram in find_ngrams(words, n):
                            wc_index[ngram][page.page_id] += weight
                            global_wc_index[ngram].add(page.page_id)
            elif type(cur_field) == str:
                words = cur_field.lower().split(' ')
                for n in range(11):
                    for ngram in find_ngrams(words, n):
                        wc_index[ngram][page.page_id] += weight
                        global_wc_index[ngram].add(page.page_id)
            self.application.index.docs_count += 1