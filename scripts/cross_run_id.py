#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 15:00:00 2019

Performs an analysis comparing the results of the same benchmark results
across multiple run IDs.  It is assumed that the run IDs are chosen
because they are identical in most of the test conditions (found in the
the benchmark metadata and containing items such as mhz_per_cpu,
helics_version, system, etc) except for one of interest. For each
benchmark results that exists in both run IDs, graphs comparing the
performance in that benchmark are created. A single PDF is created from
all of these including a metadata header highlighting the difference in
test conditions (metadata) between the run IDs.

For some benchmarks, the dimensionality of the data is high enough when
comparing multiple run that what was a single graph in the standard
analysis becomes a series of graphs with one of the parameters held
constant for each graph. This is done to allow easier comparison between
the results from each run-ID.

The script handles more than two run IDs for comparison. A run-ID is
specified by the 5 character unique ID in the filename for every results
file associated with that run.

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
import cross_run_id_pdf as criPDF
import bmk_plotting
import make_dataframe as md
import standard_analysis as sa
import sys

# Installation of FPDF is: python -m pip install fpdf
# Installation of hvplot.pandas is: conda install -c pyviz hvplot
# Installation of selenium is: conda install -c bokeh selenium
# Installation of phantomjs is: brew tap homebrew/cask; brew cask install
# phantomjs

# Setting up logging
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

# TDH (2020-01-06): The hard-coded list below allows the metadata header
# to be generated programatically (instead of through a lot of copy and
# paste). These are the values are the literal strings of the parameter
# names in the results dictionarey (json_results) and dataframe. The
# header of the results PDF shows the values of each of these pieces of
# metdata associated with each run-ID.


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
                            logging.info(
                                'Added file to process {}'.format(file))
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


def find_common_bm_to_graph(json_results, run_id_dict):
    """This function builds a lists of benchmarks for each run ID to
    find matches for cross-run-ID comparison. Only those benchmarks that
    are common to all run-IDs should be compared.

    Args:
        json_results (dict) - Contains metadata and results
        keyed off the path for each benchmark results file.

        run_id_dict (dict) - Contains file metadata associated with
        each run ID

    Returns:
        bm_list_to_graph (list) - list of benchmarks common to all
        run-ids that, thus, should be graphed. Each list entry is a
        dictionary with the benchmark name and the benchmark type
        ("full" or "key")
    """
    bm_list_to_graph = []
    bm_dict = {}
    for run_id in run_id_dict.keys():
        bm_dict[run_id] = []
    for bm in json_results:
        bm_name = json_results[bm]['benchmark']
        # TDH (2020-01-14)
        # Don't need to look for comparisons between benchmarks that we
        # don't generate graphs
        if bm_name != 'actionMessageBenchmark' \
                and bm_name != 'conversionBenchmark':
            if json_results[bm]['benchmark_type'] == 'key':
                bm_name = bm_name + '_key'
            else:
                bm_name = bm_name + '_full'
            bm_dict[json_results[bm]['run_id']].append(bm_name)
    # TDH (2019-12-27): pick list of benchmarks in first list
    # arbitrarily as reference for comparison
    key = list(run_id_dict.keys())[0]
    for bm in bm_dict[key]:
        comparison_possible = True
        for run_id in bm_dict:
            # TDH (2020-01-14)
            # As soon as a benchmark is not found in the results for
            # any of the run IDs we know a comparison will not be possible
            # and can stop looking.
            if bm not in bm_dict[run_id]:
                comparison_possible = False
                break
        if comparison_possible:
            if bm[-4:] == 'full':
                bm_type = 'full'
            else:
                bm_type = 'key'
            # TDH (2020-01-14)
            # Extracting the base benchmark name for storage in the list
            bm_name_parts = bm.split('_')
            bm_name = bm_name_parts[0]
            bm_list_to_graph.append({'bm_name': bm_name, 'bm_type': bm_type})
    return bm_list_to_graph


