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
                    if 'helics-broker-out' in uuid_str:
                        continue
                    else:
                        err_str = '{} already exists in dictionary and ' \
                                  'shouldn\'t (filenames should be unique)'
                        err_str = err_str.format(uuid_str)
                        logging.error(err_str)
                        raise Exception(err_str)
                json_results[uuid_str] = {}
                json_results[uuid_str]['filename'] = filename
                json_results[uuid_str]['path'] = path

                # The header lines in the results file contain metadata
                # that is not JSON formatted and needs to be
                # "hand-parsed". After these lines are parsed, the
                # remainder of the file is correctly JSON formatted
                # and is aggregated into a single string to be later
                # used by Python's built-in JSON parser.
                json_str, json_results = parse_header_lines(json_file,
                                                            json_results,
                                                            uuid_str)
    return json_results


def _check_file_validity(path, filename):
    """This function evaluates whether a the passed-in file should be
    processed. The function largely evaluates the file extension but
    also filters out other system files

    Args:
        path (str) - Path to (but not including) the file to be
        evaluated
        filename (str) - Name of file being evaluated

    Returns:
        file_valid (bool) - Flag indicating whether this file should be
        processed.
    """

    file_valid = True
    name, extension = os.path.splitext(filename)
    if filename == '.DS_Store':
        file_valid = False
    elif filename == '.':
        file_valid = False
    elif filename == '/':
        file_valid = False
    elif filename == '':
        file_valid = False
    elif extension == '.png':
        file_valid = False
    elif extension == '.jpg':
        file_valid = False
    elif extension == '.pdf':
        file_valid = False
    return file_valid


def parse_header_lines(json_file, json_results, uuid_str):
    """This function parses the non-JSON metadata header lines in the
    results files and loads them into the dictionary. After the header
    lines, the remainder of the file is JSON so teh function sucks up
    those lines into a single JSON-formatted string and passes it back.

    Args:
        json_file (file obj) - Current benchmark results file being
        processed.
        json_results (dict) - Dictionary of all benchmark results
        (keyed by benchmark results filename) that the data and
        metadata from json_file are being added to.
        uuid_str (str) - Key for dictionary for this benchmark results
        file (json_file)

    Returns:
        json_str (str) - JSON-formatted string containing some metadata
        and all benchmark results found in json_file
        json_results (dict) - Dictionary with new entry containing
        header-line metadata for json_file
    """

    json_str = ''
    json_body = 0
    for line in json_file:
        line = line.strip()

        # Generally, an attempt is made to pull out relevant information
        # from the raw header line string and save it as its own entity
        # in the dictionary (for ease of use later). The raw header line
        # string is also generally saved for use later if needed.
        # Sometimes the raw header line string is exactly the data
        # needed in which case the string is not saved separately.
        # Sometimes the details in the string are not known and thus no
        # specific pieces are pulled out for later use.
        if 'HELICS VERSION:' in line:
            json_results[uuid_str]['helics_version_string'] = line[16:]
            match = re.search('\d+.*?-',line)
            if match:
                json_results[uuid_str]['helics_version'] = \
                    match.group(0)[ :-1] # trimming the trailing dash
            else:
                logging.error(
                    '{}: Failed to parse HELICS VERSION line.'.format(
                        json_file['name']))
        elif 'ZMQ VERSION:' in line:
            json_results[uuid_str]['zmq_version_string']  = line[12:]
            match = re.search('v\d+\..*',line)
            if match:
                json_results[uuid_str]['zmq_version'] = match.group(0)[1:]
            else:
                logging.error('{}: Failed to parse ZMQ VERSION line.'.format(
                    json_file['name']))
        elif 'COMPILER INFO:' in line:
            json_results[uuid_str]['compiler_info_string']  = line[15:]
            json_results = _parse_compiler_string(uuid_str, json_results)
        elif 'BUILD FLAGS:' in line:
            json_results[uuid_str]['build_flags_string'] = line[12:]
        elif 'HOST PROCESSOR TYPE:' in line:
            json_results[uuid_str]['host_processor'] = line[21:]
        elif 'CPU MODEL:' in line:
            json_results[uuid_str]['host_processor_string'] = line[10:].strip()
        elif 'ELAPSED TIME' in line:
            json_results[uuid_str]['elapsed_time'] = line[19:]
        elif 'EVENT COUNT' in line:
            json_results[uuid_str]['EvCount'] = line[13:]
        elif ('-------------------------------------------' in line and
              json_body == 0):
            # Last line of non-JSON header
            json_body = 1
        elif json_body == 1:
            # Creating JSON string for remainder of file to be loaded
            # into dictionary separately.
            json_str = json_str + line
        elif 'HELICS BUILD INFO' in line or 'PROCESSOR INFO' in line:
            # Headers lines we don't need to parse and can just skip
            pass
        else:
            logging.error('Failed to parse line in {}.'.format(
                os.path.join(json_results[uuid_str]['path'],
                             json_results[uuid_str]['filename'])))
            logging.error('    {}'.format(line))
    return json_str, json_results


