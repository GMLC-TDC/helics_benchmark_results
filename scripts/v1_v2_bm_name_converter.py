#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 5 11:26:49 2019

Due to some slightly non-uniform ways of naming the benchmark tests, a new standard naming conventions was established.
This scripts is used to convert the existing benchmark test names contained in the existing results to conform to the
(v2) standard. v2 naming goes into effect on benchmark results starting 2019-12-05.

@author: hard312
"""
import argparse
import logging
import pprint
import os
import re
import subprocess

# Setting up logging
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

def get_benchmark_files(results_dir):
    # Find all the results files in the user-provided results directory
    file_list = []
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            file_list.append(os.path.join(root, file))
    logger.info('Files to parse:\n %s', pp.pformat(file_list))
    return file_list

def rename_bm(file_list):
    pattern1 = re.compile('echo|messageLookup|phold|ring')
    pattern2 = re.compile('messageSend')
    for file in file_list:
        path, filename = os.path.split(file)
        if filename != '.DS_Store':  # Stupid macOS file we can ignore
            match1 = pattern1.search(filename)
            if match1:
                # Most benchmark results will be updated here
                response = subprocess.run(['sed', '-i', '', '-E', '-e', 's~BM_([^\/]*)_multiCore\/([^\/]*)~BM_\\1\/multiCore\/\\2~g',
                               '-e', 's~BM_([^\/]*)_singleCore~BM_\\1\/singleFed~g', file], text=True)
                if response.returncode != 0:
                    logging.warning('Failed update of benchmark names in {}'.format(file))
                    logging.warning('    {}'.format(response.stderr))
                else:
                    logging.info('Updated benchmark names in {}'.format(file))

            else:
                match2 = pattern2.search(filename)
                if match2:

                    # Only the 'messageSendResults' results files get updated here
                    response = subprocess.run(
                        ['sed', '-i', '', '-E', '-e', 's~BM_([^\/]*)\/(.*)MultiCore~BM_\\1\/multiCore\/\\2Core~g',
                         '-e', 's~BM_([^\/]*)\/singleCore~BM_\\1\/singleFed~g', file], text=True)
                    if response.returncode != 0:
                        logging.warning('Failed update of benchmark names in {}'.format(file))
                        logging.warning('    {}'.format(response.stderr))
                    else:
                        logging.info('Updated benchmark names in {}'.format(file))








def _auto_run(args):
    file_list = get_benchmark_files(args.benchmark_results_dir)
    rename_bm(file_list)



if __name__ == '__main__':
    logging.basicConfig(filename="v1_v2_name_converter.log", filemode='w',
                        level=logging.INFO)
    parser = argparse.ArgumentParser(description='Process input files.')
    parser.add_argument('benchmark_results_dir', nargs='?',
                        default='../benchmark_results/')  #
    args = parser.parse_args()
    _auto_run(args)
