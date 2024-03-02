from sys import modules as sys_modules

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


def main(args):

    parser = build_args_parser(
        signature=__signature__,
        description='Sample values'
    )

    args = parser.parse_args(args)

    if not args.silent:
        print(__signature__)
        print()
    else:
        args.log = 'ERROR'

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

    # Rename the columns of the samples
    # with the component names of the original data
    samples_df.columns = data['Component'].tolist()

    # Save the output
    if args.output_file == "":
        print(samples_df.to_csv(index=False))
    else:
        samples_df.to_csv(args.output_file, index=False)
        logger.info(f"File saved to {args.output_file}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
