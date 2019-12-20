#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 10:21:03 2019

Given the results of a single run as a JSON string and the path to those results (where graph images have already been
created, generate a PDF report headed by all appropriate metadata and including all images.

@author: hard312
"""

import argparse
import logging
import pprint
import os
from fpdf import FPDF

# Installation of FPDF is: python -m pip install fpdf


# Setting up logging
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)


def create_standard_analysis_report(benchmark_results_dir, json_results):
    # Create the PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=8)
    # Getting the run ID for results file name
    key_list = list(json_results.keys())
    run_id = json_results[key_list[0]]['run_id']
    report_name = run_id + ' standard analysis.pdf'
    output_path = os.path.join(benchmark_results_dir, 'report', report_name)

    # Create the header metadata from the metadata in the JSON results and write out to PDF
    header_metadata_str = grab_header_metadata(json_results)
    pdf.write(3, header_metadata_str)

    # Add graphs
    pdf = add_benchmark_graphs(pdf, benchmark_results_dir)



    # Output final PDF
    pdf.output(output_path)



    #print(header_metadata_str)


def grab_header_metadata(json_results):
    # TDH (2019-12-20): Since all the metadata is common for each run, I can grab the metadata I need from any
    #   of the results files in this dictionary
    key_list = list(json_results.keys())
    key = key_list[0]
    header_metadata_str = ''
    if 'benchmark' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n\n'.format('BENCHMARK:', json_results[key]['benchmark'])
    else:
        logging.warning('"benchmark" not found in metadata.')

    if 'run_id' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('run ID:', json_results[key]['run_id'])
    else:
        logging.warning('"run_id" not found in metadata.')

    if 'date' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('Timestamp:', json_results[key]['date'])
    else:
        logging.warning('"run_id" not found in metadata.')

    if 'helics_version' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('HELICS version:', json_results[key]['helics_version'])
    else:
        logging.warning('"helics_version" not found in metadata.')

    if 'generator' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('generator:', json_results[key]['generator'])
    else:
        logging.warning('"generator" not found in metadata.')

    if 'system' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('system:', json_results[key]['system'])
    else:
        logging.warning('"system" not found in metadata.')

    if 'system_version' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('system version:', json_results[key]['system_version'])
    else:
        logging.warning('"system_version" not found in metadata.')

    if 'platform' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('platform:', json_results[key]['platform'])
    else:
        logging.warning('"platform" not found in metadata.')

    if 'cxx_compiler' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('C++ compiler:', json_results[key]['cxx_compiler'])
    else:
        logging.warning('"cxx_compiler" not found in metadata.')

    if 'cxx_compiler_version' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('C++ compiler version:', json_results[key]['cxx_compiler_version'])
    else:
        logging.warning('"cxx_compiler_version" not found in metadata.')

    if 'build_flags_string' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('compiler string:', json_results[key]['build_flags_string'])
    else:
        logging.warning('"build_flags_string" not found in metadata.')

    if 'host_name' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('host name:', json_results[key]['host_name'])
    else:
        logging.warning('"host_name" not found in metadata.')

    if 'host_processor' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('host processor:', json_results[key]['host_processor'])
    else:
        logging.warning('"host_processor" not found in metadata.')

    if 'num_cpus' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('CPU core count:', json_results[key]['num_cpus'])
    else:
        logging.warning('"num_cpus" not found in metadata.')

    if 'mhz_per_cpu' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('base processor speed:', json_results[key]['mhz_per_cpu'])
    else:
        logging.warning('"mhz_per_cpu" not found in metadata.')

    header_metadata_str = header_metadata_str + '\n' + '\n'
    logging.info('Final metadata header:\n{}'.format(header_metadata_str))
    return header_metadata_str

def add_benchmark_graphs(pdf, benchmark_results_dir):
    graph_path = os.path.join(benchmark_results_dir, 'report')
    for root, dirs, files in os.walk(graph_path):
        for file in files:
            name, extension = os.path.splitext(file)
            if extension == '.png':
                graph_file_path = os.path.join(benchmark_results_dir, 'report', file)
                # Scaling image; shouldn't need this for the actual graphs as we can specify the size on output
                size = 15
                width = size * 10
                height = size * 8
                pdf.image(graph_file_path, w=width, h=height)
                logging.info('Added graph file {} to PDF'.format(graph_file_path))
    return pdf

def _auto_run(args):
    import benchmark_postprocessing as bmpp
    file_list = bmpp.get_benchmark_files(args.benchmark_results_dir)
    json_results = bmpp.parse_files(file_list)
    json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    create_standard_analysis_report(args.benchmark_results_dir, json_results)



if __name__ == '__main__':
    logging.basicConfig(filename="standard_analysis_PDF.log", filemode='w',
                        level=logging.INFO)
    parser = argparse.ArgumentParser(description='Generate PDF report.')
    parser.add_argument('benchmark_results_dir', nargs='?',
                        default='../benchmark_results/2019-12-05')
    args = parser.parse_args()
    _auto_run(args)