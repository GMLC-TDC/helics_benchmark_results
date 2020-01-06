#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 03 13:47:29 2020

Given the results of a cross-comparison run (where graph images have already been
created), generate a PDF report headed by all appropriate metadata and including all images.

@author: hard312
"""

import argparse
import logging
import pprint
import os
import standard_analysis_pdf as saPDF
from fpdf import FPDF

# Installation of FPDF is: python -m pip install fpdf


# Setting up logging
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)


def create_cross_run_id_report(json_results, run_id_list, output_path, parameter_list):
    run_id_keys = get_run_id_keys(json_results, run_id_list)

    # Create the PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=8)
    run_id_str = '-'.join(run_id_list)
    report_name = run_id_str + '_cross_run_id_analysis.pdf'
    report_path = os.path.join(output_path, report_name)

    # Create the header metadata from the metadata in the JSON results and write out to PDF
    line_height = 3

    # TDH (2020-01-06): Create report title
    pdf.set_font("Courier", style='', size=20)
    title = 'Cross-run-ID Comparison Report\n\n'
    pdf.write(line_height, title)

    pdf.set_font("Courier", style='', size=10)
    title = '(differences in bold)\n\n\n'
    pdf.write(line_height, title)

    for param in parameter_list:
        param_title = '{}:\n'.format(param.upper())
        pdf.set_font("Courier", style='', size=10)
        pdf.write(line_height, param_title)
        header_metadata_str, diff = grab_header_metadata(json_results, run_id_keys, param)
        # TDH (2020-01-06): Parameters that are different get written out in bold
        if diff:
            pdf.set_font("Courier", style = 'B', size=10)
            pdf.write(line_height, header_metadata_str)
        else:
            pdf.set_font("Courier", style='', size=8)
            pdf.write(line_height, header_metadata_str)


    # Add graphs
    pdf = saPDF.add_benchmark_graphs(pdf, output_path)

    # Output final PDF
    pdf.output(report_path)

    #print(header_metadata_str)

def get_run_id_keys(json_results, run_id_list):
    run_id_keys = {}
    for run_id in run_id_list:
        for key in json_results:
            if run_id in key:
                if run_id not in run_id_keys:
                    run_id_keys[run_id] = key
                    break
    return run_id_keys


def grab_header_metadata(json_results, run_id_keys, param):
    param_value_list = []
    header_metadata_str = ''
    for key, value in run_id_keys.items():
        if param in json_results[value]:
            header_metadata_str = header_metadata_str + '{}: {}\n'.format(key, json_results[value][param])
            param_value_list.append(json_results[value][param])
        else:
            header_metadata_str = header_metadata_str + '{}: (value not found)\n'.format(key)
            logging.warning('{} not found in metadata for {}.'.format(param, value))
    header_metadata_str = header_metadata_str + '\n'

    # TDH (2020-01-06): Skipping date since that will always (?) be different and doesn't need to be highlighted.
    if param != 'date':
        for value in param_value_list:
            if value == param_value_list[0]:
                diff = False
            else:
                diff = True
                break
    else:
        diff = False
    return header_metadata_str, diff


def get_unique_run_ids(json_results):
    run_id_list = []
    for key in json_results:
        if json_results[key]['run_id'] not in run_id_list:
            run_id_list.append(json_results[key]['run_id'])
    return run_id_list

def _auto_run(args):
    import benchmark_postprocessing as bmpp
    file_list = bmpp.get_benchmark_files(args.benchmark_results_dir)
    json_results = bmpp.parse_files(file_list)
    json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    run_id_list = get_unique_run_ids(json_results)
    for run_id in run_id_list:
        output_path = os.path.join(args.benchmark_results_dir, '{}_report'.format(run_id))
        try:
            os.mkdir(output_path)
        except OSError:
            logging.error('Failed to create directory for report at {}'.format(output_path))
        create_standard_analysis_report(output_path, json_results, run_id)



if __name__ == '__main__':
    fileHandle = logging.FileHandler("standard_analysis_PDF.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])
    parser = argparse.ArgumentParser(description='Generate PDF report.')
    parser.add_argument('benchmark_results_dir', nargs='?',
                        default='../benchmark_results/2019-11-27')
    args = parser.parse_args()
    _auto_run(args)