def find_common_core_types(meta_bmk_df, run_id_list):
    """In order to compare multiple run-ids, there needs to be
    congruency among them.  This function asserts that the run-ids share
    common core types.  If there are only a subset of core types in
    common among the run-ids, this function returns that subset as a
    list to be used elsewhere.
    """
    core_types = []
    for run_id in run_id_list:
        c_set = set(meta_bmk_df[meta_bmk_df.run_id == '{}'.format(
            run_id)]['core_type'].unique())
        core_types.append(c_set)
    new_core_types = list(set.intersection(*core_types))
    return new_core_types


def make_cross_run_id_graphs(meta_bmk_df, bm_list, run_id_list, output_path,
                             comparison_parameter):
    """Based on the specified benchmark (bm), the appropriate graphing
    function is called. Since the graph is saved in the graphing function
    we need to pass in the output path. Rather than having a legend
    that uses the run-ID for text (which would be technically correct
    but practically less useful), the user passes in the parameter
    expected to be different across the run-IDs (comparison_parameter.

    It was found to be convenient to filter the full dataset prior to
    sending it to the graphing function to ensure only the intended data
    was being graphed.

    Args:
        meta_bmk_df (pandas dataframe) - Full dataset

        bm (string) - benchmark being compared

        run_id_list (list) - list of run-ID strings

        output_path (string) - path to where output graphs should be
        saved

        comparison_parameter - parameter of partiular interest that the
        user expects to differ across run-IDs.

    Returns:
        null
    """
    for bm in bm_list:
        logging.info('current benchmark {}'.format(bm['bm_name']))
        if bm['bm_name'] == 'echoBenchmark':
            df = meta_bmk_df[(meta_bmk_df.benchmark == 'echoBenchmark') &
                             (meta_bmk_df.benchmark_type == 'full')]
            core_types = find_common_core_types(df, run_id_list)
            for core_type in core_types:
                bmk_plotting.cr_plot(
                    df, 'federate_count', 'real_time', 'echoBenchmark',
                    run_id_list, core_type, comparison_parameter, output_path)
        if bm['bm_name'] == 'cEchoBenchmark':
            df = meta_bmk_df[(meta_bmk_df.benchmark == 'cEchoBenchmark') &
                             (meta_bmk_df.benchmark_type == 'full')]
            core_types = find_common_core_types(df, run_id_list)
            for core_type in core_types:
                bmk_plotting.cr_plot(
                    df, 'federate_count', 'real_time', 'cEchoBenchmark',
                    run_id_list, core_type, comparison_parameter, output_path)
        if bm['bm_name'] == 'echoMessageBenchmark':
            df = meta_bmk_df[
                (meta_bmk_df.benchmark == 'echoMessageBenchmark') &
                (meta_bmk_df.benchmark_type == 'full')]
            core_types = find_common_core_types(df, run_id_list)
            for core_type in core_types:
                bmk_plotting.cr_plot(
                    df, 'federate_count', 'real_time', 'echoMessageBenchmark',
                    run_id_list, core_type, comparison_parameter, output_path)
        if bm['bm_name'] == 'messageLookupBenchmark':
            df = meta_bmk_df[
                meta_bmk_df.benchmark == 'messageLookupBenchmark']
            ml1 = df[(df.benchmark_type == 'full') & (df.federate_count == 2)]
            ml2 = df[(df.benchmark_type == 'full') & (df.federate_count == 8)]
            ml3 = df[
                (df.benchmark_type == 'full') & (df.federate_count == 64)]
            bmk_plotting.cr_plot(
                ml1, 'interface_count', 'real_time',
                'messageLookup, fed_ct=2', run_id_list, 'inproc',
                comparison_parameter, output_path)
            bmk_plotting.cr_plot(
                ml2, 'interface_count', 'real_time', 'messageLookup, fed_ct=8',
                run_id_list, 'inproc', comparison_parameter, output_path)
            bmk_plotting.cr_plot(
                ml3, 'interface_count', 'real_time',
                'messageLookup, fed_ct=64', run_id_list, 'inproc',
                comparison_parameter, output_path)
        if bm['bm_name'] == 'ringBenchmark':
            # TDH (2020-01-09) - Special case because only a single data
            # point is run for the singleCore data. All the others have
            # multiple data points and can actually be used to form a
            # graph.
            df = meta_bmk_df[(meta_bmk_df.benchmark == 'ringBenchmark') &
                             (meta_bmk_df.benchmark_type == 'full') &
                             (meta_bmk_df.core_type != 'singleCore')]
            core_types = find_common_core_types(df, run_id_list)
            for core_type in core_types:
                bmk_plotting.cr_plot(
                    df, 'federate_count', 'real_time', 'ringBenchmark',
                    run_id_list, core_type, comparison_parameter, output_path)
        if bm['bm_name'] == 'ringMessageBenchmark':
            # TDH (2020-01-09) - Special case because only a single data
            # point is run for the singleCore data. All the others have
            # multiple data points and can actually be used to form a
            # graph.
            df = meta_bmk_df[
                (meta_bmk_df.benchmark == 'ringMessageBenchmark') &
                (meta_bmk_df.benchmark_type == 'full') &
                (meta_bmk_df.core_type != 'singleCore')]
            core_types = find_common_core_types(df, run_id_list)
            for core_type in core_types:
                bmk_plotting.cr_plot(
                    df, 'federate_count', 'real_time', 'ringMessageBenchmark',
                    run_id_list, core_type, comparison_parameter, output_path)
        if bm['bm_name'] == 'pholdBenchmark':
            df = meta_bmk_df[(meta_bmk_df.benchmark == 'pholdBenchmark') &
                             (meta_bmk_df.benchmark_type == 'full')]
            core_types = find_common_core_types(df, run_id_list)
            for core_type in core_types:
                bmk_plotting.cr_plot(
                    meta_bmk_df, 'federate_count', 'real_time',
                    'pholdBenchmark', run_id_list, core_type,
                    comparison_parameter, output_path)
        if bm['bm_name'] == 'messageSendBenchmark':
            df = meta_bmk_df[
                (meta_bmk_df.benchmark == 'messageSendBenchmark') &
                (meta_bmk_df.benchmark_type == 'full')]
            bmk_plotting.cr_plot(
                df, 'message_size', 'real_time', 'messageSend, singleCore',
                run_id_list, 'singleCore', comparison_parameter, output_path)
            core_types = find_common_core_types(df, run_id_list)
            for core_type in core_types:
                ms1 = df[df.message_count == 1]
                ms2 = df[df.message_size == 1]
                bmk_plotting.cr_plot(
                    ms1, 'message_size', 'real_time', 'messageSend, msg_ct=1',
                    run_id_list, core_type, comparison_parameter, output_path)
                bmk_plotting.cr_plot(
                    ms2, 'message_count', 'real_time', 'messageSend, msg_sz=1',
                    run_id_list, core_type, comparison_parameter, output_path)
        if bm['bm_name'] == 'filterBenchmark':
            df = meta_bmk_df[(meta_bmk_df.benchmark == 'filterBenchmark') &
                             (meta_bmk_df.benchmark_type == 'full')]
            bmk_plotting.cr_plot(
                df, 'federate_count', 'real_time', 'filter, singleCore',
                run_id_list, 'singleCore', comparison_parameter, output_path)
            core_types = find_common_core_types(df, run_id_list)
            core_types = [c for c in core_types if c != 'ipc']
            dest = df[df.filter_location == 'destination']
            src = df[df.filter_location == 'source']
            for core_type in core_types:
                bmk_plotting.cr_plot(
                    src, 'federate_count', 'real_time',
                    'filter, fltr_loc=source', run_id_list, core_type,
                    comparison_parameter, output_path)
                bmk_plotting.cr_plot(
                    dest, 'federate_count', 'real_time',
                    'filter, fltr_loc=dest', run_id_list, core_type,
                    comparison_parameter, output_path)
        if bm['bm_name'] == 'timingBenchmark':
            df = meta_bmk_df[(meta_bmk_df.benchmark == 'timingBenchmark') &
                             (meta_bmk_df.benchmark_type == 'full')]
            core_types = find_common_core_types(df, run_id_list)
            for core_type in core_types:
                bmk_plotting.cr_plot(
                    meta_bmk_df, 'federate_count', 'real_time',
                    'timingBenchmark', run_id_list, core_type,
                    comparison_parameter, output_path)


