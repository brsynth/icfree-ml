from setuptools import (
    setup,
    find_packages
    )

# from os import path as os_path

setup(
    name='plates_generator',
    description='Generate plates for cell-free buffer optimization',
    url='https://github.com/brsynth/icfree-ml/tree/main/plates_generator',
    author='Yorgo El Moubayed',
    install_requires=[
        'os',
        'numpy',
        'pandas',
        'pyDOE2'],
    test_suite='pytest',
    license='MIT',
    packages=find_packages()
)