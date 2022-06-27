import sys

from brs_utils import (
    create_logger
)

from .active_learning import (
    dataset_generator,
    dataset_processor
    # create_single_regressor,
    # create_ensemble_regressor,
    # active_learning_array_generator,
    # select_best_predictions_from_ensemble_model,
    # save_conditions_to_test,
    # model_statistics_generator,
    # save_model_statistics
)

from .args import build_args_parser


def main():
    parser = build_args_parser(
        program='active_learning',
        description='Predict new experimental combinations to test')

    args = parser.parse_args()

    # Create Logger
    logger = create_logger(parser.prog, args.log)

    args = parser.parse_args()
    data_folder = args.data_folder
    files_number = args.files_number

    dataset = dataset_generator(
        data_folder,
        files_number,
        logger=logger)

    dataset_processor_variables = dataset_processor(dataset)
    # initial_max = dataset_processor_variables[0]
    # X_data = dataset_processor_variables[1]
    # y_data = dataset_processor_variables[2]
    # y_data_std = dataset_processor_variables[3]


if __name__ == "__main__":
    sys.exit(main())
