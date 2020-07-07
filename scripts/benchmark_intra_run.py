# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 08:24:59 2020

Performs intra-run analysis that compares multiple
benchmarks' data for a single run.  This allows the user
to visualize the performance across multiple benchmarks
for a single run.

This script can be run as a standalone script to generate the intra-run
analysis for every run in the user-provided path. By default it will not
overwrite any existing report. A "run" is specified by the 5 character
unique ID in the filename for every results file associated with that
run.

The command line arguments for the function can be found in the code
following the lines following the "if __name__ == '__main__':" line
at the end of this file.

@author: barn553
"""

import argparse
import logging
import pprint
import os
import shutil
import benchmark_postprocessing as bmpp
import benchmark_intra_run_pdf as birp
import standard_analysis as sa
from bmk_plotting import ir_plot
import make_dataframe as md
import sys

# Installation of FPDF is: python -m pip install fpdf
# Installation of hvplot.pandas is: conda install -c pyviz hvplot
# Installation of selenium is: conda install -c bokeh selenium
# Installation of phantomjs is: brew tap homebrew/cask; brew cask install
# phantomjs

# TDH: Setting up logging
logger = logging.getLogger(__name__)

# TDH: Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)


def find_specific_run_id(benchmark_results_dir, run_id_list):
    """This function traverses the directory structure starting at the
    root folder of benchmark_results_dir looking for the folders that
    contain the run-IDs for comparison (specified in run_id_list).

    Args:
        benchmark_results_dir (str) - root folder that contains all
        results from the run IDs specified in run_id_list.

        run_id_list (list) - List of strings defining the run IDs to
        compare

    Returns:
        run_id_dict (dict) - Dictionary containing file-level data
        needed to run the cross-run-ID comparison such as a list of files
        associated with each run-ID, the path to the folder containing
        the results files, etc.
    """
    run_id_dict = {}
    for root, dirs, files in os.walk(benchmark_results_dir):
        for file in files:
            # If the root ends in 'report' than we are in a report
            # directory and can ignore all the files inside since they
            # do not contain benchmark results
            if root[-6:] != 'report':
                # TDH (2019-12-26):  Assume all files ending in '.txt'
                # are the results files.
                head, tail = os.path.splitext(file)
                if tail == '.txt':
                    # TDH (2019-12-23): Assuming that the files are
                    # always named such that the run id is the last
                    # five characters before the ".txt"...
                    run_id = file[-9:-4]
                    if run_id in run_id_list:
                        if run_id not in run_id_dict.keys():
                            run_id_dict[run_id] = {}
                        if 'files' not in run_id_dict[run_id].keys():
                            run_id_dict[run_id]['files'] = []
                        if 'bm_data_path' not in run_id_dict[run_id].keys():
                            run_id_dict[run_id]['bm_data_path'] = root
                        if file not in run_id_dict[run_id]['files']:
                            run_id_dict[run_id]['files'].append(
                                os.path.join(root, file))
                            logging.info('Added file to process {}'.format(
                                file))
    return run_id_dict


def create_output_path(output_path_list, delete_existing_report):
    """This function creates any output folders that are needed for
    storing the graphs and final PDF report. If specified, it will also
    delete the existing report folder.

    Args:
        output_path (str) - Path to the results folder for the comparison
        of these run-IDs

        delete_existing_report (bool) - Flag indicating whether any
        existing report folder should be deleted (True) or not (False)

    Returns:
        null
    """
    # "head" will be the full path to and including "benchmark_tracking"
    # "tail" will be just the name of the report folder
    for output in output_path_list:
        head, tail = os.path.split(output)
        # TDH (2020-01-14)
        # If for some reason the parent folder that contains all the intra-run
        # information does not exist it needs to be created. If it
        # does exist we can just move on.
        if os.path.exists(head):
            pass
        else:
            try:
                os.mkdir(head)
            except OSError:
                logging.error('Failed to create directory {}'.format(head))
                print('Failed to create directory {}'.format(head))
        # TDH (2020-01-14)
        # Now working on creating the folder specific to the benchmarks being
        # compared.
        if os.path.exists(output):
            if delete_existing_report:
                shutil.rmtree(output)
        else:
            try:
                os.mkdir(output)
            except OSError:
                logging.error('Failed to create directory {}'.format(output))


def make_intra_run_graphs(meta_bmk_df, run_id, bm_list, core_type,
                          output_path):
    """This function creates intra-run graphs of multiple benchmarks, for a
    given run_id.  In other words, given a run-id, this function creates
    plots of the echoBenchmark and cEchoBenchmark results for making
    comparisons.

    Args:
        meta_bmk_df (pandas dataframe) - Full dataset.

        run_id (str) - Specific run_id used to create this plot.

        bm_list (list) - List of benchmarks to create intra-run graphs.

        core_type_list - Specific core_types used to create this plot.

        output_path (str) - Location to send the graph.

    Returns:
        (null)
    """
    # Creating the comparison between echo and timing benchmark
    if 'echoBenchmark' in bm_list and 'timingBenchmark' in bm_list:
        df1 = meta_bmk_df[meta_bmk_df.benchmark == 'echoBenchmark']
        df2 = meta_bmk_df[meta_bmk_df.benchmark == 'timingBenchmark']
        # Making sure the run-ids have results for echo and timing
        # benchmarks.  If so, plots are generated.  Otherwise we get an error.
        if any(df1.run_id.isin(df2.run_id)) and any(
                df1.core_type.isin(df2.core_type)):
            ir_plot(
                df1, df2, 'federate_count', 'real_time',
                'echo', 'timing', False, '',
                'federate_count vs real_time', run_id, core_type, output_path)
            ir_plot(
                df1, df2, 'federate_count', 'real_time',
                'echo', 'timing', True, 'spc',
                'federate_count vs spf', run_id, core_type, output_path)
            logging.info(
                'echo vs timing plot has been created for run-id {}'.format(
                    run_id))
        else:
            logging.error(
                'run_id {} doesn\'t have echo AND timing results'.format(
                    run_id))
    # Creating the comparison between echo and cEcho benchmark
    if 'echoBenchmark' in bm_list and 'cEchoBenchmark' in bm_list:
        df1 = meta_bmk_df[meta_bmk_df.benchmark == 'echoBenchmark']
        df2 = meta_bmk_df[meta_bmk_df.benchmark == 'cEchoBenchmark']
        if any(df1.run_id.isin(df2.run_id)) and any(
                df1.core_type.isin(df2.core_type)):
            ir_plot(
                df1, df2, 'federate_count', 'real_time',
                'echo', 'cEcho', False, '',
                'federate_count vs real_time', run_id, core_type, output_path)
            ir_plot(
                df1, df2, 'federate_count', 'real_time',
                'echo', 'cEcho', True, 'spc',
                'federate_count vs spf', run_id, core_type, output_path)
            logging.info(
                'echo vs cEcho plot has been created for run-id {}'.format(
                    run_id))
        else:
            logging.error(
                'run_id {} doesn\'t have echo AND cEcho results'.format(
                    run_id))
    # For additional intra-run benchmark comparisons, simply copy and paste
    # the above code, and change accordingly.  For example, if we wanted
    # to compare echo and echoMessage, change either 'timing' or 'cEcho' to
    # 'echoMessage'.


def _auto_run(args):
    """This function executes when the script is called as a stand-alone
    executable. It is used both for development/testing as well as the
    primary executable for generating the intra-run analysis PDF report.

    A more complete description of this code can be found in the
    docstring at the beginning of this file.

    Args:
        '-r' or '--benchmark_results_dir' - Path of top-level folder
        that contains the benchmark results folders/files to be
        processed.

        '-l' or '--run_id_list' - Python list of run IDs to compare.

        '-b' or '--bm_list' - List of benchmarks for intra-run comparison
        plots.

        '-c' or '--core_type_list' - List of core_types for the graphs.

        '-o' or '--output_path_list' - List of output paths for each
        run_id to send the intra-run reports.

        '-d' or '--delete_all_reports' - "True" or "False" to indicate
        if existing reports should be over-written

    Returns:
        (nothing)
    """
    logging.info('starting the execution of this script...')
    # Finding the specific run-ids and creating the output path.
    run_id_dict = find_specific_run_id(args.benchmark_results_dir,
                                       args.run_id_list)
    create_output_path(args.output_path_list, args.delete_report)
    file_list = []
    for run_id in run_id_dict:
        file_list.extend(run_id_dict[run_id]['files'])
    # Preparing the data for analysis.
    bm_files, bmk_files = sa.sort_results_files(file_list)
    file_list = bm_files
    json_results = bmpp.parse_files(file_list)
    json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    meta_bmk_df = md.make_dataframe1(json_results)
    counter = 0
    # Creating the analysis reports.
    for run_id in args.run_id_list:
        for core_type in args.core_type_list:
            make_intra_run_graphs(
                meta_bmk_df, run_id, args.bm_list, core_type,
                args.output_path_list[counter])
        birp.create_intra_run_id_report(
            args.output_path_list[counter], json_results, run_id)
        counter += 1
    logging.info(
        'finished the execution of this script; results are in a folder')


if __name__ == '__main__':
    # TDH: This slightly complex mess allows lower importance messages
    # to be sent to the log file and ERROR messages to additionally
    # be sent to the console as well. Thus, when bad things happen
    # the user will get an error message in both places which,
    # hopefully, will aid in trouble-shooting.
    fileHandle = logging.FileHandler("intra_run.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])
    # TDH: Standard argument parsing
    parser = argparse.ArgumentParser(description='Generate PDF report.')
    # TDH: Have to do a little bit of work to generate a good default
    # path for the results folder. Default only works if being run
    # from the "scripts" directory in the repository structure.
    script_path = os.path.dirname(os.path.realpath(__file__))
    head, tail = os.path.split(script_path)
    benchmark_results_dir = os.path.join(head, 'benchmark_results')
    output_dir = os.path.join(head, 'intra_run_comparison')
    bm_list = ['echoBenchmark', 'cEchoBenchmark', 'timingBenchmark']
    core_type_list = [
        'singleCore', 'inproc', 'zmq', 'zmqss',
        'ipc', 'tcp', 'tcpss', 'udp']
    parser.add_argument('-r',
                        '--benchmark_results_dir',
                        nargs='?',
                        default=benchmark_results_dir)
    parser.add_argument('-l',
                        '--run_id_list',
                        nargs='?',
                        default=['bScQ6', 'Obg9g'])
    args = parser.parse_args()
    parser.add_argument('-b',
                        '--bm_list',
                        nargs='?',
                        default=bm_list)
    parser.add_argument('-c',
                        '--core_type_list',
                        nargs='?',
                        default=core_type_list)
    args = parser.parse_args()

    dir_name_list = []
    for run_id in args.run_id_list:
        dir_name = '' + str(run_id) + '_intra_run_report'
        dir_name_list.append(dir_name)
    default_output_path_list = [
        os.path.join(output_dir, d) for d in dir_name_list]
    parser.add_argument('-o',
                        '--output_path_list',
                        nargs='?',
                        default=default_output_path_list)
    parser.add_argument('-d',
                        '--delete_report',
                        nargs='?',
                        default=False)
    args = parser.parse_args()
    # TDH: Run the standard analysis
    _auto_run(args)
