import books


def configure():
    config = books.configure()
    return config.get('database')