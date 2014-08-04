import sys, os

def get_open_fnc( *args ):
    """
    get_open_fnc returns the correct open function to use for file, gzip compatible.
    Arguments:
        Any number of file names, all of which are either gzipped or not.
    Returns:
        The open function to use: either 'open' or 'gzip.open'
    """
    fname_extensions = set([os.splitext( fname ) for fname in args])
    if '.gz' not in fname_extensions:
        return open
    elif fname_extensions == set(['.gz']):
        import gzip
        return gzip.open
    else:
        sys.exit('Error: All files must be of the same format and either fastq or gzipped fastq files.')
