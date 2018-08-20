import hashlib
import contextlib

def hash_str(input_str):
    h = hashlib.sha1()
    h.update(input_str.encode('utf-8'))
    return h.hexdigest()

@contextlib.contextmanager
def session_scope(Session):
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.expunge_all()
        session.close()

def find_ngrams(input_list, n):
  return [' '.join(x) for x in zip(*[input_list[i:] for i in range(n)])]