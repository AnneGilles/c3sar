import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'WebTest',
    'cryptacular',
    'pyramid_beaker',
    'pyramid_simpleform',
    'pyramid_mailer',
    'boto',
    'fdfgen',
    ]

test_requirements = [
    'WebTest',
    'nose'
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='c3sar',
      version='0.1',
      description='c3sar',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Christoph Scheid',
      author_email='c@openmusiccontest.org',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='c3sar.tests',
      install_requires=requires,
      tests_require=test_requirements,
      entry_points="""\
      [paste.app_factory]
      main = c3sar:main
      """,
      paster_plugins=['pyramid'],
      )
