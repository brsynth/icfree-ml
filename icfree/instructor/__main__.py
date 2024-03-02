from brs_utils import (
    create_logger
)

from .args import build_args_parser
from .instructor import generate_final_instructions


def main():
    parser = build_args_parser(
        program='instructor',
        description='Generates instructions for robots'
    )

    args = parser.parse_args()

    logger = create_logger(parser.prog, args.log)

    generate_final_instructions(
        source_plate_paths=args.source_plates,
        destination_plate_paths=args.destination_plates,
        base_output_instructions_path=args.base_output,
        split_upper_vol=args.split_upper_vol,
        split_lower_vol=args.split_lower_vol,
        split_outfile_components=args.split_outfile_components,
        src_plate_type_option=args.src_plate_type,
        logger=logger
    )


if __name__ == "__main__":
    main()
