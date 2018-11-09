import sys
import os
import gzip
from itertools import izip_longest
from IPython.display import HTML


def get_gzip_friendly_open_fnc(*args):
    """
    get_open_fnc returns the correct open function to use for file, gzip compatible.
    Arguments:
        Any number of file names, all of which are either gzipped or not.
    Returns:
        The open function to use: either 'open' or 'gzip.open'
    """
    fname_extensions = set([os.path.splitext(fname)[-1] for fname in args])
    if '.gz' not in fname_extensions:
        return open
    elif fname_extensions == set(['.gz']):
        import gzip
        return gzip.open
    else:
        sys.exit(
            'Error: All files must be of the same format and either fastq or gzipped fastq files.')


def gzip_friendly_open(fname, mode='r'):
    """
    gzip_friendly_open returns a file handle appropriate for the file, whether gzipped or not.
    """
    if os.path.splitext(fname)[-1] == '.gz':
        return gzip.open(fname, mode)
    else:
        return open(fname, mode)


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def getToggleScript():
    return '''<script>
code_show=true; 
function code_toggle() {
 if (code_show){
  $('div.input').hide();
  } else {
  $('div.input').show();
  }
 code_show = !code_show
} 
$( document ).ready(code_toggle);
</script>
The raw code for this IPython notebook is by default hidden for easier reading.
To toggle on/off the raw code, click <a href="javascript:code_toggle()">here</a>.'''


def add_toggle_script():
    HTML(getToggleScript())


def dot():
    sys.stdout.write('.')
    sys.stdout.flush()


def walk_dict_tree_at_given_depth(d, depth, only_keys=False, prev_args=[]):
    """
    Allow for easy iteration at given depth of structured dict-of-dicts tree.
    """
    # There are two cases which must be handled: 
    #       1) The objects at depth == depth are dicts, in which case we return the keys or dicts
    #           as specified by only_keys
    #       2) The objects at depth == depth are not dicts, in which case we return the values.
    # If we wish to return dicts or non-dict values, we must catch them when depth == 2.
    if depth == 1:
        # We only arrive here if only_keys == True.
        for k in sorted(d.keys()):
            yield prev_args + [k]
        return
    elif depth == 2:
        if not only_keys or not isinstance(d.itervalues().next(), dict): # Test for non-dict leaves
            for k, v in sorted(d.items()):
                yield prev_args + [k, v]
            return
        # else continue on as ususal
    try:
        for k, v in sorted(d.items()):
            for args in walk_dict_tree_at_given_depth(v, depth-1, only_keys, prev_args + [k]):
                yield args
    except AttributeError:
        raise AttributeError('Tree has less than requested depth.')
    except:
        raise


def python_intervals_overlap(interval1, interval2):
    query_start, query_end = interval1
    subject_start, subject_end = interval2
    return (query_start <= subject_start < query_end
            or query_start < subject_end <= query_end
            or subject_start <= query_start < subject_end
            or subject_start < query_end <= subject_end)
