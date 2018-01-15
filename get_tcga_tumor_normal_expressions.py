#!/usr/bin/env python
import os, sys
from argparse import ArgumentParser, FileType

def generate_expressions(manifest_file,
                         input_dir,
                         verbose):
    head = manifest_file.readline().strip()
    fields = head.split('\t')
    field2num = {}
    for f in range(len(fields)):
        field = fields[f]
        if field in ["id", "case_id", "file_name", "sample_type_id"]:
            field2num[field] = f

    case_dic = {}
            
    files = []
    for line in manifest_file:
        line = line.rstrip()
        fields = line.split('\t')
        id = fields[field2num["id"]]
        case_id = fields[field2num["case_id"]]
        file_name = fields[field2num["file_name"]]
        sample_type_id = fields[field2num["sample_type_id"]]
        files.append([id, case_id, file_name])

        if case_id not in case_dic:
            case_dic[case_id] = [[id, sample_type_id]]
        else:
            case_dic[case_id].append([id, sample_type_id])

    # DK - debugging purposes
    print "cases:", len(case_dic), "files:", len(files)
    for case_id, values in case_dic.items():
        if len(values) <= 1:
            continue
        print case_id, values
    sys.exit(1)
            
    
if __name__ == '__main__':
    parser = ArgumentParser(
        description='Generate TCGA tumor vs. normal expressions.')
    parser.add_argument('manifest_file',
                        nargs='?',
                        type=FileType('r'),
                        help='input manifest file (use "-" for stdin)')
    parser.add_argument('input_dir',
                        nargs='?',
                        type=str,
                        default='',
                        help='input directory name (e.g. input)')
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        help='also print some statistics to stderr')

    args = parser.parse_args()
    if not args.manifest_file or \
       args.input_dir == "" or \
       not os.path.exists(args.input_dir):
        parser.print_help()
        exit(1)
    generate_expressions(args.manifest_file,
                         args.input_dir,
                         args.verbose)
    
