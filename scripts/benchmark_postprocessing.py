#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 2 15:43:22 2019

Processes all HELICS benchmark results files in user-indicated
directories and provides summarized results.

Assumes all files in indicated directory are results files. Supports
results files in arbitrary directory structure beneath the user-provided
directory

@author: hard312
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
        if 'HELICS_BENCHMARK:' in line:
            if 'echo_cResults' in json_results[uuid_str]['filename']:
                json_results[uuid_str]['benchmark'] = 'cEchoBenchmark'
            else:
                json_results[uuid_str]['benchmark'] = line[18:]
        elif 'HELICS VERSION:' in line:
            json_results[uuid_str]['helics_version_string']  = line[16:]
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

        if 'ActionMessage' in filename:
            for idx, results_dict in enumerate(
                    json_results[key]['benchmarks']):
                bm_name = results_dict['name']
                # Core type
                json_results = _add_core(bm_name,
                                         filename,
                                         json_results,
                                         key,
                                         idx)

            info_str = ('Test type = ActionMessage\n'
                       '          Added minimal benchmark metadata to {} ')
            info_str = info_str.format(filename)
            logging.info(info_str)
        elif 'conversion' in filename:
            for idx, results_dict in enumerate(
                    json_results[key]['benchmarks']):
                bm_name = results_dict['name']
                # Core type
                json_results = _add_core(bm_name,
                                         filename,
                                         json_results,
                                         key,
                                         idx)
            info_str = ('Test type = Conversion\n'
                       '          Added minimal benchmark metadata to {} ')
            info_str = info_str.format(filename)
            logging.info(info_str)
        elif 'echo' in filename:
            for idx, results_dict in enumerate(
                    json_results[key]['benchmarks']):
                bm_name = results_dict['name']

                # Federate count
                match = re.search('/\d+/',bm_name)
                federate_count = int(match.group(0)[1:-1])
                json_results[key]['benchmarks'][idx]['federate_count'] = \
                    federate_count

                # Core type
                json_results= _add_core(bm_name,
                                        filename,
                                        json_results,
                                        key,
                                        idx)
            if 'echoResults' in filename:
                info_str = ('Test type = echoResults\n'
                            '          Added benchmark metadata to {} ')
            if 'echoMessage' in filename:
                info_str = ('Test type = echoMessage\n'
                            '          Added benchmark metadata to {} ')
            info_str = info_str.format(filename)
            logging.info(info_str)
        elif 'filter' in filename:
            for idx, results_dict in enumerate(
                    json_results[key]['benchmarks']):
                bm_name = results_dict['name']

                # Federate count and filter location
                match = re.search('/\d+/\d+/', bm_name)
                match2 = re.findall('\d+', match.group(0))
                federate_count = int(match2[0])
                if match2[1] == "1":
                    filter_location = "destination"
                elif match2[1] == "2":
                    filter_location = "source"
                else:
                    err_str = '{}: {}: Filter location {} is not a valid ' \
                              'value of "0" or "1"'
                    err_str = err_str.format(filename, bm_name, match2[1])
                    logging.error(err_str)
                json_results[key]['benchmarks'][idx]['filter_location'] =\
                    filter_location
                json_results[key]['benchmarks'][idx]['federate_count'] =\
                    federate_count

                # Core type
                json_results = _add_core(bm_name,
                                         filename,
                                         json_results,
                                         key,
                                         idx)
            info_str = ('Test type = filter\n'
                        '          Added benchmark metadata to {} ')
            info_str = info_str.format(filename)
            logging.info(info_str)
        elif 'messageLookup' in filename:
            for idx, results_dict in enumerate(
                    json_results[key]['benchmarks']):
                bm_name = results_dict['name']

                if 'multiCore' in bm_name:
                    # Interface count and federate count
                    match = re.search('/\d+/\d+/',bm_name)
                    match2 = re.findall('\d+',match.group(0))
                    interface_count = int(match2[0])
                    federate_count = int(match2[1])
                    json_results[key]['benchmarks'][idx]['interface_count'] = \
                        interface_count
                    json_results[key]['benchmarks'][idx]['federate_count'] = \
                        federate_count

                # Core type
                json_results = _add_core(bm_name,
                                         filename,
                                         json_results,
                                         key,
                                         idx)
            info_str = ('Test type = messageLookup\n'
                        '          Added benchmark metadata to {} ')
            info_str = info_str.format(filename)
            logging.info(info_str)
        elif 'messageSend' in filename:
            for idx, results_dict in enumerate(
                    json_results[key]['benchmarks']):
                bm_name = results_dict['name']

                # Message size and message count
                match = re.search('/\d+/\d+/',bm_name)
                match2 = re.findall('\d+',match.group(0))
                message_size = int(match2[0])
                message_count = int(match2[1])
                json_results[key]['benchmarks'][idx]['message_size'] = \
                    message_size
                json_results[key]['benchmarks'][idx]['message_count'] = \
                    message_count

                # Core type
                json_results = _add_core(bm_name,
                                         filename,
                                         json_results,
                                         key,
                                         idx)
            info_str = ('Test type = messageSend\n'
                        '          Added benchmark metadata to {} ')
            info_str = info_str.format(filename)
            logging.info(info_str)
        elif 'ring' in filename:
            for idx, results_dict in enumerate(
                    json_results[key]['benchmarks']):
                bm_name = results_dict['name']

                if 'multiCore' in bm_name:
                    # Federate count
                    match = re.search('/\d+/',bm_name)
                    federate_count = int(match.group(0)[1:-1])
                    json_results[key]['benchmarks'][idx]['federate_count'] = \
                        federate_count

                # Core type
                json_results = _add_core(bm_name,
                                         filename,
                                         json_results,
                                         key,
                                         idx)
            info_str = ('Test type = ring\n'
                        '          Added benchmark metadata to {} ')
            info_str = info_str.format(filename)
            logging.info(info_str)
        elif 'phold' in filename:
            for idx, results_dict in enumerate(
                    json_results[key]['benchmarks']):
                bm_name = results_dict['name']

                # Federate count
                match = re.search('/\d+/',bm_name)
                federate_count = int(match.group(0)[1:-1])
                json_results[key]['benchmarks'][idx]['federate_count'] = \
                    federate_count

                # Core type
                json_results = _add_core(bm_name,
                                         filename,
                                         json_results,
                                         key,
                                         idx)
            info_str = ('Test type = phold\n'
                        '          Added benchmark metadata to {} ')
            info_str = info_str.format(filename)
            logging.info(info_str)
        elif 'timing' in filename:
            for idx, results_dict in enumerate(
                    json_results[key]['benchmarks']):
                bm_name = results_dict['name']

                # Federate count
                match = re.search('/\d+/',bm_name)
                federate_count = int(match.group(0)[1:-1])
                json_results[key]['benchmarks'][idx]['federate_count'] = \
                    federate_count

                # Core type
                json_results= _add_core(bm_name,
                                        filename,
                                        json_results,
                                        key,
                                        idx)
            info_str = ('Test type = timing\n'
                        '          Added benchmark metadata to {} ')
            info_str = info_str.format(filename)
            logging.info(info_str)
    return json_results



