import os
import books


def configure(ini='develop'):
    config = books.configure(ini)
    return os.path.abspath(config.get('database'))