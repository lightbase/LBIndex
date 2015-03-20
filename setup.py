from setuptools import setup, find_packages

requires = [
    'ConfigParser',
    'requests',
    'pyelasticsearch',
    ]

setup(
    name = "LBIndex",
    version = "0.1.2",
    author = "Lightbase",
    author_email = "pedro.ricardo@lightbase.com.br",
    url = "https://pypi.python.org/pypi/LBIndex",
    description = "Indexer Daemon for the neo-lightbase service",
    license = "GPLv2",
    keywords = "index elasticsearch lightbase daemon",
    install_requires=requires,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: No Input/Output (Daemon)",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Natural Language :: Portuguese (Brazilian)",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database :: Database Engines/Servers",
    ]
)
