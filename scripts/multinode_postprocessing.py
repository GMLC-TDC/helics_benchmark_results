# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 14:51:42 2020

@author: barn553
"""

import argparse
import logging
import pprint
import os
import json
import re
# import uuid
import sys
import standard_analysis as sa

# Setting up logging
logger = logging.getLogger(__name__)


# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

def parse_files(file_list):
    """This function parses and formats all the data and metadata of
    interest for each of the files in file_list and puts it into a
    dictionary, keyed off the filename. Since the 5 character run ID
    is assumed (guaranteed?) to be unique (for our purposes) all results
    file paths will be unique strings.

    Args:
        file_list (list) - List of paths to files to parse and process

    Returns:
        json_results (dict) -
    """
    json_results = {}
    for file in file_list:
        path, filename = os.path.split(file)

        # TDH (2020-01-17)
        # Check to make sure that file is valid and worth processing.
        file_valid =_check_file_validity(path, filename)
        if file_valid:
            with open(file) as json_file:

                # TDH (2019-12-26): run IDs can now assumed to be unique
                # so filenames should now be unique.
                uuid_str = filename
                if uuid_str in json_results.keys():
                    err_str = '{} already exists in dictionary and' \
                              'shouldn\'t (filenames should be unique)'
                    err_str = err_str.format(uuid_str)
                    logging.error(err_str)
                    raise Exception(err_str)
                json_results[uuid_str] = {}
                json_results[uuid_str]['filename'] = filename
                json_results[uuid_str]['path'] = path

                # TDH (2019-12-27): Adding in whether this is a "full"
                # (bm) or "key" (bmk) results file
                if filename[0:3] == 'bmk':
                    json_results[uuid_str]['benchmark_type'] = 'key'
                else:
                    json_results[uuid_str]['benchmark_type'] = 'full'

                # The header lines in the results file contain metadata
                # that is not JSON formatted and needs to be
                # "hand-parsed". After these lines are parsed, the
                # remainder of the file is correctly JSON formatted
                # and is aggregated into a single string to be later
                # used by Python's built-in JSON parser.
                json_str, json_results = parse_header_lines(json_file,
                                                            json_results,
                                                            uuid_str)

                # Generally the contents of "json_str" will be correctly
                # formatted JSON. In cases where bugs in the benchmarking
                # code introduce errors in the output file, this will
                # not be the case. When these errors exist, parsing fails,
                # no JSON is added to the dictionary for this file, and
                # an error message is generated in the log file.
                try:
                    json_dict = json.loads(json_str)
                    for key,value in json_dict['context'].items():
                        json_results[uuid_str][key] = value
                    json_results[uuid_str]['benchmarks'] = json_dict[
                        'benchmarks']
                    logging.info('Successfully captured JSON %s', filename)
                except Exception as e:
                    logging.error('Failed to completely capture JSON %s',
                                  filename)
                    logging.error('     exception {}'.format(e))
                    logging.error(json_str)
                    print('Failed to completely capture JSON %s', filename)
                    print('     exception {}'.format(e))
                    sys.exit(1)
    return json_results