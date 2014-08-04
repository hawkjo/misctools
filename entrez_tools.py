import sys
from Bio import Entrez
from my_pprint import pprint

Entrez.email = 'hawkjo@gmail.com'

def list_dbs():
    handle = Entrez.einfo()
    record = Entrez.read(handle)

    for k,v in record.items():
        print k,':'
        print
        pprint( sorted(v) )

def get_list_of_dbs():
    handle = Entrez.einfo()
    record = Entrez.read(handle)
    return record.values()[0]

def list_searchable_fields(db):
    record = Entrez.read( Entrez.einfo(db='protein') )

    for field in record['DbInfo']['FieldList']:
        print '%(Name)s, %(FullName)s, %(Description)s' % field

def download_all_hits( db, search_term, outfname, batch_size = 20, outfmt = 'fasta' ):
    search_results = Entrez.read( Entrez.esearch(db=db, term=search_term, usehistory='y') )
    
    count = int( search_results['Count'] )
    webenv = search_results['WebEnv']
    query_key = search_results['QueryKey']
    
    with open(outfname, 'w') as out:
        for start in range(0,count,batch_size):
            end = min(count, start+batch_size)
            print('Downloading %s record %i to %i of %i' % (outfname, start+1, end, count))
            fetch_handle = Entrez.efetch(db=db, rettype=outfmt, retmode='text',
                                            retstart=start, retmax=batch_size,
                                            webenv=webenv, query_key=query_key)
            data = fetch_handle.read()
            fetch_handle.close()
            out.write(data)
    return count
