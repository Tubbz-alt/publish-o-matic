try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='publish-o-matic',
    version="1.0",
    author='NHS England',
    author_email='',
    license="MIT",
    url='http://github.com/nhsengland/publish-o-matic/',
    description="A collections of scripts and tools to simplify publishing NHS England data",
    zip_safe=False,
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['datasets', 'publish', 'publish.lib', 'publish.tools'],
    include_package_data=True,
    dependency_links=[
        "http://github.com/davidmiller/ffs/tarball/master#egg=ffs-0.0.8",
        "http://github.com/nhsengland/dc/tarball/master#egg=dc-0.0.1",
        "http://github.com/rossjones/dmswitch/tarball/master#egg=dmswitch-0.0.1"
    ],
    install_requires = [
        "awesome-slugify==1.6.1",
        "beautifulsoup4==4.3.2",
        "ckanapi==3.3",
        "cssselect==0.9.1",
        "html2text==2014.12.29",
        "lxml==3.4.1",
        "requests==2.5.1",
        "urlhelp==0.0.1",
        "dc==0.0.1",
        "ffs==0.0.8",
        "dmswitch==0.0.1",
        "requests-cache==0.4.9",
        "html2text==2014.12.29",
        "boto==2.36.0"
    ],
    entry_points = {
        'console_scripts': [
            'crontool=publish.tools.crontool:main',
            'run_scraper=publish.tools.run_scraper:main',
            'fix_urls=publish.tools.url_fixer:main'
        ],
        'scrapers': [
            'ascof=datasets.ascof:entrypoints',
            'ccgois=datasets.ccgois:entrypoints',
            'hqip=datasets.hqip:entrypoints',
            'hscic=datasets.hscic:entrypoints',
            'nhsof=datasets.nhsof:entrypoints',
            'ods=datasets.ods:entrypoints',
            'phof=datasets.phof:entrypoints',
            'qof=datasets.qof:entrypoints',
            'nhse_stats=datasets.nhse_stats:entrypoints',
            'patient_survey=datasets.patient_survey:entrypoints',
            'staff_survey=datasets.staff_survey:entrypoints',
        ]
    }
)