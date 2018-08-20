from collections import defaultdict

class Index(object):
     # our index. Thread safe due to GIL
    def __init__(self):
        self.wc = defaultdict(lambda: defaultdict(float))
        self.global_wc = defaultdict(set)
        self.docs_count = 0
        self.built = False