#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 15:00:00 2019

Performs standard analysis for all runs in a given path (searches directory tree for runs)

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

# Setting up logging
logger = logging.getLogger(__name__)



# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

def find_runs(benchmark_results_dir):
    run_id_dict = {}
    # TDH (2019-20-23): Find the unique run IDs. These are the key values that will determine what standard reports
    #   to generate and which can be skipped (because they already exist).
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
                    if run_id not in run_id_dict:
                        run_id_dict[run_id] = {}
                        run_id_dict[run_id]['files'] = []

                        # Checking to see if a report folder exists
                        report_dir_name = run_id + '_report'
                        if report_dir_name in dirs:
                            run_id_dict[run_id]['report_exists'] = True
                        else:
                            run_id_dict[run_id]['report_exists'] = False
                    if 'bm_data_path' not in run_id_dict[run_id].keys():
                        run_id_dict[run_id]['bm_data_path'] = root
                    if file not in run_id_dict[run_id]['files']:
                        run_id_dict[run_id]['files'].append(os.path.join(root,file))

    return run_id_dict


def remove_all_reports(run_id_dict):
    for key in run_id_dict:
        if run_id_dict[key]['report_exists']:
            shutil.rmtree(run_id_dict[key]['report_path'])
            run_id_dict[key]['report_exists'] = False
            logger.info('Removed report directory {}'.format(run_id_dict[key]['report_path']))
    return run_id_dict


def find_bm_to_graph(json_results, run_id):
    bm_list_to_graph = []
    for bm in json_results:
        if json_results[bm]['run_id'] == run_id:
            bm_name = json_results[bm]['benchmark']
            if bm_name != 'actionMessageBenchmark' and bm_name != 'conversionBenchmark':
                bm_list_to_graph.append(bm_name)
            pass
    return bm_list_to_graph

def make_SA_graphs(meta_bmk_df, bm, run_id, output_path):
    if bm == 'echoBenchmark':
        bmk_plotting.plot_echo_result(meta_bmk_df, run_id, output_path)
    if bm == 'echoMessageBenchmark':
        bmk_plotting.plot_echo_msg(meta_bmk_df, run_id, output_path)
    if bm == 'messageLookupBenchmark':
        bmk_plotting.plot_msg_lookup(meta_bmk_df, run_id, output_path)
    if bm == 'ringBenchmark':
        bmk_plotting.plot_ring(meta_bmk_df, run_id, output_path)
    if bm == 'pholdBenchmark':
        bmk_plotting.plot_phold(meta_bmk_df, run_id, output_path)
    if bm == 'messageSendBenchmark':
        bmk_plotting.plot_msg_send_1(meta_bmk_df, run_id, output_path)
        bmk_plotting.plot_msg_send_2(meta_bmk_df, run_id, output_path)
        bmk_plotting.plot_msg_send_3(meta_bmk_df, run_id, output_path)
    if bm == 'filterBenchmark':
        bmk_plotting.plot_filter(meta_bmk_df, run_id, output_path)
        bmk_plotting.plot_src(meta_bmk_df, run_id, output_path)
        bmk_plotting.plot_dest(meta_bmk_df, run_id, output_path)
    pass

def add_report_path(run_id_dict):
    for key in run_id_dict:
        report_dir_name = key + '_report'
        report_path = os.path.join(run_id_dict[key]['bm_data_path'],report_dir_name)
        run_id_dict[key]['report_path'] = report_path
    return run_id_dict

def _auto_run(args):
    run_id_dict = find_runs(args.benchmark_results_dir)
    run_id_dict = add_report_path(run_id_dict)
    if args.delete_all_reports:
        run_id_dict = remove_all_reports(run_id_dict)
    for run_id in run_id_dict:
        if run_id_dict[run_id]['report_exists'] == False:
            # find_runs returns a list of files for the run, now.
            # file_list = bmpp.get_benchmark_files(run_id_dict[run_id]['bm_data_path'])
            file_list = run_id_dict[run_id]['files']
            json_results = bmpp.parse_files(file_list)
            json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
            meta_bmk_df = md.make_dataframe(json_results)
            # Any given folder may contain multiple run_ids
            for run_id in meta_bmk_df.run_id.unique():
                bm_list = find_bm_to_graph(json_results, run_id)
                # Making results directory
                try:
                    os.mkdir(run_id_dict[run_id]['report_path'])
                except OSError:
                    logging.error('Failed to create directory for report at {}'.format(run_id_dict[run_id]['report_path']))
                    print ('Failed to create directory for report at {}'.format(run_id_dict[run_id]['report_path']))
                for bm in bm_list:
                    make_SA_graphs(meta_bmk_df, bm, run_id, run_id_dict[run_id]['report_path'])
                saPDF.create_standard_analysis_report(run_id_dict[run_id]['report_path'], json_results, run_id)



if __name__ == '__main__':
    logging.basicConfig(filename="standard_analysis.log", filemode='w',
                       level=logging.INFO)
    # TDH (2019-12-26): Can't get messages to both the log file and console. I've spent enough time on it for now.
    # logger.setLevel(logging.INFO)
    # file_handler = logging.FileHandler('standard_analysis.log', mode='w')
    # file_handler.setLevel(logging.INFO)
    # logger.addHandler(file_handler)
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setLevel(logging.ERROR)
    # logger.addHandler(console_handler)
    parser = argparse.ArgumentParser(description='Generate PDF report.')
    parser.add_argument('benchmark_results_dir',
                        nargs='?',
                        default='../benchmark_results/')
    parser.add_argument('-d',
                        '--delete_all_reports',
                        nargs='?',
                        default=False)
    args = parser.parse_args()
    _auto_run(args)