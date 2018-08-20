import os

class Config(object):
    ROOT_NODES = ['https://www.imdb.com/search/title?groups=top_1000&sort=user_rating&view=simple']
    WORKER_THREADS = 4
    DB = 'metadata.db'
    SCRAPE_ROOT_PATH = 'https://www.imdb.com'