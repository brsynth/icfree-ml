from sys import modules as sys_modules
from pandas import option_context as pd_option_context

from brs_utils import (
    create_logger
)

from icfree._version import __version__
from .args import build_args_parser
from .sampler import (
    load_data,
    get_discrete_ranges,
    sampling
)

__signature__ = f'{sys_modules[__name__].__package__} {__version__}'


def main():

    parser = build_args_parser(
        signature=__signature__,
        description='Sample values'
    )

    args = parser.parse_args()

    print(__signature__)
    print()

    # CREATE LOGGER
    logger = create_logger(parser.prog, args.log)

    # Load the data from file
    try:
        data = load_data(args.input_file, logger)
    except FileNotFoundError:
        logger.error("File not found. Exiting.")
        exit()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit()

    # Get the discrete ranges
    discrete_ranges = get_discrete_ranges(
        data=data,
        ratios=args.ratios,
        step=args.step,
        nb_bins=args.nb_bins,
        logger=logger
    )

    # Call the sampling method
    try:
        samples_df = sampling(
            discrete_ranges=discrete_ranges,
            n_samples=args.nb_samples,
            method=args.method,
            seed=args.seed,
            logger=logger
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit()
    # Rename the columns
    samples_df.columns = data.columns

    # Save the output
    if args.output_file == "":
        with pd_option_context(
            'display.max_rows', None, 'display.max_columns', None
        ):
            print(samples_df)
    else:
        samples_df.to_csv(args.output_file, index=False)
        logger.info(f"File saved to {args.output_file}")


if __name__ == "__main__":
    main()
