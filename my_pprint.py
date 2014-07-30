import sys, warnings
from terminalsize import get_terminal_size

def pprint(thing):
    if type(thing) is list:
        pprint_list(thing)
    else:
        warnings.warn( 
            'Failed output. pprint does not currently support objects of type %s' % type(thing) )

def pprint_list(input_list):
    (term_width, term_height) = get_terminal_size()
    if len( str(input_list) ) <= term_width:
        print input_list
        return

    repr_list = [repr(x) for x in input_list]
    min_chars_between = 3 # a comma and two spaces
    usable_term_width = term_width - 3 # For '[ ' and ']' at beginning and end
    min_element_width = min( len(x) for x in repr_list ) + min_chars_between
    max_element_width = max( len(x) for x in repr_list ) + min_chars_between
    if max_element_width >= usable_term_width:
        ncol = 1
        col_widths = [1]
    else:
        # Start with max possible number of columns and reduce until it fits
        ncol = min( len(repr_list), usable_term_width / min_element_width  )
        while True:
            col_widths = [ max( len(x) + min_chars_between \
                                for j, x in enumerate( repr_list ) if j % ncol == i ) \
                                for i in range(ncol) ]
            if sum( col_widths ) <= usable_term_width: break
            else: ncol -= 1

    sys.stdout.write('[ ')
    for i, x in enumerate(repr_list):
        if i != len(repr_list)-1: x += ','
        sys.stdout.write( x.ljust( col_widths[ i % ncol ] ) )
        if i == len(repr_list) - 1:
            sys.stdout.write(']\n')
        elif (i+1) % ncol == 0:
            sys.stdout.write('\n  ')