def parse_and_add_benchmark_metadata(json_results):
    """This function parses the name of the test to extract metadata
    related to the test conditions (e.g. number of federates, which
    HELICS core was used)

    Args:
        json_results (dict) - Dictionary of all benchmark results
        (keyed by benchmark results filename) that metadata from the
        benchmark name are being added to.

    Returns:
        json_results (dict) - Dictionary with new benchmark metadata
    """
    for key, value in json_results.items():
        # Convenience and/or performance assignments
        filename = json_results[key]['filename']
        json_results = _add_run_id(key, json_results)
        json_results = _add_core(key, json_results)
        json_results = _add_name(key, json_results)
        if 'PholdFederate' in filename:
            json_results[key]['benchmark'] = 'PholdFederate'
    return json_results


def _add_core(key, json_results):
    """This function parses the benchmark name to add the core type to
    benchmark metadata.

    Args:

        bm_name (str) - Benchmark name string which contains the core
        type information
        filename (str) - Path and name of file in which the benchmark
        information is contained. Only used for error reporting.
        json_results (dict) - Dictionary of all benchmark results
        (keyed by benchmark results filename) that the data and
        metadata from json_file are being added to.
        key (str) - Key for dictionary for this benchmark results
        idx (str) - Index of the current benchmark being processed.
        needed so core type information can be written into the correct
        location in the json_results dictionary.

    Returns:
        json_results (dict) - Dictionary of all benchmark results
        (keyed by benchmark results filename) that metadata from the
        benchmark name are being added to.
    """
    path = json_results[key]['path']
    
    if 'tcp' in path:
        json_results[key]['core_type'] = 'tcp'
    elif 'tcpss' in path:
        json_results[key]['core_type'] = 'tcpss'
    elif 'udp' in path:
        json_results[key]['core_type'] = 'udp'
    elif 'zmq' in path:
        json_results[key]['core_type'] = 'zmq'
    elif 'zmqss' in path:
        json_results[key]['core_type'] = 'zmqss'
    else:
        warn_str = 'Unable to find core type in {}; ' \
                        'setting to "unspecified"'.format(path)
        logging.warning(warn_str)
        
    return json_results


def _add_run_id(key, json_results):
    """This function parses the filename to extract the 5 character
    run ID for a given file and adds it to the json_results dictionary

    Args:
        json_results (dict) - Dictionary of all benchmark results
        (keyed by benchmark results filename) that the data and
        metadata from json_file are being added to.

    Returns:
        json_results (dict) - json_results with run_id added for
        the indicated results file.
    """
    match = re.search('\d\-out.txt', json_results[key]['filename'])
    if match:
        run_id = match.group(0)[0:-4]
        json_results[key]['run_id'] = run_id
    else:
        json_results[key]['run_id'] = ''
    return json_results

