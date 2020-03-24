# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 12:46:52 2020

Given the results for a test and a path for that test,
this script creates a report for the multinode benchmark
results files.  This allows the user to visualize the
performance of the multi-machine tests.

This script can be run as a standalone script to generate the 
multinode benchmark report PDF for every run in the user-provided path. 

The command line arguments for the function can be found in the code
following the lines following the "if __name__ == '__main__':" line
at the end of this file.

@author: barn553
"""

import argparse
import numpy as np
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

def create_multimachine_report(output_path, dataframe):
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
    header_metadata_str = grab_header_metadata(dataframe)
    line_height = 3
    pdf.write(line_height, header_metadata_str)

    # Add graphs to PDF object
    pdf = add_benchmark_graphs(pdf, output_path)

    # Output final PDF file from PDF object
    pdf.output(report_path)



def grab_header_metadata(dataframe):
    """This function creates the header metadata as a string.

    Args:
        json_results (dict) - benchmark results

    Returns:
        header_metadata_str (str) - Formatted header metadata for report
    """

    # TDH (2019-12-20): Since all the metadata is common for each run, I
    # can grab the metadata I need from any of the results files
    # corresponding to the indicated run.
    header_metadata_str = ''
    if 'date' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'date:',
                dataframe.date.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'date:',
                ' ')
        logging.error('"date" is not a column in dataframe')
#    if 'benchmark' in dataframe.columns.unique():
#        header_metadata_str += '{:<25}{}\n\n'.format(
#                'BENCHMARK:',
#                dataframe.benchmark.unique())
#    else:
#        header_metadata_str += '{:<25}{}\n'.format(
#                'BENCHMARK:',
#                ' ')
#        logging.error('"benchmark" is not a column in dataframe')
    if 'helics_version' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'HELICS version:',
                dataframe.helics_version.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'HELICS version:',
                ' ')
        logging.error('"helics_version" is not a column in dataframe')
    if 'generator' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'generator:',
                dataframe.generator.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'generator:',
                ' ')
        logging.error('"generator" is not a column in dataframe.')
    if 'system' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'system:',
                dataframe.system.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'system:',
                ' ')
        logging.error('"system" is not a column in dataframe.')
    if 'system_version' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'system version:',
                dataframe.system_version.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'system version:',
                ' ')
        logging.error('"system_version" is not a column in dataframe')
    if 'platform' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'platform:',
                dataframe.platform.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'platform:',
                ' ')
        logging.error('"platform" is not a column in dataframe')
    if 'cxx_compiler' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'C++ compiler:',
                dataframe.cxx_compiler.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'cxx_compiler:',
                ' ')
        logging.error('"cxx_compiler" is not a column in dataframe')
    if 'cxx_compiler_version' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'C++ compiler version:',
                dataframe.cxx_compiler_version.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'cxx_compiler_version:',
                ' ')
        logging.error('"cxx_compiler_version" is not a column in dataframe')
    if 'build_flags_string' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'compiler string:',
                dataframe.build_flags_string.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'compiler string:',
                ' ')
        logging.error('"build_flags_string" is not a column in dataframe')
    if 'host_processor' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'host processor:',
                dataframe.host_processor.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'host processor:',
                ' ')
        logging.error('"host_processor" is not a column in dataframe')
    if 'host_processor_string' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'CPU Model:',
                dataframe.host_processor_string.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'CPU Model:',
                ' ')
        logging.error('"host_processor_string" is not a column in dataframe')
    if 'mhz_per_cpu' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'processor speed (MHz):',
                dataframe.mhz_per_cpu.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'mhz_per_cpu:',
                ' ')
        logging.error('"mhz_per_cpu" is not a column in dataframe')
    if 'cluster' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'cluster:',
                dataframe.cluster.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'cluster:',
                ' ')
        logging.error('"cluster" is not a column in dataframe')
    if 'topology' in dataframe.columns.unique():
        header_metadata_str += '{:<25}{}\n'.format(
                'topology:',
                dataframe.topology.values[0])
    else:
        header_metadata_str += '{:<25}{}\n'.format(
                'topology:',
                ' ')
        logging.error('"topology" is not a column in dataframe')
    header_metadata_str = header_metadata_str + '\n' + '\n'
    logging.info('Final metadata header:\n{}'.format(header_metadata_str))
    return header_metadata_str


def add_benchmark_graphs(pdf, output_path):
    """This function adds the graphs to the PDF object.

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
                pdf.image(graph_file_path, x=15, w=175, h=100)
                logging.info('Added graph file {} to PDF'.format(output_path))
    return pdf


