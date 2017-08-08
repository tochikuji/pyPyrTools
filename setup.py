#!/usr/bin/env python

from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess


class BuildSO(build_py):
    def run(self):
        command = ['make']
        if subprocess.call(command) != 0:
            raise OSError('Could not make extension. Try "make" manually.')

        build_py.run(self)


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
    package_dir={'pyrtools': 'pyrtools'},
    package_data={'pyrtools': ['*.so']},
    setup_requires=[],
    install_requires=install_requirements,
    cmdclass={'build_py': BuildSO},
)
