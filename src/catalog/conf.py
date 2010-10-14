import os
import books


def configure():
    config = books.configure()
    return os.path.abspath(config.get('database'))