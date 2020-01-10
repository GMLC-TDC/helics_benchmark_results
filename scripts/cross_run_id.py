#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 15:00:00 2019

Performs cross-run-id analysis for user-provided run-ids.

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
import holoviews as hv
import math

# Installation of FPDF is: python -m pip install fpdf
# Installation of hvplot.pandas is: conda install -c pyviz hvplot
# Installation of selenium is: conda install -c bokeh selenium
# Installation of phantomjs is: brew tap homebrew/cask; brew cask install phantomjs

# Setting up logging
logger = logging.getLogger(__name__)



# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

# TDH (2020-01-06): The hard-coded list below allows the metadata header to be generated programatically (instead
#   of through a lot of copy and paste).
parameter_list = [
    'date',
    'helics_version',
    'generator',
    'system',
    'system_version',
    'platform',
    'cxx_compiler',
    'cxx_compiler_version',
    'build_flags_string',
    'host_name',
    'host_processor',
    'num_cpus',
    'mhz_per_cpu'
]


def find_specific_run_id(benchmark_results_dir, run_id_list):
    run_id_dict = {}
    for root, dirs, files in os.walk(benchmark_results_dir):
        for file in files:
            # If the root ends in 'report' than we are in a report directory and don't need to do much.
            if root[-6:] != 'report':
                # TDH (2019-12-26):  Assume only files ending in '.txt' are the results files.
                #   Files in the reports folders should all end in '.png' or '.pdf'
                head, tail = os.path.splitext(file)
                if tail == '.txt':
                    # TDH (2019-12-23): Assuming that the files are always named such that the run id is the last
                    #   five characters before the ".txt"...
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
    # "head" will be the full path to and including "cross_case_comparison"
    # "tail" will be just the name of the report
    head, tail = os.path.split(output_path)
    if os.path.exists(head):
        pass
    else:
        try:
            os.mkdir(head)
        except OSError:
            logging.error('Failed to create directory {}'.format(head))
            print('Failed to create directory {}'.format(head))
    if os.path.exists(output_path):
        if delete_existing_report:
            shutil.rmtree(args.output_path)
    else:
        try:
            os.mkdir(output_path)
        except OSError:
            logging.error('Failed to create directory {}'.format(output_path))


def find_common_bm_to_graph(json_results, run_id_dict):
    bm_list_to_graph = []
    # TDH (2019-12-27): Building lists of benchmarks for each run ID to find matches for cross-run-ID comparison
    bm_dict = {}
    for run_id in run_id_dict.keys():
        bm_dict[run_id] = []
    for bm in json_results:
        bm_name = json_results[bm]['benchmark']
        if bm_name != 'actionMessageBenchmark' and bm_name != 'conversionBenchmark':
            if json_results[bm]['benchmark_type'] == 'key':
                bm_name = bm_name + '_key'
            else:
                bm_name = bm_name + '_full'
            bm_dict[json_results[bm]['run_id']].append(bm_name)
    # TDH (2019-12-27): pick list of benchmarks in first list arbitrarily as reference for comparison
    key = list(run_id_dict.keys())[0]
    for bm in bm_dict[key]:
        comparison_possible = True
        for run_id in bm_dict:
            if bm not in bm_dict[run_id]:
                comparison_possible = False
                break
        if comparison_possible:
            if bm[-4:] == 'full':
                bm_type = 'full'
            else:
                bm_type = 'key'
            bm_name_parts = bm.split('_')
            bm_name = bm_name_parts[0]
            bm_list_to_graph.append({'bm_name': bm_name, 'bm_type':bm_type})
    return bm_list_to_graph