def _auto_run(args):
    """This function executes when the script is called as a stand-alone
    executable. It is used both for development/testing as well as the
    primary executable for generating the cross-run-ID comparison
     PDF report.

    A more complete description of this code can be found in the
    docstring at the beginning of this file.

    Args:
        '-r' or '--benchmark_results_dir' - Path of top-level folder
        that contains the benchmark results folders/files to be
        processed.

        '-l' or '--run_id_list' - Python list of run IDs to compare

        '-p' or '--comparison_parameter_list' - Particular parameter list that
        we are interested in using for comparisons

        '-o' or '--output_path' - Path to location where output will be
        written

        '-d' or '--delete_all_reports' - "True" or "False" to indicate
        if existing reports should be over-written
    Returns:
        (nothing)
    """
    logging.info('starting the execution of this script...')
    logging.info('finding the specific run_id...\n')
    run_id_dict = find_specific_run_id(
        args.benchmark_results_dir, args.run_id_list)
    file_list = []
    logging.info('preparing the data')
    for run_id in run_id_dict:
        file_list.extend(run_id_dict[run_id]['files'])
    bm_files, bmk_files = sa.sort_results_files(file_list)
    file_list = bm_files
    json_results = bmpp.parse_files(file_list)
    json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    meta_bmk_df = md.make_dataframe1(json_results)
    bm_list = find_common_bm_to_graph(json_results, run_id_dict)
    valid_params = []
    logging.info('checking to see which parameters are valid...\n')
    for p in args.comparison_parameter_list:
        header, diff = criPDF.grab_header_metadata(
            json_results,
            criPDF.get_run_id_keys(json_results, args.run_id_list),
            p)
        if diff is True:
            valid_params.append(p)
    path = os.path.join(args.output_path)
    for v in valid_params:
        output_path = os.path.join(path, '{}'.format(v))
        create_output_path(output_path, args.delete_report)
        make_cross_run_id_graphs(
            meta_bmk_df, bm_list, list(run_id_dict.keys()), output_path, v)
        criPDF.create_cross_run_id_report(
            json_results, list(run_id_dict.keys()),
            output_path, parameter_list)
    logging.info('Finished the cross-run_id analysis for {}.'.format(
        args.run_id_list))


