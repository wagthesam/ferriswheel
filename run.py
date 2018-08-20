from collections import defaultdict
from IPython import embed
from IPython.terminal.embed import InteractiveShellEmbed
from config.prod import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
import contextlib
import shutil
import os
from threading import Thread
from queue import Queue 
import hashlib

from utils import hash_str
from utils import session_scope

from model import Page, Index, Base
from workers import Processor
from search import Search

class TaskQueue(Queue):

    def __init__(self, application, num_workers=1):
        Queue.__init__(self)
        self.application = application
        self.num_workers = num_workers
        self.processor = Processor(application)
        self.start_workers()

    def add_page(self, task):
        self.put(task)

    def start_workers(self):
        for i in range(self.num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def worker(self):
        while True:
            page = self.get()
            self.processor.process(page)
            self.task_done()

class Application(object):
    config = Config

    def __init__(self):
        self.index = Index()
        self.__init_db()    
        self.queue = TaskQueue(application=self,
                               num_workers=self.config.WORKER_THREADS)
        self.search_module = Search(application=self)

    def __init_db(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print(dir_path)
        self.db_path = "sqlite:///%s/datastore/%s" % \
            (dir_path, self.config.DB)
        self.engine = create_engine(self.db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def init(self):
        print('Starting scraper! Fetching documents')
        pages_added = 0
        with session_scope(self.Session) as session:
            if session.query(Page).count() == 0:
                for i in self.config.ROOT_NODES:
                    page = Page(url=i)
                    session.add(page)
                    session.commit()
                    self.queue.add_page(page.page_id)
                    pages_added += 1
            else:
                for page in session.query(Page).filter(Page.state != Page.State.PROCESSED).all():
                    self.queue.add_page(page.page_id)
                    pages_added += 1
            session.expunge_all()

        print('Started pipeline! Added %s root pages to processing queue' % pages_added)
        self.queue.join()
        print("Finished processing!")
        app.search_module.build_index()

    def search(self, search_str):
        return self.search_module.search(search_str)

    def rebuild(self):
        self.reset()
        self.init()
        self.search_module.build_index()

    def reset(self):
        meta = Base.metadata
        with session_scope(self.Session) as session:
            for table in reversed(meta.sorted_tables):
                session.execute(table.delete())
            session.commit()
        Base.metadata.create_all(self.engine)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        folder = "%s/datastore/object_store" % dir_path
        for cur_file in os.listdir(folder):
            file_path = os.path.join(folder, cur_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    banner = '''

Welcome to IMDB Search.
Commands:
- app.init(): runs scraper, builds the document corpus and search index
- search(search_str): returns relevant movies for the given search string

Admin commands:
- app.reset(): reruns scraper, rebuilds the document corpus and search index
'''
    exit_msg = ''
    app = Application()
    ipshell = InteractiveShellEmbed(banner1=banner, exit_msg=exit_msg)

    ipshell()