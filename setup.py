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
        "http://github.com/davidmiller/dc/tarball/master#egg=dc-0.0.1"
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
        "ffs==0.0.8"
    ],
    entry_points = {
        'console_scripts': [
            'crontool=publish.tools.crontool:main'
        ],
    }
)