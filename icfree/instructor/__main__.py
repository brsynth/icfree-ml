from sys import modules as sys_modules
from brs_utils import (
    create_logger
)

from .args import build_args_parser
from .instructor import (
    generate_instructions,
    split_instructions_by_components
)
from icfree._version import __version__

__signature__ = f'{sys_modules[__name__].__package__} {__version__}'


def main():
    parser = build_args_parser(
        signature=__signature__,
        description='Generates instructions for robots'
        ' to transfer liquids between plates.'
    )

    args = parser.parse_args()

    logger = create_logger(parser.prog, args.log)

    instructions_df = generate_instructions(
        source_plate_paths=args.source_plates,
        destination_plate_paths=args.destination_plates,
        split_upper_vol=args.split_upper_vol,
        split_lower_vol=args.split_lower_vol,
        src_plate_type_option=args.src_plate_type,
        logger=logger
    )

    # Check if split_outfile_components is specified
    if args.split_outfile_components:
        # Split the instructions DataFrame into multiple CSV files based on the
        # specified components
        instructions_components = split_instructions_by_components(
            instructions_df,
            args.output_file,
            args.split_outfile_components,
            logger
        )
        for file, df in instructions_components.items():
            df.to_csv(
                file,
                index=False
            )
    else:
        instructions_df.to_csv(args.output_file, index=False)


if __name__ == "__main__":
    main()