def _add_name(key, json_results):
    """This function creates a name for each .txt and adds it
    to json_results.
       
    Args:
        json_results (dict) - Dictionary of all benchmark results
        (keyed by benchmark results filename) that the data and
        metadata from json_file are being added to.

    Returns:
        json_results (dict) - json_results with run_id added for
        the indicated results file.
    """
    match = re.search('N\d\-job-\d*', json_results[key]['path'])
    if match:
        name = match.group(0)
        json_results[key]['name'] = name
    else:
        json_results[key]['name'] = ''
    return json_results
    


def _parse_compiler_string(uuid, json_results):
    """This function parses the compiler string in the metadata header
    line and adds it to the json_results metadata for the benchmark

        Args:
            json_results (dict) - Dictionary of all benchmark results
            (keyed by benchmark results filename) that the data and
            metadata from json_file are being added to.

        Returns:
            json_results (dict) - json_results with compiler metadata
            extracted and added to the results for a given
            benchmark.
        """
    # Since I'm going to be using it alot...
    compiler_str = json_results[uuid]['compiler_info_string']

    # Generator
    generators = ['Ninja',
                  'Visual Studio 15 2017',
                  'Visual Studio 16 2019',
                  'Unix Makefiles',
                  'MSYS Makefiles']
    match = re.search('^.*?:', compiler_str)
    matched_generator = False
    for item in generators:
        if item in match.group(0):
            json_results[uuid]['generator'] = item
            matched_generator = True
            break
    if matched_generator == False:
        err_str = 'Unable to match element in string "{}" to ' \
                  'known generator in compiler options: {}'
        err_str = err_str.format(match.group(0), pp.pformat(generators))
        logging.error(err_str)

    # System
    match = re.search('\s.*?:', compiler_str)
    if match:
        match_linux = re.search('Linux-.*?:', match.group(0))
        match_windows = re.search('Windows-[\d|\.]*', match.group(0))
        match_darwin = re.search('Darwin-[\d|\.]*', match.group(0))
        if match_linux:
            # Linux system
            json_results[uuid]['system'] = 'Linux'
            linux_version = match_linux.group(0)[6:]
            json_results[uuid]['system_version'] = linux_version

            # Splitting up the Linux version string
            match3= re.search('\d+\.',linux_version)
            json_results[uuid]['linux_kernel_version'] = match3.group(0)[:-1]
            match3 = re.search('\.\d+\.', linux_version)
            json_results[uuid]['linux_major_version'] = match3.group(0)[1:-1]
            match3 = re.search('\.\d+-', linux_version)
            json_results[uuid]['linux_minor_version'] = match3.group(0)[1:-1]

            # TDH: There's some weirdness with the bug fix version
            # and/or distro string. I'm doing my best to handle it.
            match3 = re.search('-\d+-', linux_version)
            if match3:
                json_results[uuid]['linux_bug_fix_version'] =\
                    match3.group(0)[1:-1]
                match4 = re.search('-(?!\d).*$', linux_version)
                json_results[uuid]['linux_distro_string'] =\
                    match4.group(0)[1:-1]
            else:
                match3 = re.search('-.*:(?!-\d+\.\d+\.\d+-)', linux_version)
                if match3:
                    json_results[uuid]['linux_bug_fix_version'] = \
                        match3.group(0)[1:-1]
                    json_results[uuid]['linux_distro_string'] = ''
                else:
                    err_str = 'Unable to parse Linux ' \
                              'kernel bug fix version: {}'
                    err_str = err_str.format(linux_version)
                    logging.error(err_str)
        elif match_windows:
            # Windows
            json_results[uuid]['system'] = 'Windows'
            windows_version =  match_windows.group(0)[8:]
            json_results[uuid]['system_version'] = windows_version
        elif match_darwin:
            # Darwin (Mac) system
            json_results[uuid]['system'] = 'Darwin'
            darwin_version = match_darwin.group(0)[7:]
            json_results[uuid]['system_version'] = darwin_version

            # Splitting up the Linux version string
            match3 = re.search('\d+\.', darwin_version)
            json_results[uuid]['darwin_kernel_version'] = match3.group(0)[:-1]
            match3 = re.search('\.\d+\.', darwin_version)
            json_results[uuid]['darwin_major_version'] = match3.group(0)[1:-1]
            match3 = re.search('\.\d+$', darwin_version)
            json_results[uuid]['darwin_minor_version'] = match3.group(0)[1:]
    else:
        err_str = 'Unexpected compiler system data, could not parse {}'
        err_str = err_str.format(compiler_str)
        logging.error(err_str)


    # Platform
    # TDH: This string can be null so I'm having to find it by process
    # of elimination
    match = re.search('.*?[Windows|Linux]-', compiler_str)
    trimmed_str = re.sub(json_results[uuid]['generator'], '', match.group(0))
    trimmed_str = re.sub(json_results[uuid]['system'], '', trimmed_str)
    trimmed_str = re.sub('-', '', trimmed_str)
    trimmed_str = trimmed_str.strip()
    json_results[uuid]['platform'] = trimmed_str



    # CXX compiler
    match = re.search(':.*$', compiler_str)
    if match:
        # compiler name
        match2 = re.search(':.*-', match.group(0))

        if match2:
            cxx_compiler = match2.group(0)[1:-1]
            json_results[uuid]['cxx_compiler'] = cxx_compiler
        else:
            json_results[uuid]['cxx_compiler'] = ''

        # compiler version
        match2 = re.search('-.*$', match.group(0))
        if match2:
            cxx_compiler_version = match2.group(0)[1:]
            json_results[uuid]['cxx_compiler_version'] = cxx_compiler_version
        else:
            json_results[uuid]['cxx_compiler_version'] = ''
    else:
        json_results[uuid]['cxx_compiler'] = ''
        json_results[uuid]['cxx_compiler_version'] = ''

    return json_results

