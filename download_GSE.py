from ftplib import FTP
from urlparse import urlparse
import tempfile
import subprocess
import os
import sys
import xml.etree.ElementTree as etree
import string

def get_xml(output_dir, accession):
    xml_tail = '{0}_family.xml'.format(accession)
    xml_fn = '{0}/{1}'.format(output_dir, xml_tail)
    tgz_fn = xml_fn + '.tgz'

    xml_url_template = 'ftp://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}nnn/{accession}/miniml/{xml_tail}.tgz'
    xml_url = xml_url_template.format(prefix=accession[:5],
                                      accession=accession,
                                      xml_tail=xml_tail,
                                     )

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    wget_command = ['wget', '--quiet', '-P', output_dir, xml_url]
    subprocess.check_call(wget_command)

    tar_command = ['tar', 'xvzf', tgz_fn, '-C', output_dir]
    subprocess.check_call(tar_command)
    os.remove(tgz_fn)

    return xml_fn

def extract_samples_from_xml(xml_fn, condition=lambda x: True):
    samples = []
    tree = etree.parse(xml_fn)
    root = tree.getroot()
    sanitize = string.maketrans(' /,', '___')
    for child in root:
        if child.tag.endswith('Sample'):
            skip_sample = False
            for grand in child:
                if grand.tag.endswith('Title'):
                    sample_name = grand.text
                    sample_URLs = []
                    if not type(sample_name) == str:
                        # Some sample names (knockout strains) have a unicode
                        # delta in them. Replace this with a spelled out
                        # 'delta' and coerce to a non-unicode string.
                        delta = u'\u0394'
                        sample_name = str(sample_name.replace(delta, 'delta_'))
                    sample_name = sample_name.translate(sanitize, '()')
                    if not condition(sample_name):
                        skip_sample = True
                        break
                elif grand.tag.endswith('Supplementary-Data') and grand.attrib['type'] == 'SRA Experiment':
                    sample_URL = grand.text.strip()
                    sample_URLs.append(sample_URL)
            if not skip_sample:
                samples.append((sample_name, sample_URLs))
    return samples

def download_samples(output_dir, samples):
    ascp_bin = '/home/jah/.aspera/connect/bin/ascp'
    ascp_key = '/home/jah/.aspera/connect/etc/asperaweb_id_dsa.openssh'

    sra_fns = []
    for sample_name, sample_URLs in samples:
        sample_dir = '{0}/{1}/data'.format(output_dir, sample_name)
        if not os.path.isdir(sample_dir):
            os.makedirs(sample_dir)
        
        for sample_URL in sample_URLs:
            parsed_sample_url = urlparse(sample_URL)
            f = FTP(parsed_sample_url.netloc)
            f.login()
            f.cwd(parsed_sample_url.path)
            ls = []
            f.dir(ls.append)
            f.quit()

            for line in ls:
                run = line.split()[-1]
                run_url = '{0}/{1}/{1}.sra'.format(sample_URL, run)
                parsed_run_url = urlparse(run_url)
                wget_command = ['wget',
                                '-P', sample_dir,
                                run_url,
                               ]
                ascp_command = [ascp_bin,
                                '-i', ascp_key,
                                '-QT',
                                '-l', '300m',
                                'anonftp@{0}:{1}'.format(parsed_run_url.netloc, parsed_run_url.path),
                                sample_dir,
                               ]
                subprocess.check_call(ascp_command)
                sra_fn = '{0}/{1}.sra'.format(sample_dir, run)
                sra_fns.append(sra_fn)

    return sra_fns

def dump_fastqs(sra_fns, paired=False):
    for sra_fn in sra_fns:
        print "fastq-dump'ing {0}".format(sra_fn) 
        head, tail = os.path.split(sra_fn)
        root, ext = os.path.splitext(sra_fn)
        if paired:
            # Split into two files and include read number (out of pair) in the
            # seq name line.
            fastq_dump_command = ['fastq-dump',
                                  '--split-3',
                                  '--defline-seq', '@$ac.$si/$ri',
                                  '--defline-qual', '+',
                                  '-O', head,
                                  sra_fn,
                                 ]
        else:
            fastq_dump_command = ['fastq-dump',
                                  '--defline-seq', '@$ac.$si',
                                  '--defline-qual', '+',
                                  '-O', head,
                                  sra_fn,
                                 ]
        subprocess.check_call(fastq_dump_command)
        os.remove(sra_fn)

