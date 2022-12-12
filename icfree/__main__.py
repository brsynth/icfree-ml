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

    parser = build_args_parser(
        prog='iCFree',
        description='\
            Package to process cell-free with ECHO® robot.\
            Only \'sampler\', \'converter\', \'plates_generator\' and \'instructor\' \
            modules are runnable (python -m icfree.<module>).'
    )
    args = parser.parse_args()

    modules = get_modules(
        os_path.dirname(os_path.abspath(__file__))
        )

    description = (
        f'\nWelcome to {parser.prog}!\n'
        f'\n\'{parser.prog}\' is a package that cannot be directly run. '
        'Runnable tools are:\n'
    )
    for module in modules:
        description += '   - '+module+'\n'
    description += (
        '\nTo find help for a specific tool, please type:\n'
        f'   python -m {parser.prog.lower()}.<tool_name> --help\n\n'
    )

    print(description)

    init(parser, args)


def _cli():

    return entry_point()


if __name__ == '__main__':
    _cli()
