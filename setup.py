import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
            'repoze.bfg',
            'docutils',
            'ore.xapian',
            'WebError'
            ]

setup(name='rstlibrary',
      version='0.1.0',
      description='rstlibrary',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: BFG",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Viliam Segeda',
      author_email='viliam@vasudevaserver.org',
      url='',
      keywords='web wsgi bfg',
      package_dir = {'':'src'},
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="books.tests",
      entry_points = """\
      [paste.app_factory]
      app = library.run:app
      """
      )

