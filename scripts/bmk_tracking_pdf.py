# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 11:29:43 2020

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
import benchmark_postprocessing as bmpp
import make_dataframe as md

# Installation of FPDF is: python -m pip install fpdf


# Setting up logging
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

def create_benchmark_tracking_report(output_path, json_results):
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
    report_name = 'benchmark_tracking.pdf'
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
    

def grab_header_metadata(json_results, run_id):
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
    for key in key_list:
        if json_results[key]['run_id'] == run_id:
            break
    header_metadata_str = ''
    if 'benchmark' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n\n'.format(
            'BENCHMARK:',
            json_results[key]['benchmark'])
    else:
        logging.warning('"benchmark" not found in metadata.')

    if 'run_id' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
            'run ID:',
            json_results[key]['run_id'])
    else:
        logging.warning('"run_id" not found in metadata.')

    if 'date' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
            'Timestamp:',
            json_results[key]['date'])
    else:
        logging.warning('"run_id" not found in metadata.')

#    if 'helics_version' in json_results[key]:
#        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
#            'HELICS version:',
#            json_results[key]['helics_version'])
#    else:
#        logging.warning('"helics_version" not found in metadata.')

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

    if 'host_name' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
            'host name:',
            json_results[key]['host_name'])
    else:
        logging.warning('"host_name" not found in metadata.')

    if 'host_processor' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
            'host processor:',
            json_results[key]['host_processor'])
    else:
        logging.warning('"host_processor" not found in metadata.')

    if 'num_cpus' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
            'CPU core count:',
            json_results[key]['num_cpus'])
    else:
        logging.warning('"num_cpus" not found in metadata.')

    if 'mhz_per_cpu' in json_results[key]:
        header_metadata_str = header_metadata_str + '{:<25}{}\n'.format(
            'processor speed (MHz):',
            json_results[key]['mhz_per_cpu'])
    else:
        logging.warning('"mhz_per_cpu" not found in metadata.')

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
                pdf.image(graph_file_path, x=15, w=175, h=100)
                logging.info('Added graph file {} to PDF'.format(output_path))
    return pdf


def make_benchmark_track_graphs(meta_bmk_df, output_path):
    """This function creates the graphs for the 'tracking' benchmarks'
    data.
    
    Args:
        meta_bmk_df (obj):  Pandas dataframe of the 'tracking'
        benchmarks' data.
        output_path (path): Path to send the graphs.
        
    Returns:
        (null)
    """
    if 'echoMessageBenchmark' in list(meta_bmk_df.benchmark.unique()):
        track = meta_bmk_df[(meta_bmk_df.benchmark == 'echoMessageBenchmark') & 
                            (meta_bmk_df.benchmark_type == 'key')]
        bmk_plotting.sa_plot(track,
                             'date',
                             'real_time', 
                             'echoMessage', 
                             by_bool=True, 
                             by_name='core_type', 
                             run_id='', 
                             output_path)
    if 'echoBenchmark' in list(meta_bmk_df.benchmark.unique()):
        track = meta_bmk_df[(meta_bmk_df.benchmark == 'echoBenchmark') & 
                            (meta_bmk_df.benchmark_type == 'key')]
        bmk_plotting.sa_plot(track,
                             'date',
                             'real_time', 
                             'echo', 
                             by_bool=True, 
                             by_name='core_type', 
                             run_id='', 
                             output_path)
    if 'messageLookupBenchmark' in list(meta_bmk_df.benchmark.unique()):
        track = meta_bmk_df[(meta_bmk_df.benchmark == 'messageLookupBenchmark') & 
                            (meta_bmk_df.benchmark_type == 'key')]
        bmk_plotting.sa_plot(track,
                             'date',
                             'real_time', 
                             'messageLookup', 
                             by_bool=True, 
                             by_name='core_type', 
                             run_id='', 
                             output_path)
    if 'timingBenchmark' in list(meta_bmk_df.benchmark.unique()):
        track = meta_bmk_df[(meta_bmk_df.benchmark == 'timingBenchmark') & 
                            (meta_bmk_df.benchmark_type == 'key')]
        bmk_plotting.sa_plot(track,
                             'date',
                             'real_time', 
                             'timing', 
                             by_bool=True, 
                             by_name='core_type', 
                             run_id='', 
                             output_path)
        

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
    file_list = bmpp.get_benchmark_files(args.benchmark_results_dir)
    json_results = bmpp.parse_files(file_list)
    json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    
    ### CGR (2020-02-10) Add a json_file argument to the parser so that
    ### we can just grab the bm_results.json file for the dataframe
    ### function
    meta_bmk_df = md.make_dataframe1(args.json_file)
    output_path = os.path.join(args.output_path)
    make_benchmark_track_graphs(meta_bmk_df, output_path)
    create_benchmark_tracking_report(output_path,
                                     json_results)


if __name__ == '__main__':
    fileHandle = logging.FileHandler("benchmark_tracking_PDF.log", mode='w')
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
    parser.add_argument('-j',
                        '--json_file',
                        nargs='?',
                        default='bm_results.json')
    args = parser.parse_args()
    default_output_path == os.path.join(args.benchmark_results_dir, 'benchmark_tracking')
    parser.add_argument('-o', 
                        '--output_path', 
                        nargs='?',
                        default=default_output_path)
    args = parser.parse_args()
    # TDH (2020-01-13) - Create the PDF for a standard analysis
    _auto_run(args)