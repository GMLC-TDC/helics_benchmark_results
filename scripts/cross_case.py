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
import standard_analysis as sa
import sys

# Installation of FPDF is: python -m pip install fpdf
# Installation of hvplot.pandas is: conda install -c pyviz hvplot
# Installation of selenium is: conda install -c bokeh selenium
# Installation of phantomjs is: brew tap homebrew/cask; brew cask install phantomjs

# Setting up logging
logger = logging.getLogger(__name__)



# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)



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
            print('Failed to create directory {}'.format(output_path))





def _auto_run(args):
    run_id_dict = find_specific_run_id(args.benchmark_results_dir, args.run_id_list)
    create_output_path(args.output_path, args.delete_report)
    file_list = []
    for run_id in run_id_dict:
        file_list.extend(run_id_dict[run_id]['files'])
    json_results = bmpp.parse_files(file_list)
    json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    meta_bmk_df = md.make_dataframe(json_results)
    for run_id in meta_bmk_df.run_id.unique():
        bm_list = sa.find_bm_to_graph(json_results, run_id)
        # make_cross_case_graphs()
        # make_cross_case_PDF()



if __name__ == '__main__':
    logging.basicConfig(filename="cross_case_comparison.log", filemode='w',
                       level=logging.INFO)
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