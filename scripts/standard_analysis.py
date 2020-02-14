#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 15:00:00 2019

Performs standard analysis for all runs in a given path (searches
directory tree for runs). For each standard analysis a graph file for
each benchmark is created. A single PDF is created from all of these
including a metadata header culled from the benchmark results files.

The data from these results files exists in few forms:
    - benchmark results files that are largely JSON formatted with a
    metadata header
    - "json_results" dictionary which is a parsed version of the JSON
    file with the associated metadata.
    - "meta_bmk_df" pandas dataframe which is largely a reformatted
    version of the JSON into a strcuture more readily handled by
    the holoview graphing utility

This script can be run as a standalone script to generate the standard
analysis for every run in the user-provided path. By default it will not
overwrite any existing report. A "run" is specified by the 5 character
unique ID in the filename for every results file associated with that
run.

The command line arguments for the function can be found in the code
following the lines following the "if __name__ == '__main__':" line
at the end of this file.

@author: hard312
"""

import argparse
import logging
import pprint
import os
import shutil
import benchmark_postprocessing as bmpp
import standard_analysis_pdf as saPDF
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

def find_runs(benchmark_results_dir):
    """This function finds all runs and their associated results files
    paths that need standard analysis reports generated.

    This function assumes that files for a run-ID are only found in a
    single folder.

    Args:
        benchmark_results_dir (str) - Path of top-level folder that
        contains the benchmark results folders/files to be processed.

    Returns:
        run_id_dict (dict) - The dictionary keyed off the 5 character
        run-ID and contains the following elements:
            - "files" - list of files found for this run-ID.
            - "report_exists" - True/False indicating whether a report
            exists for this run-ID
            - "bm_data_path" - path to the folder containing the results
            files
    """
    run_id_dict = {}
    # TDH (2019-20-23): Find the unique run IDs. These are the key
    # values that will determine what standard reports to generate and
    # which can be skipped (because they already exist).
    for root, dirs, files in os.walk(benchmark_results_dir):
        for file in files:
            # If the root ends in 'report' than we are in a report
            # directory and don't need to do much.
            if root[-6:] != 'report':
                # TDH (2019-12-26):  Assume only files ending in
                # '.txt' are the results files. Files in the reports
                # folders should all end in '.png' or '.pdf'
                head, tail = os.path.splitext(file)
                if tail == '.txt':
                    # TDH (2019-12-23): Assuming that the files are
                    # always named such that the run id is the last five
                    # characters before the ".txt"...
                    run_id = file[-9:-4]
                    if run_id not in run_id_dict:
                        run_id_dict[run_id] = {}
                        run_id_dict[run_id]['files'] = []

                        # Checking to see if a report folder exists and
                        # adding it to the metadata
                        report_dir_name = run_id + '_report'
                        if report_dir_name in dirs:
                            run_id_dict[run_id]['report_exists'] = True
                        else:
                            run_id_dict[run_id]['report_exists'] = False
                    # TDH: Only need to define the path to the results
                    # files once for each run-ID.
                    if 'bm_data_path' not in run_id_dict[run_id].keys():
                        run_id_dict[run_id]['bm_data_path'] = root
                    if file not in run_id_dict[run_id]['files']:
                        run_id_dict[run_id]['files'].append(
                            os.path.join(root,file))
    return run_id_dict


def remove_all_reports(run_id_dict):
    """This function removes from the file system all report folders. It
    is called when the user specifies that all existing reports should
    be deleted using the command-line argument. This would normally be
    done if a change is made to the data processing and/or
    presentation such that the old reports would be invalidated

    Args:
        run_id_dict (dict) - Dictionary containing metadata for each
        run-ID including whether a report exists and the path to the
        report

    Returns:
        run_id_dict (dict) - Unmodified from version passed in
    """
    for key in run_id_dict:
        if run_id_dict[key]['report_exists']:
            shutil.rmtree(run_id_dict[key]['report_path'])
            run_id_dict[key]['report_exists'] = False
            logger.info('Removed report directory {}'.format(
                run_id_dict[key]['report_path']))
    return run_id_dict


def add_report_path(run_id_dict):
    """This function adds the path (as a string) to the report folder
    for all run-IDs in the run_id_dict as an element named "report_path"

    Args:
        run_id_dict (dict) - Dictionary containing metadata for each
        run-ID including the path to the benchmark data files. This is
        the location where the standard analysis report is added.

    Returns:
        run_id_dict (dict) - Modifed to include element "report_path"
    """
    for key in run_id_dict:
        report_dir_name = key + '_report'
        report_path = os.path.join(
            run_id_dict[key]['bm_data_path'],report_dir_name)
        run_id_dict[key]['report_path'] = report_path
    return run_id_dict


def find_bm_to_graph(json_results, run_id):
    """This function generates a list of all the benchmarks associated
    with a run-ID.

    Args:
        json_results (dict) - Dictionary containing metadata and results
        keyed off the path for each benchmark results file.
        run_id (str) - specific run-ID to evaluate

    Returns:
        bm_list_to_graph (list) - List of two element dictionaries for
        all benchmarks that specify the name and the benchmark type
        ("full" or "key").
    """
    bm_list_to_graph = []
    for bm in json_results:
        if json_results[bm]['run_id'] == run_id:
            bm_name = json_results[bm]['benchmark']
            if bm_name != 'actionMessageBenchmark' and \
                    bm_name != 'conversionBenchmark':
                if json_results[bm]['benchmark_type'] == 'key':
                    bm_type = 'key'
                else:
                    bm_type = 'full'
                bm_list_to_graph.append(
                    {'bm_name': bm_name, 'bm_type':bm_type})
    return bm_list_to_graph


def make_SA_graphs(meta_bmk_df, bm, run_id, output_path):
    """This function determines which graphing function to call (based
    on the name of the benchmark passed in "bm") and whether it should
    be graphed (based on the benchmark type, "full" or "key").

    Args:
        meta_bmk_df (pandas dataframe) - Contains all benchmark results
        and associated metadata.
        bm (dict) - small dictionary storing the benchmark name and type
        ("full" or "key")
        run_id (str) - 5 character unique identifier for the run-ID
        output_path (str) - Path where graphs should be saved

    Returns:
        (nothing)
    """
    if bm['bm_name'] == 'echoBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'echoBenchmark']
        if bm['bm_type'] == 'full':
            meta_bmk_df = meta_bmk_df[(meta_bmk_df.benchmark_type == 'full') &
                                      (meta_bmk_df.run_id == '{}'.format(run_id))]
            x_axis = 'federate_count'
            y_axis = 'real_time'
            bm_name = 'echoBenchmark'
            by_bool = True
            by_name = 'core_type'
            bmk_plotting.sa_plot(meta_bmk_df, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
        else:
            pass
    if bm['bm_name'] == 'cEchoBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'cEchoBenchmark']
        if bm['bm_type'] == 'full':
            meta_bmk_df = meta_bmk_df[(meta_bmk_df.benchmark_type == 'full') &
                                      (meta_bmk_df.run_id == '{}'.format(run_id))]
            x_axis = 'federate_count'
            y_axis = 'real_time'
            bm_name = 'cEchoBenchmark'
            by_bool = True
            by_name = 'core_type'
            bmk_plotting.sa_plot(meta_bmk_df, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
        else:
            pass
    if bm['bm_name'] == 'echoMessageBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'echoMessageBenchmark']
        if bm['bm_type'] == 'full':
            meta_bmk_df = meta_bmk_df[(meta_bmk_df.benchmark_type == 'full') &
                                      (meta_bmk_df.run_id == '{}'.format(run_id))]
            x_axis = 'federate_count'
            y_axis = 'real_time'
            bm_name = 'echoMessageBenchmark'
            by_bool = True
            by_name = 'core_type'
            bmk_plotting.sa_plot(meta_bmk_df, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
        else:
            pass
    if bm['bm_name'] == 'messageLookupBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'messageLookupBenchmark']
        if bm['bm_type'] == 'full':
            ml_1 = meta_bmk_df[(meta_bmk_df.core_type == 'inproc') &
                               (meta_bmk_df.benchmark_type == 'full') & 
                               (meta_bmk_df.run_id == '{}'.format(run_id)) &
                               (meta_bmk_df.federate_count == 2)]
            x_axis = 'interface_count'
            y_axis = 'real_time'
            bm_name = 'messageLookup, core_type=inproc, fed_ct=2'
            by_bool = False
            by_name = ''
            bmk_plotting.sa_plot(ml_1, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
            ml_2 = meta_bmk_df[(meta_bmk_df.core_type == 'inproc') &
                               (meta_bmk_df.benchmark_type == 'full') & 
                               (meta_bmk_df.run_id == '{}'.format(run_id)) &
                               (meta_bmk_df.federate_count == 8)]
            x_axis = 'interface_count'
            y_axis = 'real_time'
            bm_name = 'messageLookup, core_type=inproc, fed_ct=8'
            by_bool = False
            by_name = ''
            bmk_plotting.sa_plot(ml_2, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
            ml_3 = meta_bmk_df[(meta_bmk_df.core_type == 'inproc') &
                               (meta_bmk_df.benchmark_type == 'full') & 
                               (meta_bmk_df.run_id == '{}'.format(run_id)) &
                               (meta_bmk_df.federate_count == 64)]
            x_axis = 'interface_count'
            y_axis = 'real_time'
            bm_name = 'messageLookup, core_type=inproc, fed_ct=64'
            by_bool = False
            by_name = ''
            bmk_plotting.sa_plot(ml_3, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
        else:
            pass
    if bm['bm_name'] == 'ringBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'ringBenchmark']
        if bm['bm_type'] == 'full':
            meta_bmk_df = meta_bmk_df[(meta_bmk_df.benchmark_type == 'full') &
                                      (meta_bmk_df.run_id == '{}'.format(run_id))]
            x_axis = 'federate_count'
            y_axis = 'real_time'
            bm_name = 'ringBenchmark'
            by_bool = True
            by_name = 'core_type'
            bmk_plotting.sa_plot(meta_bmk_df, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
        else:
            pass
    if bm['bm_name'] == 'pholdBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'pholdBenchmark']
        if bm['bm_type'] == 'full':
            meta_bmk_df = meta_bmk_df[(meta_bmk_df.benchmark_type == 'full') &
                                      (meta_bmk_df.run_id == '{}'.format(run_id))]
            x_axis = 'federate_count'
            y_axis = 'real_time'
            bm_name = 'pholdBenchmark'
            by_bool = True
            by_name = 'core_type'
            bmk_plotting.sa_plot(meta_bmk_df, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
        else:
            pass
    if bm['bm_name'] == 'messageSendBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'messageSendBenchmark']
        if bm['bm_type'] == 'full':
            ms_1 = meta_bmk_df[(meta_bmk_df.core_type == 'singleCore') &
                               (meta_bmk_df.benchmark_type == 'full') &
                               (meta_bmk_df.run_id == '{}'.format(run_id))]
            x_axis = 'message_size'
            y_axis = 'real_time'
            bm_name = 'messageSend, core_type=singleCore'
            by_bool = False
            by_name = ''
            bmk_plotting.sa_plot(ms_1, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
            ms_2 = meta_bmk_df[(meta_bmk_df.benchmark_type == 'full') &
                               (meta_bmk_df.run_id == '{}'.format(run_id)) & 
                               (meta_bmk_df.message_count == 1)]
            x_axis = 'message_size'
            y_axis = 'real_time'
            bm_name = 'messageSend, msg_ct=1'
            by_bool = True
            by_name = 'core_type'
            bmk_plotting.sa_plot(ms_2, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
            ms_3 = meta_bmk_df[(meta_bmk_df.benchmark_type == 'full') &
                               (meta_bmk_df.run_id == '{}'.format(run_id)) & 
                               (meta_bmk_df.message_size == 1)]
            x_axis = 'message_count'
            y_axis = 'real_time'
            bm_name = 'messageSend, msg_sz=1'
            by_bool = True
            by_name = 'core_type'
            bmk_plotting.sa_plot(ms_3, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
        else:
            pass
    if bm['bm_name'] == 'filterBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'filterBenchmark']
        if bm['bm_type'] == 'full':
            f = meta_bmk_df[(meta_bmk_df.core_type == 'singleCore') &
                            (meta_bmk_df.benchmark_type == 'full') &
                            (meta_bmk_df.run_id == '{}'.format(run_id))]
            x_axis = 'federate_count'
            y_axis = 'real_time'
            bm_name = 'filterBenchmark, core_type=singleCore'
            by_bool = True
            by_name = 'filter_location'
            bmk_plotting.sa_plot(f, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
            source = meta_bmk_df[(meta_bmk_df.filter_location == 'source') &
                                 (meta_bmk_df.benchmark_type == 'full') &
                                 (meta_bmk_df.run_id == '{}'.format(run_id))]
            x_axis = 'federate_count'
            y_axis = 'real_time'
            bm_name = 'filterBenchmark, filter_loc=source'
            by_bool = True
            by_name = 'core_type'
            bmk_plotting.sa_plot(source, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
            dest = meta_bmk_df[(meta_bmk_df.filter_location == 'destination') &
                               (meta_bmk_df.benchmark_type == 'full') &
                               (meta_bmk_df.run_id == '{}'.format(run_id))]
            x_axis = 'federate_count'
            y_axis = 'real_time'
            bm_name = 'filterBenchmark, filter_loc=destination'
            by_bool = True
            by_name = 'core_type'
            bmk_plotting.sa_plot(dest, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
        else:
            pass
    if bm['bm_name'] == 'timingBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'timingBenchmark']
        if bm['bm_type'] == 'full':
            meta_bmk_df = meta_bmk_df[(meta_bmk_df.benchmark_type == 'full') &
                                      (meta_bmk_df.run_id == '{}'.format(run_id))]
            x_axis = 'federate_count'
            y_axis = 'real_time'
            bm_name = 'timingBenchmark'
            by_bool = True
            by_name = 'core_type'
            bmk_plotting.sa_plot(meta_bmk_df, 
                                 x_axis,
                                 y_axis,
                                 bm_name,
                                 'full',
                                 by_bool,
                                 by_name,
                                 run_id, 
                                 output_path)
        else:
            pass


def sort_results_files(file_list):
    """This function classifies the benchmarks as being "key" or "full"

    Args:
        file_list (list) - List of full paths to individual benchmark
        results files

    Returns:
        bm_files (list) - List of full paths to benchmark files that are
        classified as "full"
        bmk_files (list) - List of full paths to benchmark files that
        are classified as "key"
    """
    bm_files = []
    bmk_files = []
    for file in file_list:
        head, tail = os.path.split(file)
        # TDH (2020-01-08) just need to check to see if file starts out
        # as "bm" or "bmk"
        if tail[0:3] == 'bmk':
            bmk_files.append(file)
        elif tail[0:2] == 'bm':
            bm_files.append(file)
        else:
            logging.error('File {} does not begin with "bm" or "bmk, '
                          'cannot be classified, and will be ignored'.format(file))
    return bm_files, bmk_files

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

        '-d' or '--delete_all_reports' - "True" or "False" to indicate
        if existing reports should be over-written
    Returns:
        (nothing)
    """
    run_id_dict = find_runs(args.benchmark_results_dir)
    run_id_dict = add_report_path(run_id_dict)
    if args.delete_all_reports:
        run_id_dict = remove_all_reports(run_id_dict)
    for run_id in run_id_dict:
        if run_id_dict[run_id]['report_exists'] == False:
            # TDH: For the standard analysis we only need to process the
            # "full" benchmark results files.
            bm_files, bmk_files = sort_results_files(
                run_id_dict[run_id]['files'])
            file_list = bm_files
            json_results = bmpp.parse_files(file_list)
            json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
            meta_bmk_df = md.make_dataframe1(json_results)
            for run_id in meta_bmk_df.run_id.unique():
                bm_list = find_bm_to_graph(json_results, run_id)
                # TDH: Thorough attempt to safely create the results
                # directory and provide good error reporting if
                # something went wrong.
                try:
                    os.mkdir(run_id_dict[run_id]['report_path'])
                except OSError:
                    logging.error(
                        'Failed to create directory for report at {}'.format(
                            run_id_dict[run_id]['report_path']))
                for bm in bm_list:
                    make_SA_graphs(meta_bmk_df,
                                   bm,
                                   run_id,
                                   run_id_dict[run_id]['report_path'])
                saPDF.create_standard_analysis_report(
                    run_id_dict[run_id]['report_path'],
                    json_results,
                    run_id)



if __name__ == '__main__':
    # TDH: This slightly complex mess allows lower importance messages
    # to be sent to the log file and ERROR messages to additionally
    # be sent to the console as well. Thus, when bad things happen
    # the user will get an error message in both places which,
    # hopefully, will aid in trouble-shooting.
    fileHandle = logging.FileHandler("standard_analysis.log", mode='w')
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
    parser.add_argument('-r',
                        '--benchmark_results_dir',
                        nargs='?',
                        default=benchmark_results_dir)
    parser.add_argument('-d',
                        '--delete_all_reports',
                        nargs='?',
                        default=True)
    args = parser.parse_args()

    # TDH: Run the standard analysis
    _auto_run(args)