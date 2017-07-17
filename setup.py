try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'My Project',
    'author': 'Axel Müller',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'amuller@coh.org',
    'version': '0.1',
    'install_requires': ['pytest', 'pronto'],
    'packages': ['geominer'],
    'scripts': ['bin/*'],
    'name': 'projectname'
}

setup(**config)
