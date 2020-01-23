# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 08:24:59 2020

@author: barn553
"""

import argparse
import logging
import pprint
import os
import shutil
import benchmark_postprocessing as bmpp
import benchmark_inter_run_pdf as birp
import standard_analysis as sa
import bmk_plotting
import make_dataframe as md
import sys

# Installation of FPDF is: python -m pip install fpdf
# Installation of hvplot.pandas is: conda install -c pyviz hvplot
# Installation of selenium is: conda install -c bokeh selenium
# Installation of phantomjs is: brew tap homebrew/cask; brew cask install phantomjs

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
                            run_id_dict[run_id]['files'].append(os.path.join(root, file))
                            logging.info('Added file to process {}'.format(file))
    return run_id_dict


def create_output_path(output_path, delete_existing_report):
    """This function creates any output folders that are needed for
    storing the graphs and final PDF report. If specified, it will also
    delete the existing report folder

    Args:
        output_path (str) - Path to the results folder for the comparison
        of these run-IDs
        delete_existing_report (bool) - Flag indicating whether any
        existing report folder should be deleted (True) or not (False)

    Returns:
        null
    """

    # "head" will be the full path to and including "cross_case_comparison"
    # "tail" will be just the name of the report folder
    head, tail = os.path.split(output_path)

    # TDH (2020-01-14)
    # If for some reason the parent folder that contains all the cross-
    # run-ID comparisons does not exist it needs to be created. If it
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
    # Now working on creating the folder specific to the run IDs being
    # compared.
    if os.path.exists(output_path):
        if delete_existing_report:
            shutil.rmtree(output_path)
    else:
        try:
            os.mkdir(output_path)
        except OSError:
            logging.error('Failed to create directory {}'.format(output_path))


def make_inter_run_graphs(meta_bmk_df,
                          run_id,
                          bm_list,
                          core_type,
                          output_path):
    """This function creates inter-run graphs of multiple benchmarks, for a
    given run_id.
    
    Args:
        meta_bmk_df (pandas dataframe): Full dataset.
        run_id (str): Specific run_id used to create this plot.
        bm_list (list): List of benchmarks to create inter-run graphs.
        core_type_list: Specific core_types used to create this plot.
        output_path (path): Location to send the graph.
    
    Returns:
        null
    """
    
    if 'echoBenchmark' in bm_list and 'timingBenchmark' in bm_list:
        df1 = meta_bmk_df[meta_bmk_df.benchmark == 'echoBenchmark']
        df2 = meta_bmk_df[meta_bmk_df.benchmark == 'timingBenchmark']
        if run_id in list(df1.run_id.unique()) and run_id in list(df2.run_id.unique()):
            if core_type in list(df1.core_type.unique()) and core_type in list(df2.core_type.unique()):
                bmk_plotting.plot_echo_vs_timing(df1, 
                                                 df2, 
                                                 run_id, 
                                                 core_type, 
                                                 output_path)
        else:
            pass
    if 'echoBenchmark' in bm_list and 'cEchoBenchmark' in bm_list:
        df1 = meta_bmk_df[meta_bmk_df.benchmark == 'echoBenchmark']
        df2 = meta_bmk_df[meta_bmk_df.benchmark == 'cEchoBenchmark']
        if run_id in list(df1.run_id.unique()) and run_id in list(df2.run_id.unique()):
            if core_type in list(df1.core_type.unique()) and core_type in list(df2.core_type.unique()):
                bmk_plotting.plot_echo_vs_echo_c(df1, 
                                                 df2, 
                                                 run_id, 
                                                 core_type, 
                                                 output_path)
        else:
            pass


def _auto_run(args):
    """This function executes when the script is called as a stand-alone
    executable. It is used both for development/testing as well as the
    primary executable for generating the standard analysis PDF report.

    A more complete description of this code can be found in the
    docstring at the beginning of this file.

    Args:
        '-r' or '--benchmark_results_dir' - Path of top-level folder
        that contains the benchmark results folders/files to be
        processed.
        
        '-l' or '--run_id_list' - Python list of run IDs to compare.
        
        '-b' or '--bm_list' - List of benchmarks for inter-run comparison
        plots.
        
        '-c' or '--core_type_list' - List of core_types for the graphs.

        '-d' or '--delete_all_reports' - "True" or "False" to indicate
        if existing reports should be over-written
    Returns:
        (nothing)
    """
    run_id_dict = find_specific_run_id(args.benchmark_results_dir,
                                       args.run_id_list)
    create_output_path(args.output_path, args.delete_report)
    file_list = []
    for run_id in run_id_dict:
        file_list.extend(run_id_dict[run_id]['files'])
    bm_files, bmk_files = sa.sort_results_files(file_list)
    file_list = bm_files
    json_results = bmpp.parse_files(file_list)
    json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    meta_bmk_df = md.make_dataframe(json_results)
    for run_id in args.run_id_list:
        print(run_id)
        for core_type in args.core_type_list:
            make_inter_run_graphs(meta_bmk_df,
                                  run_id,
                                  args.bm_list,
                                  core_type,
                                  args.output_path)
            birp.create_inter_run_id_report(args.output_path,
                                            json_results,
                                            run_id)


if __name__ == '__main__':
    # TDH: This slightly complex mess allows lower importance messages
    # to be sent to the log file and ERROR messages to additionally
    # be sent to the console as well. Thus, when bad things happen
    # the user will get an error message in both places which,
    # hopefully, will aid in trouble-shooting.
    fileHandle = logging.FileHandler("inter_run.log", mode='w')
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
    benchmark_results_dir = os.path.join(head,'benchmark_results')
    output_dir = os.path.join(head, 'inter_run_comparison')
    bm_list = ['echoBenchmark', 'cEchoBenchmark', 'timingBenchmark']
    core_type_list = ['singleCore', 'inproc', 'zmq', 'zmqss', 'ipc',
       'tcp', 'tcpss', 'udp']
    parser.add_argument('-r',
                        '--benchmark_results_dir',
                        nargs='?',
                        default=benchmark_results_dir)
    parser.add_argument('-l',
                        '--run_id_list',
                        nargs='+',
                        default=['bScQ6', 'Obg9g'])
    parser.add_argument('-b',
                        '--bm_list',
                        nargs='?',
                        default=bm_list)
    parser.add_argument('-c',
                        '--core_type_list',
                        nargs='?',
                        default=core_type_list)
    args = parser.parse_args()
    dir_name = 'inter_run_report'
#    for run_id in args.run_id_list:
#        dir_name = dir_name + str(run_id) + '_'
#        dir_name = dir_name + 'inter_run_report'

    default_output_path = os.path.join(output_dir,dir_name)
    parser.add_argument('-o',
                        '--output_path',
                        nargs='?',
                        default=default_output_path)
    parser.add_argument('-d',
                        '--delete_report',
                        nargs='?',
                        default=True)
    args = parser.parse_args()

    # TDH: Run the standard analysis
    _auto_run(args)