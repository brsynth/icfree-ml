from os import path as os_path

from setuptools import (
    setup,
    find_packages
    )


## INFOS ##
package     = 'icfree-ml'
descr       = 'Generate plates for cell-free buffer optimization'
url         = 'https://github.com/brsynth/icfree-ml/'
authors     = 'Yorgo El Moubayed, Joan Hérisson'
corr_author = 'yorgo.el-moubayed@inrae.fr'


## LONG DESCRIPTION
with open(
    os_path.join(
        os_path.dirname(os_path.realpath(__file__)),
        'README.md'
    ),
    'r',
    encoding='utf-8'
) as f:
    long_description = f.read()


def get_version():
    filename = os_path.join(
        os_path.dirname(os_path.realpath(__file__)),
        'CHANGELOG.md'
    )
    if not os_path.exists(filename):
        open(filename, 'w').close()
    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('##'):
            from re import search
            m = search("\[(.+)\]", line)
            if m:
                return m.group(1)


setup(
    name                          = package,
    version                       = get_version(),
    author                        = authors,
    author_email                  = corr_author,
    description                   = descr,
    long_description              = long_description,
    long_description_content_type = 'text/markdown',
    url                           = url,
    packages                      = find_packages(),
    package_dir                   = {package: package},
    include_package_data          = True,
    test_suite                    = 'pytest',
    license                       = 'MIT',
    classifiers                   = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires               = '>=3.7',
)

