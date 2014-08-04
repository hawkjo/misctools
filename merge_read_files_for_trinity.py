import sys, os, re, gzip

if len(sys.argv) < 2:
    sys.exit('Usage: merge_read_files_for_trinity.py <dir with fastq files> [<output dir>]')

in_dir = sys.argv[1]
if len(sys.argv) >= 3:
    out_dir = sys.argv[2]
else:
    out_dir = '.'

fastq_fnames = [fname for fname in os.listdir(in_dir) if 'fastq' in fname]

paired_fnames = []
unpaired_fnames = []

name_re = re.compile(r'_([12])_')

for fname in fastq_fnames:
    m = name_re.search(fname)
    if m:
        if 'unpaired' in fname:
            unpaired_fnames.append(fname)
        elif m.group(1) == '1':
            fname2 = name_re.sub('_2_',fname)
            if fname2 not in fastq_fnames:
                sys.exit( 'Improper pairing of files: %s and %s' % (fname, fname2) )
            paired_fnames.append( (fname, fname2) )
        elif m.group(1) == '2':
            fname1 = name_re.sub('_1_',fname)
            if fname1 not in fastq_fnames:
                sys.exit( 'Improper pairing of files: %s and %s' % (fname, fname1) )
        else:
            sys.exit('Unexpected string match: %s' % m.group(1))
    else:
        unpaired_fnames.append( fname )

print 'Paired files:'
for tup in paired_fnames:
    print tup
print 
print 'Unpaired files:'
for fname in unpaired_fnames:
    print fname
print

outname1 = os.path.join( out_dir, 'reads_left_1.fastq' )
outname2 = os.path.join( out_dir, 'reads_right_2.fastq' )

with open(outname1,'w') as out1, open(outname2,'w') as out2:
    for fname1, fname2 in paired_fnames:
        print 'Copying',(fname1,fname2)
        fname1 = os.path.join( in_dir, fname1 )
        fname2 = os.path.join( in_dir, fname2 )

        if fname1[-8:] == fname2[-8:] == 'fastq.gz':
            open_fnc = gzip.open
        elif fname1[-3:] == fname2[-3:] == '.fq' or fname1[-6:] == fname2[-6:] == '.fastq':
            open_fnc = open
        else:
            sys.exit('Input file type error: %s and %s' % (fname1, fname2) )

        with open_fnc(fname1) as f1, open_fnc(fname2) as f2:
            while True:
                defline1 = f1.readline().strip()
                defline2 = f2.readline().strip()
                if not defline1 and not defline2:
                    break
                elif not defline1 or not defline2:
                    sys.exit('Unequal number of paired reads: %s and %s' % (fname1,fname2))

                seqline1 = f1.readline().strip()
                plusline1 = f1.readline().strip()
                qualline1 = f1.readline().strip()

                seqline2 = f2.readline().strip()
                plusline2 = f2.readline().strip()
                qualline2 = f2.readline().strip()

                out1.write( '\n'.join( [defline1,seqline1,plusline1,qualline1] ) + '\n' )
                out2.write( '\n'.join( [defline2,seqline2,plusline2,qualline2] ) + '\n' )

    for fname in unpaired_fnames:
        print 'Copying',fname
        fname = os.path.join( in_dir, fname )

        if fname[-8:] == 'fastq.gz':
            open_fnc = gzip.open
        elif fname[-3:] == '.fq' or fname[-6:] == '.fastq':
            open_fnc = open
        else:
            sys.exit('Input file type error: %s and %s' % (fname1, fname2) )

        with open_fnc(fname) as f:
            while True:
                defline = f.readline().strip()
                if not defline: break
                seqline = f.readline().strip()
                plusline = f.readline().strip()
                qualline = f.readline().strip()

                if defline[-2] == '/':
                    defline = defline[:-2]

                out1.write( '\n'.join( [defline,seqline,plusline,qualline] ) + '\n' )
