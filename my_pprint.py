import sys, warnings
from terminalsize import get_terminal_size

def pprint(thing, stream=None, indent=2, width=None, depth=0):
    if stream is None: stream = sys.stdout
    indent = int(indent)
    if width is None:
        (width, _) = get_terminal_size()
    else:
        width = int(width)

    if _needs_pprint(thing):
        stream.write(  _format(thing, indent, width, depth) + '\n' )
    else:
        stream.write( repr(thing) + '\n' )

def _format(thing, indent, width, depth):
    if _isiterable(thing):
        return _format_iterable(thing, indent, width, depth)
    elif isinstance(thing, dict):
        return _format_dict(thing, indent, width, depth)
    else:
        return ' ' * (indent * depth) + repr(thing)

def _isiterable(thing): return hasattr(thing, '__iter__')

def _needs_pprint(thing):
    if _isiterable(thing) or isinstance(thing, dict): 
        return True
    return False

def _needs_recursion(thing):
    if _isiterable(thing): 
        for x in thing:
            if _needs_pprint(x): return True
        return False
    elif isinstance(thing, dict):
        for x in thing.values():
            if _needs_pprint(x): return True
        return False
    else:
        return False

def _format_iterable(itble, indent, width, depth):
    outstr = ''
    indentstr = ' ' * (indent * depth)
    usable_width = width - indent * depth

    if isinstance(itble, tuple):
        bracket = {'open':'(', 'close':')'}
    elif isinstance(itble, set):
        bracket = {'open':'{', 'close':'}'}
    else:
        bracket = {'open':'[', 'close':']'}

    itble_needs_recursion = _needs_recursion(itble) # cache for speed
    if len( str(itble) ) <= usable_width:
        return indentstr + str(itble)

    elif usable_width < 15 or itble_needs_recursion:
        outstr += indentstr + bracket['open'] + ' '*(indent-1)
        tmpstr = ''
        if usable_width < 15:
            for x in itble:
                tmpstr += indentstr + str(x) + ',\n'
        else: # itble_needs_recursion:
            for x in itble:
                tmpstr += _format(x, indent, width, depth + 1) + ',\n'
        # Remove indent spacing from the first line of the first element and
        # remove last comma and newline and close list
        spaces_to_remove = indent * (depth+1)
        outstr += tmpstr[spaces_to_remove:-2] + ' ' + bracket['close'] 
        return outstr

    else:
        repr_list = [repr(x) for x in itble]
    
        usable_width -= (indent + 2*depth) # For '[ ' and ']' at beginning and end
        min_chars_between = 3 # a comma and two spaces
        min_element_width = min( len(x) for x in repr_list ) + min_chars_between
        max_element_width = max( len(x) for x in repr_list ) + min_chars_between
        if max_element_width >= usable_width:
            ncol = 1
            col_widths = [1]
        else:
            # Start with max possible number of columns and reduce until it fits
            ncol = min( len(repr_list), usable_width / min_element_width  )
            while True:
                col_widths = [ max( len(x) + min_chars_between \
                                    for j, x in enumerate( repr_list ) if j % ncol == i ) \
                                    for i in range(ncol) ]
                if sum( col_widths ) <= usable_width: break
                else: ncol -= 1
    
        outstr += indentstr + bracket['open'] + ' '*(indent-1)

        for i, x in enumerate(repr_list):
            if i + 1 != len(repr_list): x += ','
            outstr += x.ljust( col_widths[ i % ncol ] ) 
            if i + 1 == len(repr_list):
                outstr += bracket['close'] 
            elif (i+1) % ncol == 0:
                outstr += '\n' + indentstr + ' '*indent
        return outstr

if __name__ == '__main__':
    a = [ [1,2,3], 4, set([5,6,7]), ((9,10),11), (12,), [], 
            set((range(20,150))),
            [1,range(50,80),2],3 ]
    print a
    pprint(a, indent = 2)
