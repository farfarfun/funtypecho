import sys
from os import path

from setuptools import find_packages, setup

from notebuild.tool import get_version

version_path = path.join(path.abspath(
    path.dirname(__file__)), 'script/__version__.md')

version = get_version(sys.argv, version_path, step=16)

install_requires = ['notetool']

setup(name='notetypecho',
      version=version,
      description='notetypecho',
      author='euler',
      author_email='1007530194@qq.com',
      url='https://github.com/1007530194',

      packages=find_packages(),
      package_data={"": ["*.db"]},
      install_requires=install_requires
      )
