#!/usr/bin/env python
import sys, random
import requests
import json
from argparse import ArgumentParser, FileType

files_endpt = 'https://api.gdc.cancer.gov/files'

# The 'fields' parameter is passed as a comma-separated string of single names.
fields = [
    "file_name",
    "cases.submitter_id",
    "cases.samples.sample_type",
    "cases.disease_type",
    "cases.project.project_id"
    ]

fields = ','.join(fields)

# This set of filters is nested under an 'and' operator.
#    "field": "cases.project.primary_site", "value": ["Lung"]
#    "field": "files.data_format", "value": ["BAM"]

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


params = {
    "filters": json.dumps(filters),
    "fields": fields,
    "format": "TSV",
    "size": "100000"
    }

response = requests.get(files_endpt, params = params)

print(response.content)

xs