def make_multinode_graphs(dataframe, output_path):
    """This function creates the graphs for multinode_benchmark
    _results data and sends them to the output_path
    
    Args:
        dataframe (pandas dataframe) - Contains all multinode
        benchmark results data.
        output_path (str) - Path to send graphs.
        
    Returns:
        (null)
    """
    if 'PholdFederate' in list(dataframe.benchmark.unique()):
        df = dataframe[dataframe.benchmark == 'PholdFederate']
        bmk_plotting.mm_plot(df, 
                             'federate_count', 
                             'elapsed_time', 
                             'core_type', 
                             '', 
                             False, 
                             '', 
                             'PholdFederate', 
                             'Multinode',
                             output_path)
        bmk_plotting.mm_plot(df,
                             'federate_count',
                             'elapsed_time',
                             'core_type',
                             'EvCount',
                             True,
                             'cps',
                             'PholdFederate',
                             'Multinode',
                             output_path)
    elif 'EchoLeafFederate' in list(dataframe.benchmark.unique()):
        df = dataframe[dataframe.benchmark == 'EchoLeafFederate']
        bmk_plotting.mm_plot(df, 
                             'federate_count', 
                             'elapsed_time', 
                             'core_type', 
                             '', 
                             False, 
                             '', 
                             'EchoLeafFederate', 
                             'Multinode',
                             output_path)
    elif 'EchoMessageLeafFederate' in list(dataframe.benchmark.unique()):
        df = dataframe[dataframe.benchmark == 'EchoMessageLeafFederate']
        bmk_plotting.mm_plot(df, 
                             'federate_count', 
                             'elapsed_time', 
                             'core_type', 
                             '', 
                             False, 
                             '', 
                             'EchoMessageLeafFederate', 
                             'Multinode',
                             output_path)
    elif 'MessageExchangeFederate' in list(dataframe.benchmark.unique()):
        pass
#        df = dataframe[(dataframe.benchmark == 'MessageExchangeFederate') & 
#                       (dataframe.federate_count == 2)]
#        df.message_count = np.nan_to_num(df.message_count)
#        df.message_size = np.nan_to_num(df.message_size)
#        bmk_plotting.mm_plot(df, 
#                             'message_count', 
#                             'elapsed_time', 
#                             'core_type', 
#                             '', 
#                             False, 
#                             '', 
#                             'MessageExchange_2', 
#                             'Multinode',
#                             output_path)
#        bmk_plotting.mm_plot(df, 
#                             'message_size', 
#                             'elapsed_time', 
#                             'core_type', 
#                             '', 
#                             False, 
#                             '', 
#                             'MessageExchange_1', 
#                             'Multinode',
#                             output_path)
    elif 'RingTransmitFederate' in list(dataframe.benchmark.unique()):
        df = dataframe[dataframe.benchmark == 'RingTransmitFederate']
        bmk_plotting.mm_plot(df, 
                             'federate_count', 
                             'elapsed_time', 
                             'core_type', 
                             '', 
                             False, 
                             '', 
                             'RingTransmitFederate', 
                             'Multinode',
                             output_path)
    elif 'TimingLeafFederate' in list(dataframe.benchmark.unique()):
        df = dataframe[dataframe.benchmark == 'TimingLeafFederate']
        bmk_plotting.mm_plot(df, 
                             'federate_count', 
                             'elapsed_time', 
                             'core_type', 
                             '', 
                             False, 
                             '', 
                             'TimingLeafFederate', 
                             'Multinode',
                             output_path)
    
    else:
        logging.error('Failed to create graphs')


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
        '-m' or '--m_benchmark_results_dir' - Path of top-level folder
        that contains the multinode benchmark results folders/files 
        to be processed.
        
        '-j' or '--json_file' - JSON file of all the multinode
        benchmark results data.
        
        '-f' or '--default_file' - Default file to use for creating
        a report.

    Returns:
        (nothing)
    """
#    # Grabbing the data and adding it to the JSON
#    json_results = {}
#    d = co.defaultdict(dict)
#    file = args.default_file
#    json_results.update(mpp.parse_files(file))
#    json_results = (mpp.parse_and_add_benchmark_metadata(json_results))
#    d[file].update(json_results)
    
#    json_results = {}
#    file_list = []
#    for root, dirs, files in os.walk(args.multinode_benchmark_results_dir):
#        for file in files:
#            if file != 'helics-broker-out.txt':
#                file_list.append(os.path.join(root, file))
#            else:
#                pass
#    d = co.defaultdict(dict)
#    for file in file_list:
#        json_results.update(mpp.parse_files(file))
#        json_results = (mpp.parse_and_add_benchmark_metadata(json_results))
#        d[file].update(json_results)
#        json_results = {}
    
    # Creating the multinode report.
    multi_bmk_df = md.make_dataframe2(args.json_file)
#    output_path = os.path.join(args.multinode_benchmark_results_dir)
    for benchmark in multi_bmk_df.benchmark.unique():
        print('BENCHMARK: ', benchmark)
        if benchmark == 'PholdFederate':
            output_path = os.path.join(args.multinode_benchmark_results_dir, 
                                       '2020-01-08')
            df = multi_bmk_df[multi_bmk_df.benchmark == benchmark]
            make_multinode_graphs(df, output_path)
            create_multimachine_report(output_path,
                                       df)
        else:
            output_path = os.path.join(args.multinode_benchmark_results_dir, 
                                       '2020-03-13')
            df = multi_bmk_df[multi_bmk_df.benchmark == benchmark]
            make_multinode_graphs(df, output_path)
            create_multimachine_report(output_path,
                                       df)


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
                        default='../multinode_benchmark_results')
    parser.add_argument('-j',
                        '--json_file',
                        nargs='?',
                        default='multinode_bm_results_test.json')
#    parser.add_argument('-o', 
#                        '--output_path', 
#                        nargs='?', 
#                        default='../multinode_benchmark_results/2020-01-08')
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