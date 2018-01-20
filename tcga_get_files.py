#!/usr/bin/env python
import os, sys, re
import requests, json
from argparse import ArgumentParser, FileType

def download_files(manifest_file,
                   output_dir,
                   verbose):
    head = manifest_file.readline().strip()
    fields = head.split('\t')
    field2num = {}
    for f in range(len(fields)):
        field = fields[f]
        if field in ["id", "case_id", "file_name"]:
            field2num[field] = f

    case_dic = {}

    files = []
    for line in manifest_file:
        line = line.rstrip()
        fields = line.split('\t')
        id = fields[field2num["id"]]
        case_id = fields[field2num["case_id"]]
        file_name = fields[field2num["file_name"]]
        files.append([id, case_id, file_name])
            
    data_endpt = "https://api.gdc.cancer.gov/data"

    num_downloads = 0
    for f in range(len(files)):
        id, case_id, file_name = files[f]
        print >> sys.stderr, "Downloading %s (%d / %d)" % (id, f+1, len(files))
        params = {"ids": [id]}
        response = requests.post(data_endpt,
                                 data = json.dumps(params),
                                 headers={
                                     "Content-Type": "application/json"
                                 })
        response_head_cd = response.headers["Content-Disposition"]
        
        file_name = re.findall("filename=(.+)", response_head_cd)[0]
        if output_dir != "" and not os.path.exists(output_dir):
            os.mkdir(output_dir)
        if output_dir != "":
            file_name = "%s/%s" % (output_dir, file_name)            
        with open(file_name, "wb") as output_file:
            output_file.write(response.content)
        num_downloads += 1

    print >> sys.stderr, "Number of downloaded files: %d" % num_downloads

    
if __name__ == '__main__':
    parser = ArgumentParser(
        description='Download TCGA (GDC) files.')
    parser.add_argument('manifest_file',
                        nargs='?',
                        type=FileType('r'),
                        help='input manifest file (use "-" for stdin)')
    parser.add_argument('-o', '--output-dir',
                        dest='output_dir',
                        type=str,
                        default='output',
                        help='output directory name (e.g. output)')
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        help='also print some statistics to stderr')

    args = parser.parse_args()
    if not args.manifest_file:
        parser.print_help()
        exit(1)
    download_files(args.manifest_file,
                   args.output_dir,
                   args.verbose)
    
