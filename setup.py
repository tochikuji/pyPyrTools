#!/usr/bin/env python

from setuptools import setup


install_requirements = [
    'six>=1.9.0',
    'numpy>=1.9.0',
    'pillow>=4.2.0'
]

setup(
    name='pyrtools',
    version='0.0.1',
    description="tools for multi-scale image processing",
    author='Eero Simoncelli, Rob Young, Aiga SUZUKI',
    author_email='ai-suzuki@aist.go.jp',
    license='MIT License',
    packages=['pyrtools'],
    setup_requires=[],
    install_requires=install_requirements,
)
