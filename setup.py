#!/usr/bin/env python

import setuptools

setuptools.setup(
    name="cogmindgraph",
    version="1.0",
    description="A tool for generating player progression graphs for Cogmind",
    author="Lauri Niskanen",
    author_email="ape@ape3000.com",
    url="https://github.com/Ape/cogmindgraph",
    packages=["cogmindgraph"],
    entry_points={
        "console_scripts": ["cogmindgraph=cogmindgraph.__main__:main"]
    },
    install_requires=[
        "numpy",
        "matplotlib",
    ],
    extras_require={
        "html": "yattag",
        "png": "resvg",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)