def create_file_list(directory):
    """This function creates a file_list for post-processing.
    
    Args:
        directory (directory) - Path of where files are located.
    """
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file != 'helics-broker-out.txt':
                file_list.append(os.path.join(root, file))
            else:
                pass
    
    return file_list
            
            
def _auto_run(args):
    """This function executes when the script is called as a stand-alone
    executable.
    To use as a stand-alone script (primarily for development purspoes)
    the script must run part of the standard_analysis.py to create the
    file list it will parse.

    Optionally, can write out the results to a json file for offline
    evaluation.

    A more complete description of this code can be found in the
    docstring at the beginning of this file.

    Args:
        '-r' or '--benchmark_results_dir' - Path of top-level folder
        that contains the benchmark results folders/files to be
        processed. For the purposes of testing a folder with at least
        two run IDs must be indicated.

    Returns:
        (nothing)
    """
    json_results = {}
    drs = []
    for root, dirs, files in os.walk(args.m_benchmark_results_dir):
        for dr in dirs:
            drs.append(os.path.join(os.sep, root, dr))
    for d in drs:
        file_list = create_file_list(d)
#        print(file_list)
        json_results.update(parse_files(file_list))
        json_results.update(parse_and_add_benchmark_metadata(json_results))
    if args.write_json_output:
        with open('multinode_bm_results.json', 'w') as outfile:
            json.dump(json_results, outfile)

    # TDH (2019-12-19): Trouble-shooting function whose purpose you'll
    # never guess
    #_check_missing_core_type(json_results)


if __name__ == '__main__':
    # TDH: This slightly complex mess allows lower importance messages
    # to be sent to the log file and ERROR messages to additionally
    # be sent to the console as well. Thus, when bad things happen
    # the user will get an error message in both places which,
    # hopefully, will aid in trouble-shooting.
    fileHandle = logging.FileHandler("multimachine_postprocessing.log", mode='w')
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
#    print(script_path)
    head, tail = os.path.split(script_path)
    m_benchmark_results_dir = os.path.join(head, 
                                           'multinode_benchmark_results',
                                           '2020-01-08')
    parser.add_argument('-m',
                        '--m_benchmark_results_dir',
                        nargs='?',
                        default=m_benchmark_results_dir)
    parser.add_argument('-o',
                        '--write_json_output',
                        nargs='?',
                        default=True)
    args = parser.parse_args()
    _auto_run(args)