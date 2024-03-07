from tempfile import (
    _get_candidate_names,
    _get_default_tempdir
)
from os import (
    path as os_path,
    remove as os_remove
)
def tmp_filepath(suffix=''):
    return os_path.join(
        _get_default_tempdir(),
        next(_get_candidate_names())
        ) + suffix

def clean_file(fn):
    if os_path.exists(fn):
        # f.close()
        os_remove(fn)


