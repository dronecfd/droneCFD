__author__ = 'cpaulson'
from setuptools import setup, find_packages # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
from os import path, walk

here = path.abspath(path.dirname(__file__))
# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()
datadir = 'data'
package_data = [ (d, [path.join(d, f) for f in files]) for d,folders,files in walk(datadir)]
setup(
name='droneCFD',
version='0.1.0',
description='A virtual wind tunnel based on OpenFOAM and PyFOAM',
long_description=long_description,
url='http://www.dronecfd.com',
# Author details
author='Chris Paulson',
author_email='dronecfd@gmail.com',
license='GNU',
classifiers=[
'Development Status :: 3 - Alpha',
'Intended Audience :: Developers',
'Intended Audience :: Science/Research',
'Intended Audience :: Education',
'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
'Programming Language :: Python :: 2',
'Programming Language :: Python :: 2.6',
'Programming Language :: Python :: 2.7',
],
keywords='cfd wind tunnel uav uas suas',
install_requires=['XlsxWriter', 'numpy'],
packages=['droneCFD'],
zip_safe = False,
package_dir={'droneCFD': 'droneCFD'},
data_files=package_data,
scripts=['droneCFD/scripts/dcCheck', 'droneCFD/scripts/dcRun', 'droneCFD/scripts/dcPostProcess']
# To provide executable scripts, use entry points in preference to the
# "scripts" keyword. Entry points provide cross-platform support and allow
# pip to create the appropriate form of executable for the target platform.
# entry_points={
# 'console_scripts': [
# 'sample=sample:main',
# ],
# },
)