# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 12:46:52 2020

@author: barn553
"""

import argparse
import logging
import pprint
import os
import sys
from fpdf import FPDF
import collections as co
import bmk_plotting
import multinode_postprocessing as mpp
import make_dataframe as md

# Installation of FPDF is: python -m pip install fpdf


# Setting up logging
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

def create_multimachine_report(output_path, json_results):
    """This function creates the multinode report.
    
    Args:
        output_path (str) - Path where graph images are located and PDF
        report will be saved.
        json_results (dict) - benchmark results
    
    Returns:
        (null)
    """
        # Create the PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=8)

    # Define the output path for the report PDF
    report_name = 'multinode_analysis.pdf'
    report_path = os.path.join(output_path, report_name)

    # Create the header metadata from the metadata in the JSON results
    # and write out to PDF
    header_metadata_str = grab_header_metadata(json_results)
    line_height = 3
    pdf.write(line_height, header_metadata_str)

    # Add graphs to PDF object
    pdf = add_benchmark_graphs(pdf, output_path)

    # Output final PDF file from PDF object
    pdf.output(report_path)



def grab_header_metadata(json_results):
    """This function creates the header metadata as a string

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
    header_metadata_str = ''
    for key in key_list:
        if 'benchmark' in json_results[key]:
            header_metadata_str = header_metadata_str + '{:<25}{}\n\n'.format(
                'BENCHMARK:',
                json_results[key]['benchmark'])
        else:
            logging.warning('"benchmark" not found in metadata.')
    
    #    if 'run_id' in json_results[key]:
    #        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
    #            'run ID:',
    #            json_results[key]['run_id'])
    #    else:
    #        logging.warning('"run_id" not found in metadata.')
    
        if 'helics_version' in json_results[key]:
            header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
                'HELICS version:',
                json_results[key]['helics_version'])
        else:
            logging.warning('"helics_version" not found in metadata.')
    
        if 'generator' in json_results[key]:
            header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
                'generator:',
                json_results[key]['generator'])
        else:
            logging.warning('"generator" not found in metadata.')
    
        if 'system' in json_results[key]:
            header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
                'system:',
                json_results[key]['system'])
        else:
            logging.warning('"system" not found in metadata.')
    
        if 'system_version' in json_results[key]:
            header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
                'system version:',
                json_results[key]['system_version'])
        else:
            logging.warning('"system_version" not found in metadata.')
    
        if 'platform' in json_results[key]:
            header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
                'platform:',
                json_results[key]['platform'])
        else:
            logging.warning('"platform" not found in metadata.')
    
        if 'cxx_compiler' in json_results[key]:
            header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
                'C++ compiler:',
                json_results[key]['cxx_compiler'])
        else:
            logging.warning('"cxx_compiler" not found in metadata.')
    
        if 'cxx_compiler_version' in json_results[key]:
            header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
                'C++ compiler version:',
                json_results[key]['cxx_compiler_version'])
        else:
            logging.warning('"cxx_compiler_version" not found in metadata.')
    
        if 'build_flags_string' in json_results[key]:
            header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
                'compiler string:',
                json_results[key]['build_flags_string'])
        else:
            logging.warning('"build_flags_string" not found in metadata.')
    
        if 'host_processor' in json_results[key]:
            header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
                'host processor:',
                json_results[key]['host_processor'])
        else:
            logging.warning('"host_processor" not found in metadata.')
    
        header_metadata_str = header_metadata_str + '\n' + '\n'
        logging.info('Final metadata header:\n{}'.format(header_metadata_str))
    return header_metadata_str


def add_benchmark_graphs(pdf, output_path):
    """This function adds the graphs to the PDF object

    Args:
        pdf (PDF obj) - PDF report object
        output_path (str) - Path where graph images are located and PDF

    Returns:
        pdf (PDF obj) - PDF report object with graph images included
    """
    for root, dirs, files in os.walk(output_path):
        # TDH (2019-12-23): Trying to keep the graphs in a consistent
        # order so they appear in the report in the same order from report
        # to report.
        files.sort()
        for file in files:
            name, extension = os.path.splitext(file)
            if extension == '.png':
                graph_file_path = os.path.join(output_path, file)
                # TDH (2020-01-13) Resize graph images when adding them
                # to the PDF.
                # width = 0
                # height = 0
                # pdf.image(graph_file_path, w=width, h=height)
                pdf.image(graph_file_path, x=15, w=175, h=100)
                logging.info('Added graph file {} to PDF'.format(output_path))
    return pdf


def make_multinode_graphs(multi_bmk_df, output_path):
    """This function creates the graphs for multinode_benchmark
    _results data and sends them to the output_path
    
    Args:
        multi_bmk_df (obj): Pandas dataframe that contains all multinode
        benchmark results data.
        output_path (path: Path to send graphs.
    Returns:
        (null)
    """
    if 'PholdFederate' in list(multi_bmk_df.benchmark.unique()):
        benchmark = 'PholdFederate'
        bmk_plotting.plot_counts_per_second(multi_bmk_df, benchmark, output_path)
        bmk_plotting.plot_total_seconds(multi_bmk_df, benchmark, output_path)
    else:
        pass


def _auto_run(args):
    """This function executes when the script is called as a stand-alone
    executable. It is used both for development/testing as well as the
    primary executable for generating the standard analysis PDF report.
    To use as a stand-alone script (primarily for development purspoes)
    the script has to replicate some of the functionality in
    "standard_analysis.py" to generate json_results for use here.

    A more complete description of this code can be found in the
    docstring at the beginning of this file.

    Args:
        '-r' or '--benchmark_results_dir' - Path of top-level folder
        that contains the benchmark results folders/files to be
        processed.

    Returns:
        (nothing)
    """

    # TDH (2020-01-13) For developement testing the following section
    # replicates the functionality of "standard_analysis.py" so that
    # json_results can be created and used to create the graph image
    # files.
    
    
    json_results = {}
    d = co.defaultdict(dict)
    file = args.default_file
    json_results.update(mpp.parse_files(file))
    json_results = (mpp.parse_and_add_benchmark_metadata(json_results))
    d[file].update(json_results)
#        jsons.append(json_results)
#        json_results = {}
    multi_bmk_df = md.make_dataframe2(args.json_file)
    output_path = os.path.join(args.multinode_benchmark_results_dir)
    make_multinode_graphs(multi_bmk_df, output_path)
    create_multimachine_report(output_path,
                               json_results)



if __name__ == '__main__':
    # TDH: This slightly complex mess allows lower importance messages
    # to be sent to the log file and ERROR messages to additionally
    # be sent to the console as well. Thus, when bad things happen
    # the user will get an error message in both places which,
    # hopefully, will aid in trouble-shooting.
    fileHandle = logging.FileHandler("multinode_analysis_PDF.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])

    # TDH (2020-01-13): Standard argument parsing
    parser = argparse.ArgumentParser(description='Generate PDF report.')
    parser.add_argument('-m',
                        '--multinode_benchmark_results_dir',
                        nargs='?',
                        default='../multinode_benchmark_results/2020-01-08')
    parser.add_argument('-j',
                        '--json_file',
                        nargs='?',
                        default='multinode_bm_results.json')
    args = parser.parse_args()
    default_dir = os.path.join(args.multinode_benchmark_results_dir,
                               'PholdFederate-tcp-N1-job-4286628')
    default_file = os.path.join(default_dir, 'PholdFederate-0-out.txt')
    parser.add_argument('-f', 
                        '--default_file',
                        nargs='?',
                        default=default_file)
    args = parser.parse_args()
    # TDH (2020-01-13) - Create the PDF for a standard analysis
    _auto_run(args)