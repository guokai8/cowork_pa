#!/usr/bin/env python
import os, sys, subprocess
from argparse import ArgumentParser, FileType

def generate_expressions(manifest_file,
                         input_dir,
                         output_dir,
                         num_genes,
                         verbose):
    if output_dir != "" and not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    head = manifest_file.readline().strip()
    fields = head.split('\t')
    field2num = {}
    for f in range(len(fields)):
        field = fields[f]
        if field in ["id", "case_id", "file_name", "sample_type_id", "disease_type"]:
            field2num[field] = f

    disease_dic = {}            
    for line in manifest_file:
        line = line.rstrip()
        fields = line.split('\t')
        id = fields[field2num["id"]]
        case_id = fields[field2num["case_id"]]
        fname = fields[field2num["file_name"]]
        sample_type_id = fields[field2num["sample_type_id"]]
        sample_type_id = str(int(sample_type_id))
        disease_type = fields[field2num["disease_type"]]
        if disease_type not in disease_dic:
            disease_dic[disease_type] = {}
        case_dic = disease_dic[disease_type]
        if case_id not in case_dic:
            case_dic[case_id] = [[id, fname, sample_type_id]]
        else:
            case_dic[case_id].append([id, fname, sample_type_id])

    for disease, case_dic in disease_dic.items():
        disease_ = disease.replace(' ', '_')
        expr_fname = "%s.expr" % disease_ if num_genes == sys.maxint else "%s_%d.expr" % (disease_, num_genes)
        if output_dir != "":
            expr_fname = "%s/%s" % (output_dir, expr_fname)
            
        expr_file = open(expr_fname, 'w')
        first_record = True
        gene_ids = []
        num_files = 0
        for case_id, values in case_dic.items():
            for id, fname, sample_type_id in values:
                tmp_gene_ids = []
                fields = [fname, case_id, sample_type_id]
                exprs = []
                fname = "%s/%s" % (input_dir, fname)
                if not os.path.exists(fname):
                    continue
                
                cmd = ["gzip", "-cd", fname]
                proc = subprocess.Popen(cmd,
                                        stdout=subprocess.PIPE,
                                        stderr=open("/dev/null", 'w'))
                for line in proc.stdout:
                    line = line.strip()
                    gene_id, expr = line.split()
                    if first_record:
                        gene_ids.append(gene_id)
                    tmp_gene_ids.append(gene_id)
                    exprs.append(float(expr))

                # Sanity checking
                assert gene_ids == tmp_gene_ids
                expr_sum = sum(exprs)
                exprs = [expr / expr_sum for expr in exprs]                        
                if first_record:
                    print >> expr_file, "file\tcase\tsampletype\t" + '\t'.join(gene_ids[:num_genes])
                    first_record = False
                print >> expr_file, '\t'.join(fields),
                for expr in exprs[:num_genes]:
                    print >> expr_file, "\t%e" % expr,
                print >> expr_file
                num_files += 1
            
        print >> sys.stderr, "%s: %d samples, %d cases, %d genes" % (disease, num_files, len(case_dic), len(gene_ids))
        expr_file.close()                        

            
    
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
    parser.add_argument('-o', '--output_dir',
                        type=str,
                        default='',
                        help='output directory name (default: empty)')
    parser.add_argument('-n', '--num-genes',
                        dest='num_genes',
                        type=int,
                        default=sys.maxint,
                        help='Number of Genes')
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
                         args.output_dir,
                         args.num_genes,
                         args.verbose)
    
