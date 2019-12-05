#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 2 15:43:22 2019

Processes all HELICS benchmark results files in user-indicated directories and provides summarized results.

Assumes all files in indicated directory are results files. Supports results files in arbitrary directory structure
beneath the user-provided directory

@author: hard312
"""
import argparse
import logging
import pprint
import os
import json
import re
import uuid


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

def parse_files(file_list):
    json_results = {}
    for file in file_list:
        path, filename = os.path.split(file)
        with open(file) as json_file:
            #logging.info('Trying to parse %s', filename)
            if filename != '.DS_Store': # Stupid macOS file we can ignore

                # At the time of this writing, results files are not guaranteed to have unique names (though the data
                #    in two identically named files can be different. To solve this problem a unique ID is generated
                #    for each results file and used as the key in the dictionary for the results in that file.
                #    The filename and path are saved as entities in the dictionary.
                uuid_str = str(uuid.uuid4())
                json_results[uuid_str] = {}
                json_results[uuid_str]['filename'] = filename
                json_results[uuid_str]['path'] = path

                # The header lines in the results file contain metadata that is not JSON formatted and needs to be
                #    "hand-parsed". After these lines are parsed, the remainder of the file is correctly JSON formatted
                #    and is aggregated into a single string to be later used by Python's built-in JSON parser.
                json_str, json_results = parse_header_lines(json_file, json_results, uuid_str)

                # Generally the contents of "json_str" will be correctly formatted JSON. In cases where bugs in the
                #    benchmarking code introduce errors in the output file, this will not be the case. When these errors
                #    exist, parsing fails, no JSON is added to the dictionary for this file, and an error message is
                #    generated in the log file.
                try:
                    json_dict = json.loads(json_str)
                    json_dict = _byteify(json_dict)
                    for key,value in json_dict['context'].items():
                        json_results[uuid_str][key] = value
                    json_results[uuid_str]['benchmarks'] = json_dict['benchmarks']
                    logging.info('Successfully captured JSON %s', filename)
                except Exception as e:
                    logging.error('Failed to completely capture JSON %s', filename)
                    logging.error('     exception{}'.format(e))
    return json_results


def parse_header_lines(json_file, json_results, uuid_str):
    json_str = ''
    json_body = 0
    for line in json_file:
        line = line.strip()

        # Generally, an attempt is made to pull out relevant information from the raw header line string and save it as
        #   its own entity in the dictionary (for ease of use later). The raw header line string is also generally saved
        #   for use later if needed. Sometimes the raw header line string is exactly the data needed in which case the
        #    string is not saved separately. Sometimes the details in the string are not known and thus no specific
        #    pieces are pulled out for later use.
        if 'HELICS_BENCHMARK:' in line:
            json_results[uuid_str]['benchmark'] = line[18:]
        elif 'HELICS VERSION:' in line:
            json_results[uuid_str]['helics_version_string']  = line[16:]
            match = re.search('\d+.*?-',line)
            if match:
                json_results[uuid_str]['helics_version'] = match.group(0)[:-1] # trimming the trailing dash
            else:
                log.error('Failed to parse HELICS VERSION line.')
        elif 'ZMQ VERSION:' in line:
            json_results[uuid_str]['zmq_version_string']  = line[12:]
            match = re.search('v\d+\..*',line)
            if match:
                json_results[uuid_str]['zmq_version'] = match.group(0)[1:]
            else:
                log.error('Failed to parse ZMQ VERSION line.')
        elif 'COMPILER INFO:' in line:
            json_results[uuid_str]['compiler_info_string']  = line[14:]
        elif 'BUILD FLAGS:' in line:
            json_results[uuid_str]['build_flags_string'] = line[12:]
        elif 'HOST PROCESSOR TYPE:' in line:
            json_results[uuid_str]['host_processor'] = line[21:]
        elif 'CPU MODEL:' in line:
            json_results[uuid_str]['host_processor_string'] = line[21:]
        elif '-------------------------------------------' in line and json_body == 0:
            # Last line of non-JSON header
            json_body = 1
        elif json_body == 1:
            # Creating JSON string for remainder of file to be loaded into dictionary separately.
            json_str = json_str + line
        elif 'HELICS BUILD INFO' in line or 'PROCESSOR INFO' in line:
            # Headers lines we don't need to parse and can just skip
            pass
        else:
            logging.error('Failed to parse line in {}.'.format(os.path.join(json_results[uuid_str]['path'], json_results[uuid_str]['filename'])))
            logging.error('    {}'.format(line))
    return json_str, json_results


def parse_and_add_benchmark_metadata(json_results):
    for key, value in json_results.items():
        filename = json_results[key]['filename']
        if 'ActionMessage' in filename:
            logging.warning('Added no benchmark metadata to {} as test type "ActionMessage"'.format(filename))
        if 'conversion' in filename:
            logging.warning('Added no benchmark metadata to {} as test type "conversion"'.format(filename))
        elif 'echo' in filename:
            for idx, results_dict in enumerate(json_results[key]['benchmarks']):
                match = re.search('/\d+/',results_dict['name'])
                federate_count = int(match.group(0)[1:-1])
                json_results[key]['benchmarks'][idx]['federate_count'] = federate_count
            logging.info('Added benchmark metadata to {} as test type "echo" or "echoMessage"'.format(filename))
        elif 'filter' in filename:
            logging.warning('Added no benchmark metadata to {} as test type "filter"'.format(filename))
        elif 'messageLookup' in filename:
            for idx, results_dict in enumerate(json_results[key]['benchmarks']):
                if 'multiCore' in results_dict['name']:
                    match = re.search('/\d+/\d+/',results_dict['name'])
                    match2 = re.findall('\d+',match.group(0))
                    interface_count = int(match2[0])
                    federate_count = int(match2[1])
                    json_results[key]['benchmarks'][idx]['interface_count'] = interface_count
                    json_results[key]['benchmarks'][idx]['federate_count'] = federate_count
            logging.info('Added benchmark metadata to {} as test type "messageLookup"'.format(filename))
        elif 'messageSend' in filename:
            for idx, results_dict in enumerate(json_results[key]['benchmarks']):
                match = re.search('/\d+/\d+/',results_dict['name'])
                match2 = re.findall('\d+',match.group(0))
                message_size = int(match2[0])
                message_count = int(match2[1])
                json_results[key]['benchmarks'][idx]['message_size'] = message_size
                json_results[key]['benchmarks'][idx]['message_count'] = message_count
            logging.info('Added benchmark metadata to {} as test type "messageSend"'.format(filename))
        elif 'ring' in filename:
            for idx, results_dict in enumerate(json_results[key]['benchmarks']):
                if 'multiCore' in results_dict['name']:
                    match = re.search('/\d+/',results_dict['name'])
                    federate_count = int(match.group(0)[1:-1])
                    json_results[key]['benchmarks'][idx]['federate_count'] = federate_count
            logging.info('Added benchmark metadata to {} as test type "ring"'.format(filename))
        elif 'phold' in filename:
            for idx, results_dict in enumerate(json_results[key]['benchmarks']):
                match = re.search('/\d+/',results_dict['name'])
                federate_count = int(match.group(0)[1:-1])
                json_results[key]['benchmarks'][idx]['federate_count'] = federate_count
            logging.info('Added benchmark metadata to {} as test type "pHold"'.format(filename))
    return json_results


def _byteify(input):
    if isinstance(input, dict):
        return {_byteify(key): _byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [_byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def _auto_run(args):
    file_list = get_benchmark_files(args.benchmark_results_dir)
    json_results = parse_files(file_list)
    json_results = parse_and_add_benchmark_metadata(json_results)


if __name__ == '__main__':
    logging.basicConfig(filename="helics_benchmark_postprocessing.log", filemode='w',
                        level=logging.INFO)
    parser = argparse.ArgumentParser(description='Process input files.')
    parser.add_argument('benchmark_results_dir', nargs='?',
                        default='../benchmark_results/')  #
    args = parser.parse_args()
    _auto_run(args)
