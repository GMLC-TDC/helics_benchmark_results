# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 07:49:57 2020

Given the results and paths to the results, create an intra-run
analysis report PDF.

This script creates an intra-run analysis report for comparing
benchmarks' data for a single run.  A "run" is specified by
the 5 character unique ID in the filename for every results
file associated with that run.

The command line arguments for the function can be found in the code
following the lines following the "if __name__ == '__main__':" line
at the end of this file.

@author: barn553
"""

import argparse
import logging
import pprint
import os
import sys
import standard_analysis_pdf as saPDF
from fpdf import FPDF

# Installation of FPDF is: python -m pip install fpdf


# Setting up logging
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)


def create_intra_run_id_report(output_path, json_results, run_id):
    """This function creates a pdf for a single run_id and compares
    two benchmarks' data.

    Args:
        output_path (str) - Path where graph images are located and PDF
        report will be saved.

        json_results (dict) - Benchmark results

        run_id (str) - Five character unique identifier for a particular
        benchmark run

    Returns:
        (null)
    """
    # Create the PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=8)

    # Define the output path for the report PDF
    report_name = run_id + '_benchmark_intra_run.pdf'
    report_path = os.path.join(output_path, report_name)

    # Create the header metadata from the metadata in the JSON results
    # and write out to PDF
    header_metadata_str = grab_header_metadata(json_results, run_id)
    line_height = 3
    pdf.write(line_height, header_metadata_str)

    # Add previously generated graphs to the PDF object
    pdf = saPDF.add_benchmark_graphs(pdf, output_path)

    # Output final PDF file from PDF object
    pdf.output(report_path)


def grab_header_metadata(json_results, run_id):
    """This function creates the header metadata as a string.

    Args:
        json_results (dict) - benchmark results

        run_id (str) - five character unique identifier for a particular
        benchmark run

    Returns:
        header_metadata_str (str) - Formatted header metadata for report
    """
    # TDH (2019-12-20): Since all the metadata is common for each run, I
    # can grab the metadata I need from any of the results files
    # corresponding to the indicated run.
    key_list = list(json_results.keys())
    for key in key_list:
        if json_results[key]['run_id'] == run_id:
            break
    header_metadata_str = ''
    if 'run_id' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'run ID:', json_results[key]['run_id'])
    else:
        logging.warning('"run_id" not found in metadata.')

    if 'date' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'Timestamp:', json_results[key]['date'])
    else:
        logging.warning('"run_id" not found in metadata.')

    if 'helics_version' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'HELICS version:', json_results[key]['helics_version'])
    else:
        logging.warning('"helics_version" not found in metadata.')

    if 'generator' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'generator:', json_results[key]['generator'])
    else:
        logging.warning('"generator" not found in metadata.')

    if 'system' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'system:', json_results[key]['system'])
    else:
        logging.warning('"system" not found in metadata.')

    if 'system_version' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'system version:', json_results[key]['system_version'])
    else:
        logging.warning('"system_version" not found in metadata.')

    if 'platform' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'platform:', json_results[key]['platform'])
    else:
        logging.warning('"platform" not found in metadata.')

    if 'cxx_compiler' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'C++ compiler:', json_results[key]['cxx_compiler'])
    else:
        logging.warning('"cxx_compiler" not found in metadata.')

    if 'cxx_compiler_version' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'C++ compiler version:', json_results[key]['cxx_compiler_version'])
    else:
        logging.warning('"cxx_compiler_version" not found in metadata.')

    if 'build_flags_string' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'compiler string:', json_results[key]['build_flags_string'])
    else:
        logging.warning('"build_flags_string" not found in metadata.')

    if 'host_name' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'host name:', json_results[key]['host_name'])
    else:
        logging.warning('"host_name" not found in metadata.')

    if 'host_processor' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'host processor:', json_results[key]['host_processor'])
    else:
        logging.warning('"host_processor" not found in metadata.')

    if 'num_cpus' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'CPU core count:', json_results[key]['num_cpus'])
    else:
        logging.warning('"num_cpus" not found in metadata.')

    if 'mhz_per_cpu' in json_results[key]:
        header_metadata_str += '{:<25}{}\n'.format(
            'processor speed (MHz):', json_results[key]['mhz_per_cpu'])
    else:
        logging.warning('"mhz_per_cpu" not found in metadata.')

    header_metadata_str += '\n' + '\n'
    logging.info('Final metadata header:\n{}'.format(header_metadata_str))
    return header_metadata_str


def get_unique_run_ids(json_results):
    """This function finds the unique run IDs for the provided results
    dictionary.

    Args:
        json_results (dict) - enchmark results

    Returns:
        run_id_list (list) - List of unique run ID strings in json_results
    """
    run_id_list = []
    for key in json_results:
        if json_results[key]['run_id'] not in run_id_list:
            run_id_list.append(json_results[key]['run_id'])
    logging.info('found all the unique run-ids')
    return run_id_list


def _auto_run(args):
    """This function executes when the script is called as a stand-alone
    executable. It is used both for development/testing as well as the
    primary executable for generating the benchmark intra-run PDF report.
    To use as a stand-alone script (primarily for development purposes)
    the script has to replicate some of the functionality in
    "benchmark_intra_run.py" to generate json_results for use here.

    A more complete description of this code can be found in the
    docstring at the beginning of this file.

    Args:
        '-r' or '--benchmark_results_dir' - Path of top-level folder
        that contains the benchmark results folders/files to be
        processed.

    Returns:
        (nothing)
    """
    # CGR (2020-01-22) For developement testing the following section
    # replicates the functionality of "benchmark_intra_run.py" so that
    # json_results can be created and used to create the graph image
    # files.
    logging.info('starting the execution of this script...')
    import benchmark_postprocessing as bmpp
    file_list = bmpp.get_benchmark_files(args.benchmark_results_dir)
    json_results = bmpp.parse_files(file_list)
    json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    run_id_list = get_unique_run_ids(json_results)

    # TDH (2020-01-13) - Create unqiue reports for each run ID found.
    # Even a single results directory can contain results from multiple
    # run IDs.
    for run_id in run_id_list:
        output_path = os.path.join(
            args.benchmark_results_dir,
            '{}_intra_run_report'.format(run_id))

        # TDH: Thorough attempt to safely create the results directory and
        # provide good error reporting if something went wrong.
        try:
            os.mkdir(output_path)
        except OSError:
            logging.error('Failed to create directory for report at {}'.format(
                output_path))
        create_intra_run_id_report(output_path,
                                   json_results,
                                   run_id)
    logging.info(
        'finished the execution of this script; results are in a folder')


if __name__ == '__main__':
    # TDH: This slightly complex mess allows lower importance messages
    # to be sent to the log file and ERROR messages to additionally
    # be sent to the console as well. Thus, when bad things happen
    # the user will get an error message in both places which,
    # hopefully, will aid in trouble-shooting.
    fileHandle = logging.FileHandler("benchmark_intra_run_PDF.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])
    # TDH (2020-01-13): Standard argument parsing
    parser = argparse.ArgumentParser(description='Generate PDF report.')
    parser.add_argument('-r',
                        '--benchmark_results_dir',
                        nargs='?',
                        default='../benchmark_results/2019-11-27')
    args = parser.parse_args()
    # TDH (2020-01-13) - Create the PDF for a benchmark intra-run
    _auto_run(args)
