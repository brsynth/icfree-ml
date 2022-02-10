import sys

from .echo_instructor import (
    input_importer,
    volumes_array_generator,
    save_volumes_array,
    volumes_dispatcher,
    source_to_destination,
    save_echo_instructions
)

from .args import build_args_parser


def main():
    parser = build_args_parser(
        program='robots_handler',
        description='Convert concetrations tsv files into volumes tsv files')

    args = parser.parse_args()
    input_file = args.input
    input_file_1 = args.input1
    input_file_2 = args.input2
    input_file_3 = args.input3

    input_df = input_importer(
        input_file,
        input_file_1,
        input_file_2,
        input_file_3)[0]

    input_df_1 = input_importer(
        input_file,
        input_file_1,
        input_file_2,
        input_file_3)[1]

    input_df_2 = input_importer(
        input_file,
        input_file_1,
        input_file_2,
        input_file_3)[2]

    input_df_3 = input_importer(
        input_file,
        input_file_1,
        input_file_2,
        input_file_3)[3]

    sample_volume = 10.5

    intial_set_volumes = volumes_array_generator(
        input_df,
        input_df_1,
        input_df_2,
        input_df_3,
        sample_volume)[0]

    normalizer_set_volumes = volumes_array_generator(
        input_df,
        input_df_1,
        input_df_2,
        input_df_3,
        sample_volume)[1]

    autofluorescence_set_volumes = volumes_array_generator(
        input_df,
        input_df_1,
        input_df_2,
        input_df_3,
        sample_volume)[2]

    save_volumes_array(
        input_df,
        intial_set_volumes,
        normalizer_set_volumes,
        autofluorescence_set_volumes)


if __name__ == "__main__":
    sys.exit(main())
