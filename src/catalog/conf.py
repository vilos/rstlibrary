import os
import books


def configure(**kw):
    config = books.configure(**kw)
    return os.path.abspath(config.get('database'))