# Tests for utils.py
from unittest import TestCase

from shutil import rmtree as rmtree
from pandas import (
    DataFrame,
    testing as pd_testing,
    read_csv as pd_read_csv,
    read_excel as pd_read_excel
)
from tempfile import NamedTemporaryFile

from icfree.utils import save_df


class TestUtils(TestCase):

    def test_save_df(self):
        df = DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

        file_format = 'csv'
        filename = 'test.csv'
        tmp_folder = NamedTemporaryFile().name
        outfile = save_df(
            df=df,
            outfile=filename,
            output_folder=tmp_folder
        )
        with open(outfile, 'r') as f:
            pd_testing.assert_frame_equal(pd_read_csv(f), df)
        rmtree(tmp_folder)

        file_format = 'tsv'
        with NamedTemporaryFile() as f:
            outfile = save_df(
                df=df,
                outfile=f.name,
                file_format=file_format
            )
            with open(outfile, 'r') as f:
                pd_testing.assert_frame_equal(pd_read_csv(f, sep='\t'), df)

        with NamedTemporaryFile() as f:
            outfile = save_df(
                df=df,
                outfile=f.name
            )
            with open(outfile, 'r') as f:
                pd_testing.assert_frame_equal(pd_read_csv(f), df)

        file_format = 'xlsx'
        with NamedTemporaryFile() as f:
            save_df(df, f.name, file_format=file_format)
            pd_testing.assert_frame_equal(
                pd_read_excel(f'{f.name}.{file_format}', sheet_name='Sheet1'),
                df
            )
