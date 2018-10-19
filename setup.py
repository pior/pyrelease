from setuptools import setup, find_packages


description = """
See `github repo <https://github.com/pior/pyreleaser>`_ for information.
"""

VERSION = '0.5.2'  # maintained by release tool


setup(
    name='pyreleaser',
    version=VERSION,
    description='Standard release flow for Python packages',
    long_description=description,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='release packaging twine setuptools',
    author="Pior Bastida",
    author_email="pior@pbastida.net",
    url="https://github.com/pior/pyreleaser",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['click', 'twine'],
    entry_points={
        'console_scripts': ['pyreleaser = pyreleaser.cli:main'],
    },
)
