from setuptools import find_packages
from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print(
        "warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name="torrentutils",
    version="0.6.0",
    description="Tools to manipulate torrents",
    long_description=read_md('README.md'),
    author="Walid Saad",
    author_email="walid.sa3d@gmail.com",
    url="https://github.com/walidsa3d/torrentutils",
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    include_package_data=True,
    test_suite="nose.collector",
    license="mit",
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ]

)
