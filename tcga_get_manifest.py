#!/usr/bin/env python
import sys
import requests, json
from argparse import ArgumentParser, FileType

# Python Examples found at https://docs.gdc.cancer.gov/API/Users_Guide/Python_Examples/
# Field Names found at https://docs.gdc.cancer.gov/API/Users_Guide/Appendix_A_Available_Fields/
# Sample Type Codes found at https://gdc.cancer.gov/resources-tcga-users/tcga-code-tables/sample-type-codes
#    e.g. 0X for tumor and 1X for normal

def download_manifest(verbose):
    files_endpt = "https://api.gdc.cancer.gov/files"

    # The 'fields' parameter is passed as a comma-separated string of single names.
    fields = [
        "cases.project.project_id",
        "cases.case_id",
        "cases.disease_type",
        "cases.samples.sample_type_id",
        "submitter_id",
        "file_name",
        "cases.samples.sample_type",
        "cases.demographic.ethnicity",
        "cases.demographic.gender",
        "cases.demographic.race",
        "cases.demographic.state",
        "cases.demographic.year_of_birth",
        "cases.demographic.year_of_death",
        "cases.diagnoses.age_at_diagnosis"
        ]

    fields = ','.join(fields)

    # This set of filters is nested under an 'and' operator.
    filters = {
        "op": "and",
        "content":[
            {
                "op": "in",
                "content":{
                    "field": "files.experimental_strategy",
                    "value": ["RNA-Seq"]
                }
            },
            {
                "op": "in",
                "content":{
                    "field": "files.analysis.workflow_type",
                    "value": ["HTSeq - FPKM-UQ"]
                }
            }
        ]
    }

    num_downloads, bulk_size = 0, 1000
    params = {
        "filters" : json.dumps(filters),
        "fields"  : fields,
        "format"  : "TSV",
        "from"    : num_downloads,
        "size"    : bulk_size
        }


    while True:
        lines = requests.get(files_endpt, params = params).content.strip().split('\n')
        if len(lines) <= 1:
            break

        # Output header once
        if num_downloads == 0:
            line = lines[0]
            fields = line.split()
            fields2 = []
            for field in fields:
                fields2.append(field.split('.')[-1])
            print '\t'.join(fields2)
            
        lines = lines[1:]
        for line in lines:
            print line

        num_downloads = num_downloads + len(lines)
        params["from"] = num_downloads
        if len(lines) < bulk_size:
            break

    print >> sys.stderr, "Number of files: %d" % num_downloads

    
if __name__ == '__main__':
    parser = ArgumentParser(
        description='Download TCGA (GDC) manifest.')
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        help='also print some statistics to stderr')

    args = parser.parse_args()
    download_manifest(args.verbose)
    
