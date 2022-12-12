from glob import glob
from os import path as os_path
from argparse import (
    ArgumentParser,
    Namespace
)
from logging import Logger
from typing import List
from .args import build_args_parser
from colored import fg, attr


def init(
    parser: ArgumentParser,
    args: Namespace
) -> Logger:
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
