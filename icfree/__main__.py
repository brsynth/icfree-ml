'''
iCFree: A package for cell-free protein synthesis

iCFree is a package for cell-free protein synthesis (CFPS) that allows to
design and optimize CFPS reactions. It is composed of the following modules:
- sampler: sample values with DoE methods
- converter: convert concentrations into volumes (optional)
- plates_generator: generates source and destination plates
- instructor: generate instructions for robotic pipetting
'''
from glob import glob
from os import path as os_path
from argparse import (
    ArgumentParser,
    Namespace
)
from logging import Logger
from typing import List
from colored import fg, attr

from .args import build_args_parser


def init(
    parser: ArgumentParser,
    args: Namespace
) -> Logger:
    '''
    Initialize the logger and print the program name and version

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser
    args: Namespace
        Namespace

    Returns
    -------
    logger: Logger
        Logger, default is getLogger(__name__)
    '''
    from brs_utils import create_logger
    from ._version import __version__

    if args.log.lower() in ['silent', 'quiet'] or args.silent:
        args.log = 'CRITICAL'

    # Create logger
    logger = create_logger(parser.prog, args.log)

    logger.info(
        '{color}{typo}{prog} {version}{rst}{color}{rst}\n'.format(
            prog=logger.name,
            version=__version__,
            color=fg('white'),
            typo=attr('bold'),
            rst=attr('reset')
        )
    )
    logger.debug(args)

    return logger


def get_modules(path: str) -> List[str]:
    '''
    Get modules from path

    Parameters
    ----------
    path: str
        Path

    Returns
    -------
    modules: List[str]
        Modules
    '''
    paths = [
        os_path.abspath(
            os_path.join(f + os_path.pardir)
        ) for f
        in glob(
            os_path.join(
                path,
                '*',
                '__init__.py'
            )
        )
    ]
    return [
        os_path.basename(
            os_path.dirname(f)
        ) for f in paths
    ]


def entry_point():
    '''
    Entry point for iCFree
    '''

    prog = 'iCFree'

    modules = get_modules(
        os_path.dirname(os_path.abspath(__file__))
        )

    description = (
        f'\nWelcome to {prog}!\n'
        f'\n\'{prog}\' is a package that cannot be directly run. '
        'Runnable modules are:\n'
    )
    for module in modules:
        description += '   - '+module+'\n'
    description += (
        '\nTo find help for a specific module, please type:\n'
        f'   python -m {prog.lower()}.<module> --help\n\n'
    )

    parser = build_args_parser(
        prog=prog,
        description=description
    )
    args = parser.parse_args()

    print(description)

    init(parser, args)


def _cli():

    return entry_point()


if __name__ == '__main__':
    _cli()
