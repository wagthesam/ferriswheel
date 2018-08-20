from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean
import hashlib
import pickle

from utils import hash_str
from utils import session_scope

Base = declarative_base()

class Page(Base):

    class State(object):
        UNFETCHED = 0
        FETCHED   = 1
        PARSED    = 2
        PROCESSED = 3

    class PageType(object):
        UNKNOWN  = 0
        LIST     = 1
        DETAIL   = 2

    __tablename__ = 'page'

    page_id     =   Column(Integer, primary_key=True)
    url         =   Column(String(1024), unique=True)
    state       =   Column(Integer, default=State.UNFETCHED, index=True)
    page_type   =   Column(Integer, default=PageType.UNKNOWN)
    created_at  =   Column(DateTime, default=datetime.utcnow)

    def get_raw_contents(self):
        if self.state != self.State.UNFETCHED:
            with open('./datastore/object_store/raw_'+hash_str(self.url), 'r') as f:
                data=f.read()
                return data
        else:
            raise Exception('Not fetched yet')

    def save_raw_contents(self, contents):
        with open('./datastore/object_store/raw_'+hash_str(self.url), 'w') as f:
            f.write(contents)

    def get_contents(self):
        if self.state in (self.State.PARSED, self.State.PROCESSED):
            with open('./datastore/object_store/parsed_'+hash_str(self.url), 'rb') as f:
                data = pickle.load(f)
                return data
        else:
            raise Exception('Not parsed yet')

    def set_contents(self, contents):
        with open('./datastore/object_store/parsed_'+hash_str(self.url), 'wb') as f:
            data = pickle.dump(contents, f)