def _add_core(bm_name, filename, json_results, key, idx):
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
    if 'multiCore/' in bm_name:
        core_match = re.search('multiCore/.*?Core', bm_name)
        if core_match:
            core_name = core_match.group(0)[10:-4]
            json_results[key]['benchmarks'][idx]['core_type'] = core_name
        else:
            logging.error('No core_type added to {} in {}'.format(
                bm_name,
                filename))

    # TDH (2019-12-29)
    # This is trying to deal with the inconsistency in the naming
    # convention that, as of this writing, exists in the results files.
    # Hopefully we can soon arrive at a convention and retroactively
    # change all the results files to conform to that convention.
    elif 'singleFed/' in bm_name:
            json_results[key]['benchmarks'][idx]['core_type'] = 'singleFed'
    elif 'singleCore/' in bm_name:
            json_results[key]['benchmarks'][idx]['core_type'] = 'singleCore'
    else:
        json_results[key]['benchmarks'][idx]['core_type'] = 'unspecified'
        if ('conversion' not in bm_name
                and 'interpret' not in bm_name
                and 'AM' not in bm_name):
            # TDH (2019-12-19)
            # I know these benchmarks don't have a core specified and
            # don't want to write out a warning and clutter up the log
            # file.
            warn_str = 'Unable to find core type in {} in {}; ' \
                        'setting to "unspecified"'
            warn_str = warn_str.format(bm_name, filename)
            logging.warning(warn_str)
    return json_results


def _check_missing_core_type(json_results):
    """This function checks the json_results dictionary to see if any of
    the benchmaks are missing a value for core_type. This is a
    trouble-shooting function developed by Trevor to help hunt down some
    graphing bugs and was retained because it seems useful. Results from
    the test are written to the log file.

        Args:
            json_results (dict) - Dictionary of all benchmark results
            (keyed by benchmark results filename) that the data and
            metadata from json_file are being added to.

        Returns:
            null
        """
    for uuid in json_results:
        for idx, benchmark in enumerate(json_results[uuid]['benchmarks']):
            if 'core_type' not in benchmark:
                logging.error('No core_type found in {} in {}'.format(
                    benchmark,
                    json_results[uuid]['filename']))
            else:
                logging.info('core_type found in {} in {}'.format(
                    benchmark,
                    json_results[uuid]['filename']))


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
    match = re.search('\d_.*?\.txt', json_results[key]['filename'])
    if match:
        run_id = match.group(0)[2:-4]
        json_results[key]['run_id'] = run_id
    else:
        json_results[key]['run_id'] = ''
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

    run_id_dict = sa.find_runs(args.benchmark_results_dir)
    run_id_dict = sa.add_report_path(run_id_dict)
    json_results = {}
    for run_id in run_id_dict:
        file_list = run_id_dict[run_id]['files']
        json_results.update(parse_files(file_list))
        json_results = parse_and_add_benchmark_metadata(json_results)
    if args.write_json_output:
        with open('bm_results.json', 'w') as outfile:
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
    fileHandle = logging.FileHandler("benchmark_postprocessing.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])

    parser = argparse.ArgumentParser(description='Process input files.')
    # TDH: Have to do a little bit of work to generate a good default
    # path for the results folder. Default only works if being run
    # from the "scripts" directory in the repository structure.
    script_path = os.path.dirname(os.path.realpath(__file__))
    head, tail = os.path.split(script_path)
    benchmark_results_dir = os.path.join(head, 'benchmark_results')
    parser.add_argument('-r',
                        '--benchmark_results_dir',
                        nargs='?',
                        default=benchmark_results_dir)
    parser.add_argument('-o',
                        '--write_json_output',
                        nargs='?',
                        default=True)
    args = parser.parse_args()
    _auto_run(args)