def make_cross_run_id_graphs(meta_bmk_df, bm, run_id_list, output_path, comparison_parameter):
    # TDH note to Corinne:
    # All of these calls to your bmk_plotting need new versions that appropriately handle multiple run IDs
    #   as specified in the run_id_list. That is, you'll need to create a plot_echo_results_cross_run_ID that makes
    #   one or more graphs. I've commented out the calls and added the "pass" just so the code doesn't crash when run.

    if bm == 'echoBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'echoBenchmark']
        for core_type in meta_bmk_df.core_type.unique():
            bmk_plotting.plot_echo_result_cr(meta_bmk_df, run_id_list, core_type, output_path, comparison_parameter)
    if bm == 'echoMessageBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'echoMessageBenchmark']
        for core_type in meta_bmk_df.core_type.unique():
            bmk_plotting.plot_echo_msg_cr(meta_bmk_df, run_id_list, core_type, output_path, comparison_parameter)
    if bm == 'messageLookupBenchmark':
        # TDH (2020-01-07): Extra work for this one as we want to iterate over only the federate_count values that are
        # in the messageLookupBenchmark
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'messageLookupBenchmark']
        fed_list = [i for i in meta_bmk_df.federate_count]
        fed_list = [x for x in fed_list if not math.isnan(x)]
        fed_list = list(set(fed_list))
        for federate_count in fed_list:
            #bmk_plotting.plot_msg_lookup_cr(meta_bmk_df, run_id_list, federate_count, output_path, comparison_parameter)
            pass
    if bm == 'ringBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'ringBenchmark']
        for core_type in meta_bmk_df.core_type.unique():
            # TDH (2020-01-09) - Special case because only a single data point is run for the singleCore data. All
            # the others have multiple data points and can actually be used to form a graph.
            if core_type != 'singleCore':
                bmk_plotting.plot_ring_cr(meta_bmk_df, run_id_list, core_type, output_path, comparison_parameter)
    if bm == 'pholdBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'pholdBenchmark']
        for core_type in meta_bmk_df.core_type.unique():
            bmk_plotting.plot_phold_cr(meta_bmk_df, run_id_list, core_type, output_path, comparison_parameter)
    if bm == 'messageSendBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'messageSendBenchmark']
        bmk_plotting.plot_msg_send_1_cr(meta_bmk_df, run_id_list, output_path, comparison_parameter)
        for core_type in meta_bmk_df.core_type.unique():
            bmk_plotting.plot_msg_send_2_cr(meta_bmk_df, run_id_list, core_type, output_path, comparison_parameter)
            bmk_plotting.plot_msg_send_3_cr(meta_bmk_df, run_id_list, core_type, output_path, comparison_parameter)
    if bm == 'filterBenchmark':
        meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'filterBenchmark']
        bmk_plotting.plot_filter_cr(meta_bmk_df, run_id_list, output_path, comparison_parameter)
        for core_type in meta_bmk_df.core_type.unique():
            bmk_plotting.plot_src_cr(meta_bmk_df, run_id_list, core_type, output_path, comparison_parameter)
            bmk_plotting.plot_dest_cr(meta_bmk_df, run_id_list, core_type, output_path, comparison_parameter)


def _auto_run(args):
    # TDH (2020-01-07) For now, I'm going to hard-code the parameter of interest that we will be comparing across
    # run IDs.
    comparison_parameter = 'mhz_per_cpu'
    run_id_dict = find_specific_run_id(args.benchmark_results_dir, args.run_id_list)
    create_output_path(args.output_path, args.delete_report)
    file_list = []
    for run_id in run_id_dict:
        file_list.extend(run_id_dict[run_id]['files'])
    bm_files, bmk_files = sa.sort_results_files(file_list)
    file_list = bm_files
    json_results = bmpp.parse_files(file_list)
    json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    meta_bmk_df = md.make_dataframe(json_results)
    bm_list = find_common_bm_to_graph(json_results, run_id_dict)
    for bm in bm_list:
        make_cross_run_id_graphs(meta_bmk_df, bm['bm_name'], list(run_id_dict.keys()), args.output_path, comparison_parameter)
    criPDF.create_cross_run_id_report(json_results, list(run_id_dict.keys()), args.output_path, parameter_list)




if __name__ == '__main__':
    fileHandle = logging.FileHandler("cross_run_id.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])
    parser = argparse.ArgumentParser(description='Cross case comparison.')
    script_path = os.path.dirname(os.path.realpath(__file__))
    head, tail = os.path.split(script_path)
    benchmark_results_dir = os.path.join(head,'benchmark_results')
    parser.add_argument('-r',
                        '--benchmark_results_dir',
                        nargs='?',
                        default=benchmark_results_dir)
    parser.add_argument('-l',
                        '--run_id_list',
                        nargs='+',
                        default=['aUZF6', 'Zu60n'])


    # TDH (2019-12-27): Building the output results directory name based on the run IDs specified
    args = parser.parse_args()
    dir_name = ''
    for run_id in args.run_id_list:
        dir_name = dir_name + str(run_id) + '_'
    dir_name = dir_name + 'report'

    # Finding current location of this Python script to build output directory path
    #   Assumes that the entire repository structure is in place.
    output_dir = os.path.join(head, 'cross_case_comparison')

    # Finally, we can assemble the full output path
    default_output_path = os.path.join(output_dir,dir_name)
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