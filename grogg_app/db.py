from flask import current_app, g

def get_db():
    if 'db' not in g:
        raise NotImplementedError
    else:
        raise NotImplementedError
    return g.db


def close_db():
    raise NotImplementedError

