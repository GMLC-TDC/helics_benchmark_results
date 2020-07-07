# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 09:14:07 2020

Adds metadata to current results files.

2020-03-13 multinode benchmark results data did not have
HELICS information; this script adds that information to the files
so that post-processing runs properly.

NOTE: This script should be run ONLY when there's missing
metadata from the results files; otherwise, DO NOT run this file.  In
order to run this file, a separate .txt. file must be created with the
necessary metadata.

@author: barn553
"""

import argparse
import logging
import pprint
import os
import sys

# Setting up logging
logger = logging.getLogger(__name__)


# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)


def add_metadata(file):
    """This function merges two .txt files into one."""
    data = data2 = ""
    # Reading data from file1
    with open('multinode_metadata_20200313.txt') as fp:
        data = fp.read()

    # Reading data from file2
    with open('{}'.format(file)) as fp:
        data2 = fp.read()

    # Merging 2 files
    # To add the data of file2
    # from next line
    data += "\n"
    data += data2

    with open('{}'.format(file), 'w') as fp:
        fp.write(data)
    logging.info('added the metadata to the file')


def _auto_run(args):
    """Runs this script.

    Args:
        '-m' or '--m_benchmark_results_dir' - Path of top-level folder
        that contains the multinode benchmark results folders/files
        to be processed.

    Returns:
        (null)
    """
    logging.info('starting the execution of this script...')
    for root, dirs, files in os.walk(args.m_benchmark_results_dir):
        for file in files:
            if file != 'helics-broker-out.txt':
                add_metadata(os.path.join(root, file))
                logging.info('adding metadata to the file')
            else:
                logging.error('{} is an invalid file; cannot add metadata')
    logging.info('successfully added metadata to the files.')


if __name__ == '__main__':
    fileHandle = logging.FileHandler(
        "multimachine_preprocessing.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])

    parser = argparse.ArgumentParser(description='Process output files.')
    # TDH: Have to do a little bit of work to generate a good default
    # path for the results folder. Default only works if being run
    # from the "scripts" directory in the repository structure.
    script_path = os.path.dirname(os.path.realpath(__file__))
    head, tail = os.path.split(script_path)
    m_benchmark_results_dir = os.path.join(
        head, 'multinode_benchmark_results', '2020-03-13')
    parser.add_argument('-m',
                        '--m_benchmark_results_dir',
                        nargs='?',
                        default=m_benchmark_results_dir)
    args = parser.parse_args()
    # _auto_run(args)