if __name__ == '__main__':
    # TDH: This slightly complex mess allows lower importance messages
    # to be sent to the log file and ERROR messages to additionally
    # be sent to the console as well. Thus, when bad things happen
    # the user will get an error message in both places which,
    # hopefully, will aid in trouble-shooting.
    fileHandle = logging.FileHandler("cross_run_id.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])
    parser = argparse.ArgumentParser(description='Cross case comparison')
    # TDH: Have to do a little bit of work to generate a good default
    # path for the results folder. Default only works if being run
    # from the "scripts" directory in the repository structure.
    # Also used to define the default location for the output folder
    script_path = os.path.dirname(os.path.realpath(__file__))
    head, tail = os.path.split(script_path)
    benchmark_results_dir = os.path.join(head, 'benchmark_results')
    output_dir = os.path.join(head, 'cross_case_comparison')
    parser.add_argument('-r',
                        '--benchmark_results_dir',
                        nargs='?',
                        default=benchmark_results_dir)
    parser.add_argument('-l',
                        '--run_id_list',
                        nargs='+',
                        default=['Md3vp', 'p8BJW'])
    parameter_list = [
        'mhz_per_cpu', 'helics_version', 'generator',
        'system', 'system_version', 'platform',
        'cxx_compiler', 'cxx_compiler_version', 'build_flags_string',
        'host_name', 'host_processor', 'num_cpus',
        'date', 'library_build_type']
    parser.add_argument('-p',
                        '--comparison_parameter_list',
                        nargs='?',
                        default=parameter_list)
    # TDH (2019-12-27)
    # Building the output results directory name based on the run IDs
    # specified
    args = parser.parse_args()
    d_name = ''
    for run_id in args.run_id_list:
        d_name = d_name + str(run_id) + '_'
    dir_name = d_name + 'report'
    default_output_path = os.path.join(output_dir, dir_name)
    parser.add_argument('-o',
                        '--output_path',
                        nargs='?',
                        default=default_output_path)

    parser.add_argument('-d',
                        '--delete_report',
                        nargs='?',
                        default=False)
    args = parser.parse_args()
    _auto_run(args)
