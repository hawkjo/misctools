import sys, os, gzip

def get_gzip_friendly_open_fnc( *args ):
    """
    get_open_fnc returns the correct open function to use for file, gzip compatible.
    Arguments:
        Any number of file names, all of which are either gzipped or not.
    Returns:
        The open function to use: either 'open' or 'gzip.open'
    """
    fname_extensions = set([os.path.splitext( fname )[-1] for fname in args])
    if '.gz' not in fname_extensions:
        return open
    elif fname_extensions == set(['.gz']):
        import gzip
        return gzip.open
    else:
        sys.exit('Error: All files must be of the same format and either fastq or gzipped fastq files.')

def gzip_friendly_open( fname, mode='r' ):
    """
    gzip_friendly_open returns a file handle appropriate for the file, whether gzipped or not.
    """
    if os.path.splitext(fname)[-1] == '.gz':
        return gzip.open(fname, mode)
    else:
        return open(fname, mode)
