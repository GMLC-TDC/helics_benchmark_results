#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 03 13:47:29 2020

Given the results of a cross-comparison run run as a JSON string and the
path to those results (where graph images have already been created),
generate a PDF report headed by all appropriate metadata and including all
images.

This script can be run as a standalone script to generate cross-run-ID
analysis report PDF for every run in the user-provided list. A "run" is
specified by the 5 character unique ID in the filename for every results
file associated with that run.

The metadata header for the report that is created provides a comparison
of the metadata parameter values, highlighting those that are different.

The command line arguments for the function can be found in the code
following the lines following the "if __name__ == '__main__':" line
at the end of this file.

@author: hard312
"""

import argparse
import logging
import pprint
import os
import sys
import standard_analysis_pdf as saPDF
from fpdf import FPDF

# Installation of FPDF is: python -m pip install fpdf


# Setting up logging
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)


def create_cross_run_id_report(json_results, run_id_list,
                               output_path, parameter_list):
    """This function creates the cross-run ID PDF

    Args:
        json_results (dict) - benchmark results

        run_id_list (list) - List of strings of the run-IDs being compared

        output_path (str) - Path where graph images are located and PDF
        report will be saved.

        parameter_list (list) - List of strings of metadata parameters
        to be compared

    Returns:
        null
    """
    run_id_keys = get_run_id_keys(json_results, run_id_list)

    # Create the PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=8)

    # Create PDF file name from the run IDs
    run_id_str = '-'.join(run_id_list)
    report_name = run_id_str + '_cross_run_id_analysis.pdf'
    report_path = os.path.join(output_path, report_name)

    # Create the header metadata from the metadata in the JSON results
    # and write out to PDF object.
    # TDH (2020-01-06): Create report title
    pdf.set_font("Courier", style='', size=20)
    title = 'Cross-run-ID Comparison Report\n\n'
    line_height = 3
    pdf.write(line_height, title)

    # Changing font for report subtitle
    pdf.set_font("Courier", style='', size=10)
    title = '(differences in bold)\n\n\n'
    pdf.write(line_height, title)

    # TDH (2020-01-14)
    # Comparing parameter values for all parameters in parameter_list.
    # Those that are different are highlighted in bold.
    # Note that since all text in a given string must be in the same font
    # the writing out of this header text is incremental (by parameter)
    # allowing for each parameter entry to be formatted in bold or not.
    for param in parameter_list:
        param_title = '{}:\n'.format(param.upper())
        pdf.set_font("Courier", style='', size=10)
        pdf.write(line_height, param_title)
        header_metadata_str, diff = grab_header_metadata(json_results,
                                                         run_id_keys,
                                                         param)
        # TDH (2020-01-06): Parameters that are different get written
        # out in bold
        if diff:
            pdf.set_font("Courier", style='B', size=10)
            pdf.write(line_height, header_metadata_str)
        else:
            pdf.set_font("Courier", style='', size=8)
            pdf.write(line_height, header_metadata_str)

    # Add previously generated graphs to the PDF object
    pdf = saPDF.add_benchmark_graphs(pdf, output_path)

    # Output final PDF file from PDF object
    pdf.output(report_path)


def get_run_id_keys(json_results, run_id_list):
    """This function finds the key used in the json_results dictionary
    for a given run ID. These dictionary keys are the files names and
    there are potentially many keys that are associated with a run ID.
    For the intended purposes of this function (metadata comparison),
    any file associated with the run ID will have the same metadata as
    any other file associated with the run ID; it doesn't matter which
    one we use.

    Args:
        json_results (dict) - benchmark results
        run_id_list (list) - List of strings of the run-IDs being compared

    Returns:
        run_id_keys (dict) - Dictionary relating run-IDs (five character
        unique IDs) and the key for said run ID in the json_results
        dictionary.
    """
    run_id_keys = {}
    for run_id in run_id_list:
        for key in json_results:
            if run_id in key:
                if run_id not in run_id_keys:
                    run_id_keys[run_id] = key
                    break
    return run_id_keys


def grab_header_metadata(json_results, run_id_keys, param):
    """This function generates a string for use in the metadata header
    that contains the metadata parameter values for each of the run IDs
    being compared. It also determines if parameter values are identical
    across all run IDs.

    Args:
        json_results (dict) - benchmark results
        run_id_keys (list) - list of keys for the json_results dictionary
        that correspond to the run IDs being compared.
        param (str) - metadata parameter value being compared

    Returns:
        header_metadata_str (str) - string of metadata listing all run
        IDs being compared and their values
        diff (bool) - Flag indicating whether any of the metadata
        parameter values differ from each other (True) or if they are
        all identical (False)
    """
    param_value_list = []
    header_metadata_str = ''
    for key, value in run_id_keys.items():
        if param in json_results[value]:
            header_metadata_str = header_metadata_str + '{}: {}\n'.format(
                key, json_results[value][param])
            param_value_list.append(json_results[value][param])
        else:
            header_metadata_str = \
                header_metadata_str + '{}: (value not found)\n'.format(key)
            logging.warning('{} not found in metadata for {}.'.format(
                param, value))
    header_metadata_str = header_metadata_str + '\n'

    # TDH (2020-01-06): Skipping date since that will always (?) be
    # different and doesn't need to be highlighted.
    if param != 'date':
        for value in param_value_list:
            # TDH (2020-01-14)
            # Arbitrarily choosing the first value in the parameter value
            # list as a reference against which all other values are
            # compared. Since all values have to be identical to
            # for diff to be False, it doesn't matter which one we
            # choose as the reference.
            if value == param_value_list[0]:
                diff = False
            else:
                diff = True
                # TDH (2020-01-14)
                # If any of the parameter values are different, we don't
                # need to make any more comparisons.
                break
    else:
        diff = False
    return header_metadata_str, diff


def _auto_run(args):
    """This function executes when the script is called as a stand-alone
    executable. It is used both for development/testing as well as the
    primary executable for generating the cross-run-ID PDF report.
    To use as a stand-alone script (primarily for development purspoes)
    the script has to replicate some of the functionality in
    "cross_run_id.py" to generate json_results for use here.

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
    # TDH (2020-01-14) For developement testing the following section
    # replicates the functionality of "cross_run_id.py" so that
    # json_results can be created and used to create the graph image
    # files.

    import cross_run_id as cri
    import standard_analysis as sa
    import benchmark_postprocessing as bmpp
    import make_dataframe as md
    # TDH (2020-01-14)
    # Hard-coding some inputs for development purposes
    # The "benchmark_results_name" folder and the values in "run_id_list"
    # must be manually made to match.
    benchmark_results_name = '2019-12-02'
    run_id_list = ['aUZF6', 'Zu60n']
    dir_name = 'aUZF6_Zu60n_report'
    comparison_results_root = 'cross_case_comparison'
    delete_report = True
    comparison_parameter = 'mhz_per_cpu'
    parameter_list = [
        'date', 'helics_version', 'generator',
        'system', 'system_version', 'platform',
        'cxx_compiler', 'cxx_compiler_version', 'build_flags_string',
        'host_name', 'host_processor', 'num_cpus',
        'mhz_per_cpu'
    ]

    # TDH (2020-01-14)
    # Generating results path and output path
    script_path = os.path.dirname(os.path.realpath(__file__))
    head, tail = os.path.split(script_path)
    output_dir = os.path.join(head, comparison_results_root)
    output_path = os.path.join(output_dir, dir_name)
    benchmark_results_dir = os.path.join(head,
                                         'benchmark_results',
                                         benchmark_results_name)

    run_id_dict = cri.find_specific_run_id(
        benchmark_results_dir, run_id_list)

    cri.create_output_path(output_path, delete_report)
    file_list = []
    for run_id in run_id_dict:
        file_list.extend(run_id_dict[run_id]['files'])
    bm_files, bmk_files = sa.sort_results_files(file_list)
    file_list = bm_files
    json_results = bmpp.parse_files(file_list)
    json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    meta_bmk_df = md.make_dataframe(json_results)
    bm_list = cri.find_common_bm_to_graph(json_results, run_id_dict)
    for bm in bm_list:
        cri.make_cross_run_id_graphs(
            meta_bmk_df, bm['bm_name'], list(run_id_dict.keys()),
            output_path, comparison_parameter)
    create_cross_run_id_report(
        json_results, run_id_list, output_path, parameter_list)


if __name__ == '__main__':
    fileHandle = logging.FileHandler("cross_run_id_PDF.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])
    parser = argparse.ArgumentParser(description='Generate PDF report.')
    args = parser.parse_args()
    _auto_run(args)
