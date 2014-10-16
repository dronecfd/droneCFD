__author__ = 'cpaulson'
from setuptools import setup, find_packages # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
from os import path, walk

here = path.abspath(path.dirname(__file__))
datadir = 'droneCFD/data'
package_data = [ (d, [path.join(d, f) for f in files]) for d,folders,files in walk(datadir)]
print package_data
data_files=[]
for i in package_data:
    for j in i[1]:
        data_files.append(j)
data_files = [path.relpath(file, datadir) for file in data_files]
# print files
setup(
name='droneCFD',
version='0.1.2',
description='A virtual wind tunnel based on OpenFOAM and PyFOAM',
long_description='Please see dronecfd.com for more information',
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
packages=find_packages(),
zip_safe = False,
package_data={"droneCFD.data":data_files,},
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