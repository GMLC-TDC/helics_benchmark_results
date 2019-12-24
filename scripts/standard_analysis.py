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

# Installation of FPDF is: python -m pip install fpdf
# Installation of hvplot.pandas is: conda install -c pyviz hvplot
# Installation of selenium is: conda install -c bokeh selenium
# Installation of phantomjs is: brew tap homebrew/cask; brew cask install phantomjs

# Setting up logging
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

def find_runs(benchmark_results_dir):
    run_dirs_list = []
    paths_with_reports = []
    for root, dirs, files in os.walk(benchmark_results_dir):
        for dir in dirs:
            dir_full_path = os.path.join(root, dir)
            # Don't generate a report if one already exists
            if dir_full_path[-6:] == 'report':
                paths_with_reports.append(dir_full_path)
                # TDH (2019-12-20): Gotta remove the folder that already has the report in it so we don't re-run it.
                report_parent, report = os.path.split(dir_full_path)
                paths_with_reports.append(report_parent)
            else:
                run_dirs_list.append(dir_full_path)
    if len(run_dirs_list) == 0:
        # The only directory we need to do an analysis in is the one passed in.
        run_dirs_list.append(root)
    return run_dirs_list, paths_with_reports


def remove_all_reports(run_dirs_list, paths_with_reports):
    for path in paths_with_reports:
        if path[-6:] == 'report':
            shutil.rmtree(path)
        else:
            # These are the parents of the dirs with a "report" and now need to be re-run
            run_dirs_list.append(path)
    return run_dirs_list


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



def _auto_run(args):
    run_dirs_list, paths_with_reports = find_runs(args.benchmark_results_dir)
    # TDH (2019-12-23): Trying to keep the processing of the benchmarks in a consistent order
    run_dirs_list.sort()
    if args.remove_all_reports:
        run_dirs_list = remove_all_reports(run_dirs_list, paths_with_reports)
    for path in run_dirs_list:
        file_list = bmpp.get_benchmark_files(path)
        json_results = bmpp.parse_files(file_list)
        json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
        meta_bmk_df = md.make_dataframe(json_results)
        # Any given folder may contain multiple run_ids
        for run_id in meta_bmk_df.run_id.unique():
            bm_list = find_bm_to_graph(json_results, run_id)
            output_path = os.path.join(path, '{}_report'.format(run_id))
            # Making results directory
            try:
                os.mkdir(output_path)
            except OSError:
                logging.error('Failed to create directory for report at {}'.format(output_path))
                print ('Failed to create directory for report at {}'.format(output_path))
            for bm in bm_list:
                make_SA_graphs(meta_bmk_df, bm, run_id, output_path)
            saPDF.create_standard_analysis_report(output_path, json_results, run_id)



if __name__ == '__main__':
    logging.basicConfig(filename="standard_analysis_PDF.log", filemode='w',
                        level=logging.INFO)
    parser = argparse.ArgumentParser(description='Generate PDF report.')
    parser.add_argument('benchmark_results_dir', nargs='?',
                        default='../benchmark_results/')
    parser.add_argument('remove_all_reports', nargs='?',
                        default=False)
    args = parser.parse_args()
    _auto_run(args)