experiments = {
    # Bat transcriptome data
    'zhang2013comparative': ('GSE39933', lambda name: True),        # M davidii and P Alecto
    'wu2013deep': ('GSE41275', lambda name: True),                  # M davidii
    'seim2013genome': ('GSE42297', lambda name: True),              # M brandtii
    'gracheva2011ganglion': ('GSE28243', lambda name: True),              # M brandtii
}

non_GSE_experiments = {
    'shaw2012transcriptome': [
        ('A_jamaicensis', [
            'ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByStudy/sra/SRP/SRP014/SRP014960',
            ]),
        ],
    'papenfuss2012immune': [
        ('P_alecto', [
            'ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByStudy/sra/SRP/SRP008/SRP008674',
            ]),
        ],
    'phillips2014dietary': [
        ('M_lucifigus', [
            'ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByStudy/sra/SRP/SRP031/SRP031492',
            ]),
        ],
    'dong2013comparative': [
        ('M_ricketti_and_C_sphinx', [
            'ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByStudy/sra/SRP/SRP022/SRP022034',
            ]),
        ],
    'francischetti2013vampirome': [
        ('D_rotundus', [
            'ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByStudy/sra/SRP/SRP016/SRP016760',
            ]),
        ],
    'low2013dracula': [
        ('D_rotundus', [
            'ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByStudy/sra/SRP/SRP017/SRP017201',
            ]),
        ],
}

organism_info = { 
        'ArtibeusJamaicensis': ('/home/hawkjo/SaraProjects/Chiroptera/external_bats/ArtibeusJamaicensis',
            ['shaw2012transcriptome']),
        'PteropusAlecto': ('/home/hawkjo/SaraProjects/Chiroptera/external_bats/PteropusAlecto',
            ['zhang2013comparative','papenfuss2012immune']),
        'MyotisLucifigus': ('/home/hawkjo/SaraProjects/Chiroptera/external_bats/MyotisLucifigus',
            ['phillips2014dietary']),
        'MyotisDavidii': ('/home/hawkjo/SaraProjects/Chiroptera/external_bats/MyotisDavidii',
            ['zhang2013comparative','wu2013deep']),
        'MyotisBrandtii': ('/home/hawkjo/SaraProjects/Chiroptera/external_bats/MyotisBrandtii',
            ['seim2013genome']),
        'MyotisRicketti': ('/home/hawkjo/SaraProjects/Chiroptera/external_bats/MyotisRicketti',
            ['dong2013comparative']),
        'CynopterusSphinx': ('/home/hawkjo/SaraProjects/Chiroptera/external_bats/CynopterusSphinx',
            ['dong2013comparative']),
        'DesmodusRotundus': ('/home/hawkjo/SaraProjects/Chiroptera/external_bats/DesmodusRotundus',
            ['gracheva2011ganglion','francischetti2013vampirome','low2013dracula']),
}

if __name__ == '__main__':
    if len(sys.argv) == 1:
        for bat, (output_dir, paper_names) in organism_info.items():
            for paper_name in paper_names:
    
                while len(output_dir) > 1 and output_dir[-1] == r'/':
                    # Delete trailing '/'s. They mess up the fastq-dump
                    output_dir = output_dir[:-1]
            
                if paper_name in experiments:
                    accession, condition = experiments[paper_name]
            
                    xml_fn = get_xml(output_dir, accession)
                    samples = extract_samples_from_xml(xml_fn, condition=condition)
                elif paper_name in non_GSE_experiments:
                    samples = non_GSE_experiments[paper_name]
            
                for sample in samples:
                    print sample[0]
                    for url in sample[1]:
                        print '\t', url
            
                sra_fns = download_samples(output_dir, samples)
                #dump_fastqs(sra_fns, paired=False)

    elif len(sys.argv) == 3:
        if sys.argv[1] == 'paired':
            paired=True
        elif sys.argv[1] == 'single':
            paired=False
        else:
            sys.exit('Unrecognized first argument: ' + sys.argv[1])

        ftp_address = sys.argv[2]
        while ftp_address[-1] == r'/':
            ftp_address = ftp_address[:-1]

        output_dir = '.'
        samples = [('',[ftp_address])]
        sra_fns = download_samples(output_dir, samples)
        dump_fastqs(sra_fns, paired=paired)

    else:
        sys.exit('Usage: download_GSE.py [<paired or single> <ftp address of srp head directory>]')
