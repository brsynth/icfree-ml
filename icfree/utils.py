from os import (
    path as os_path,
    mkdir as os_mkdir,
    getcwd as os_getcwd
)
from logging import (
    Logger,
    getLogger
)
from pandas import DataFrame


def save_df(
    df: DataFrame,
    outfile: str,
    file_format: str = None,
    output_folder: str = os_getcwd(),
    index: bool = False,
    logger: Logger = getLogger(__name__)
) -> str:
    """
    Save instructions in csv files

    Parameters
    ----------
        instructions_dict: Dict
            Dict with instructions dataframes

        output_folder: str
            Path to output storage folder
    """
    # Create output folder if it doesn't exist
    if not os_path.exists(output_folder):
        os_mkdir(output_folder)

    # # Create output subfolders if they don't exist
    # output_subfolder = os_path.join(output_folder, 'instructions')
    # if not os_path.exists(output_subfolder):
    #     os_mkdir(output_subfolder)

    if file_format is None:
        if '.' in outfile:
            outfile_split = outfile.split('.')
            file_format = outfile_split[-1]
            outfile = '.'.join(outfile_split[:-1])
        else:
            file_format = 'csv'

    # Save DataFrame
    outfile = f'{os_path.join(output_folder, outfile)}.{file_format}'
    if file_format == 'csv':
        df.to_csv(outfile, index=index)
    elif file_format == 'tsv':
        df.to_csv(outfile, index=index, sep='\t')
    elif file_format == 'xlsx':
        df.to_excel(outfile, index=index)
    
    return outfile
