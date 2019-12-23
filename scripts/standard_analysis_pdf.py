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


def create_standard_analysis_report(output_path, json_results, run_id):
    # Create the PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=8)
    report_name = run_id + ' standard analysis.pdf'
    report_path = os.path.join(output_path, report_name)

    # Create the header metadata from the metadata in the JSON results and write out to PDF
    header_metadata_str = grab_header_metadata(json_results, run_id)
    pdf.write(3, header_metadata_str)

    # Add graphs
    pdf = add_benchmark_graphs(pdf, output_path)

    # Output final PDF
    pdf.output(report_path)

    #print(header_metadata_str)


def grab_header_metadata(json_results, run_id):
    # TDH (2019-12-20): Since all the metadata is common for each run, I can grab the metadata I need from any
    #   of the results files corresponding to the indicated run.
    key_list = list(json_results.keys())
    for key in key_list:
        if json_results[key]['run_id'] == run_id:
            break
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
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format('processor speed (MHz):', json_results[key]['mhz_per_cpu'])
    else:
        logging.warning('"mhz_per_cpu" not found in metadata.')

    header_metadata_str = header_metadata_str + '\n' + '\n'
    logging.info('Final metadata header:\n{}'.format(header_metadata_str))
    return header_metadata_str

def add_benchmark_graphs(pdf, output_path):
    for root, dirs, files in os.walk(output_path):
        for file in files:
            name, extension = os.path.splitext(file)
            if extension == '.png':
                graph_file_path = os.path.join(output_path, file)
                # Scaling image; shouldn't need this for the actual graphs as we can specify the size on output
                # width = 0
                # pdf.image(graph_file_path, w=width,)
                pdf.image(graph_file_path)
                logging.info('Added graph file {} to PDF'.format(output_path))
    return pdf

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
            print ('Failed to create directory for report at {}'.format(output_path))
        create_standard_analysis_report(output_path, json_results, run_id)



if __name__ == '__main__':
    logging.basicConfig(filename="standard_analysis_PDF.log", filemode='w',
                        level=logging.INFO)
    parser = argparse.ArgumentParser(description='Generate PDF report.')
    parser.add_argument('benchmark_results_dir', nargs='?',
                        default='../benchmark_results/2019-11-27')
    args = parser.parse_args()
    _auto_run(args)