import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'liblightbase',
    'argparse == 1.3.0',
    'ConfigParser == 3.3.0r2',
    'elasticsearch == 1.4.0',
    'linecache2 == 1.0.0',
    'ordereddict == 1.1',
    'pyelasticsearch == 0.6.1',
    'requests == 2.3.0',
    'simplejson == 3.5.3',
    'six == 1.7.2',
    'traceback2 == 1.4.0',
    'unittest2 == 1.0.1',
    'urllib3 == 1.10.4',
    'pyramid == 1.6b2',
    'pyramid_chameleon == 0.3',
    'waitress == 1.4.1'
]

'''
NOTE: Para versionamento usar "MAJOR.MINOR.REVISION.BUILDNUMBER"! By Questor
http://programmers.stackexchange.com/questions/24987/what-exactly-is-the-build-number-in-major-minor-buildnumber-revision
'''
setup(
    name = "LBIndex",
    version = "1.0.0.0",
    long_description=README + "\n\n" + CHANGES,
    author = "LightBase",
    author_email = "",
    url = "https://pypi.python.org/pypi/LBIndex",
    description = "Indexer Daemon for the neo-lightbase service",
    license = "GPLv2",
    keywords = "index elasticsearch lightbase daemon web pyramid pylons",
    install_requires=requires,
    tests_require=requires,
    test_suite="lbiapi",
    entry_points="""\
    [paste.app_factory]
    main = lbiapi:main
    """,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: No Input/Output (Daemon)",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Natural Language :: Portuguese (Brazilian)",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Framework :: Pyramid"
    ]
)
