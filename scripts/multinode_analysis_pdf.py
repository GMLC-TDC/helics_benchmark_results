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
import pandas as pd
import numpy as np
import logging
import pprint
import os
import sys
from fpdf import FPDF
import bmk_plotting
import make_dataframe as md

# Installation of FPDF is: python -m pip install fpdf

# Setting up logger
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
        if pd.isnull(np.asarray(dataframe.date.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'date:',
                ' ')
            logging.error('"date" is not a column in dataframe')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'date:',
                    dataframe.date.unique()[-1])
    else:
        logging.error('"date" is not a column in dataframe')
    if 'helics_version' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.helics_version.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'HELICS version:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'HELICS version:',
                    dataframe.helics_version.unique()[-1])
    else:
        logging.error('"helics_version" is not a column in dataframe')
    if 'generator' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.generator.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'generator:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'generator:',
                    dataframe.generator.unique()[-1])
    else:
        logging.error('"generator" is not a column in dataframe.')
    if 'system' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.system.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'system:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'system:',
                    dataframe.system.unique()[-1])
    else:
        logging.error('"system" is not a column in dataframe.')
    if 'system_version' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.system_version.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'system version:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'system version:',
                    dataframe.system_version.unique()[-1])
    else:
        logging.error('"system_version" is not a column in dataframe')
    if 'platform' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.platform.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'platform:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'platform:',
                    dataframe.platform.unique()[-1])
    else:
        logging.error('"platform" is not a column in dataframe')
    if 'cxx_compiler' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.cxx_compiler.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'cxx_compiler:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'C++ compiler:',
                    dataframe.cxx_compiler.unique()[-1])
    else:
        logging.error('"cxx_compiler" is not a column in dataframe')
    if 'cxx_compiler_version' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.cxx_compiler_version.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'cxx_compiler_version:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'C++ compiler version:',
                    dataframe.cxx_compiler_version.unique()[-1])
    else:
        logging.error('"cxx_compiler_version" is not a column in dataframe')
    if 'build_flags_string' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.build_flags_string.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'compiler string:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'compiler string:',
                    dataframe.build_flags_string.unique()[-1])
    else:
        logging.error('"build_flags_string" is not a column in dataframe')
    if 'host_processor' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.host_processor.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'host processor:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'host processor:',
                    dataframe.host_processor.unique()[-1])
    else:
        logging.error('"host_processor" is not a column in dataframe')
    if 'host_processor_string' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.host_processor_string.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'CPU Model:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'CPU Model:',
                    dataframe.host_processor_string.unique()[-1])
    else:
        logging.error('"host_processor_string" is not a column in dataframe')
    if 'mhz_per_cpu' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.mhz_per_cpu.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'mhz_per_cpu:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'processor speed (MHz):',
                    dataframe.mhz_per_cpu.unique()[-1])
    else:
        logging.error('"mhz_per_cpu" is not a column in dataframe')
    if 'cluster' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.cluster.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'cluster:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'cluster:',
                    dataframe.cluster.unique()[-1])
    else:
        logging.error('"cluster" is not a column in dataframe')
    if 'topology' in dataframe.columns.unique():
        if pd.isnull(np.asarray(dataframe.topology.unique()[-1])):
            header_metadata_str += '{:<25}{}\n'.format(
                'topology:',
                ' ')
        else:
            header_metadata_str += '{:<25}{}\n'.format(
                    'topology:',
                    dataframe.topology.unique()[-1])
    else:
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
    for benchmark in dataframe.benchmark.unique():
        if benchmark == 'PholdFederate':
            if list(dataframe.date.unique())[0] >= '2020-06-27':
                for c in dataframe.core_type.unique():
                    df = dataframe[(dataframe.benchmark == 'PholdFederate') &
                                   (dataframe.core_type == '{}'.format(c))]
                    bmk_plotting.mm_plot(
                        df, 'federate_count',
                        'elapsed_time', 'feds_per_node',
                        '', False,
                        '', 'PholdFederate, {}, feds_per_node'.format(c),
                        'Multinode', output_path)
                    bmk_plotting.mm_plot(
                        df, 'federate_count',
                        'elapsed_time', 'feds_per_node',
                        'EvCount', True,
                        'cps', 'PholdFederate, {}, feds_per_node'.format(c),
                        'Multinode', output_path)
            else:
                df = dataframe[dataframe.benchmark == 'PholdFederate']
                bmk_plotting.mm_plot(
                        df, 'federate_count', 'elapsed_time',
                        'core_type', '', False,
                        '', 'PholdFederate', 'Multinode',
                        output_path)
                bmk_plotting.mm_plot(
                    df, 'federate_count', 'elapsed_time',
                    'core_type', 'EvCount', True,
                    'cps', 'PholdFederate', 'Multinode',
                    output_path)
        elif benchmark == 'EchoLeafFederate':
            df = dataframe[dataframe.benchmark == 'EchoLeafFederate']
            bmk_plotting.mm_plot(
                df, 'federate_count', 'elapsed_time',
                'core_type', '', False,
                '', 'EchoLeafFederate', 'Multinode',
                output_path)
        elif benchmark == 'EchoMessageLeafFederate':
            df = dataframe[dataframe.benchmark == 'EchoMessageLeafFederate']
            bmk_plotting.mm_plot(
                df, 'federate_count', 'elapsed_time',
                'core_type', '', False,
                '', 'EchoMessageLeafFederate', 'Multinode',
                output_path)
        elif benchmark == 'MessageExchangeFederate':
            df = dataframe[dataframe.benchmark == 'MessageExchangeFederate']
            bmk_plotting.mm_plot(
                df, 'message_count', 'elapsed_time',
                'core_type', '', False,
                '', 'MessageExchange_2', 'Multinode',
                output_path)
            bmk_plotting.mm_plot(
                df, 'message_size', 'elapsed_time',
                'core_type', '', False,
                '', 'MessageExchange_1', 'Multinode',
                output_path)
        elif benchmark == 'RingTransmitFederate':
            df = dataframe[dataframe.benchmark == 'RingTransmitFederate']
            bmk_plotting.mm_plot(
                df, 'federate_count', 'elapsed_time',
                'core_type', '', False,
                '', 'RingTransmitFederate', 'Multinode',
                output_path)
        elif benchmark == 'RingTransmitMessageFederate':
            df = dataframe[
                dataframe.benchmark == 'RingTransmitMessageFederate']
            bmk_plotting.mm_plot(
                df, 'federate_count', 'elapsed_time',
                'core_type', '', False,
                '', 'RingTransmitMessageFederate', 'Multinode',
                output_path)
        elif benchmark == 'TimingLeafFederate':
            df = dataframe[dataframe.benchmark == 'TimingLeafFederate']
            bmk_plotting.mm_plot(
                df, 'federate_count', 'elapsed_time',
                'core_type', '', False,
                '', 'TimingLeafFederate', 'Multinode',
                output_path)
        else:
            logging.error('benchmark {} is an invalid benchmark'.format(
                benchmark))
    logging.info('created the plots for the multinode results')


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

    Returns:
        (nothing)
    """
    logging.info('starting the execution of this script...')
    # Creating the multinode report.
    multi_bmk_df = md.make_dataframe2(args.json_file)
    for date in multi_bmk_df.date.unique():
        logging.info('creating the multinode analysis for {}'.format(date))
        output_path = os.path.join(args.multinode_benchmark_results_dir, date)
        df = multi_bmk_df[multi_bmk_df.date == date]
        make_multinode_graphs(df, output_path)
        create_multimachine_report(output_path, df)
    msg_df = multi_bmk_df[
        (multi_bmk_df.benchmark == 'MessageExchangeFederate') &
        (multi_bmk_df.date != '2020-03-13') &
        (multi_bmk_df.date != '2020-06-15')]
    output_path = os.path.join(
        args.multinode_benchmark_results_dir, '2020-06-17')
    logging.info('creating additional images for MessageExchangeFederate')
    bmk_plotting.mm_plot(
        msg_df, 'message_size', 'elapsed_time',
        'core_type', '', False,
        '', 'MessageExchange_3', 'Multinode',
        output_path)
    bmk_plotting.mm_plot(
        msg_df, 'message_count', 'elapsed_time',
        'core_type', '', False,
        '', 'MessageExchange_4', 'Multinode',
        output_path)
    logging.info('finished creating the multinode analysis reports.')


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
                        default='multinode_bm_results.json')
    args = parser.parse_args()
    # CGR (2020-03-25) - Create the PDF for multinode analysis
    _auto_run(args)
