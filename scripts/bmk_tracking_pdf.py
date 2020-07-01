# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 11:29:43 2020

This script creates a PDF report for tracking the bmk_results
files.

The purpose of this script is to monitor the overall
performance as more runs are done throughout time.  This
allows users to idenitfy potential issues and errors 
created in the runs.

This script can be run as a standalone script.  By default it will not
overwrite any existing report. A "run" is specified by the 5 character
unique ID in the filename for every results file associated with that
run.

The command line arguments for the function can be found in the code
following the lines following the "if __name__ == '__main__':" line
at the end of this file.

@author: barn553
"""

import argparse
import logging
import pprint
import os
import pandas as pd
import sys
from fpdf import FPDF
import standard_analysis as sa
import bmk_plotting
import make_dataframe as md
import hvplot.pandas

# Installation of FPDF is: python -m pip install fpdf

# Setting up logging
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

def create_benchmark_tracking_report(output_path, meta_bmk_df):
    """This function creates the multinode report.
    
    Args:
        output_path (str) - Path where graph images are located and PDF
        report will be saved.
        
        json_results (dict) - benchmark results
    
    Returns:
        (null)
    """
    # Create the PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=8)

    # Define the output path for the report PDF
    report_name = 'benchmark_tracking.pdf'
    report_path = os.path.join(output_path, report_name)

    # Create the header metadata from the metadata in the JSON results
    # and write out to PDF
    header_metadata_str = grab_header_metadata(meta_bmk_df)
    line_height = 3
    pdf.write(line_height, header_metadata_str)

    # Add graphs to PDF object
    pdf = add_benchmark_graphs(pdf, output_path)

    # Output final PDF file from PDF object
    pdf.output(report_path)
    

def grab_header_metadata(meta_bmk_df):
    """This function turns the header metadata to a string to be added
    to the analysis report.

    Args:
        meta_bmk_df (pandas dataframe) - Full dataset

    Returns:
        header_metadata_str (str) - Formatted header metadata for report
    """
    # Setting up the header string
    header_metadata_str = ''
    meta_bmk_df = meta_bmk_df[
        (meta_bmk_df.benchmark_type == 'key') & 
        (meta_bmk_df.benchmark != 'conversionBenchmark') & 
        (meta_bmk_df.mhz_per_cpu >= 3300) &
        (meta_bmk_df.mhz_per_cpu <= 3450)]
    
    # Adding metadata information to lists for the header
    benchmarks = [i for i in meta_bmk_df.benchmark.unique()]
    platforms = [i for i in meta_bmk_df.platform.unique()]
    mhz_per_cpus = sorted([str(i) for i in meta_bmk_df.mhz_per_cpu.unique()])
    
    # Adding all necessary metadata to the header
    header_metadata_str += '{:<25}{}\n'.format(
        'BENCHMARKS:', ', '.join(benchmarks))        
    header_metadata_str += '{:<25}{}\n'.format(
        'generator:', 'Unix Makefiles')
    header_metadata_str += '{:<25}{}\n'.format(
        'system:', 'Linux')
    header_metadata_str += '{:<25}{}\n'.format(
        'system version:', '4.15.0-1052-aws:')
    # header_metadata_str += '{:<25}{}\n'.format(
    #     'platform:', ' ,'.join(platforms))
    header_metadata_str += '{:<25}{}\n'.format('C++ compiler:', 'GNU')
    header_metadata_str += '{:<25}{}\n'.format(
        'C++ compiler version:', '9.2.1')
    header_metadata_str += '{:<25}{}\n'.format('host processor:', 'x86_64')
    header_metadata_str += '{:<25}{}\n'.format('CPU core count:', 36)
    header_metadata_str += '{:<25}{}\n'.format(
        'processor speed (MHz):', ', '.join(mhz_per_cpus))
    header_metadata_str = header_metadata_str + '\n' + '\n'
    logging.info('Final metadata header:\n{}'.format(header_metadata_str))
    return header_metadata_str


def add_benchmark_graphs(pdf, output_path):
    """This function adds the graphs to the PDF object

    Args:
        pdf (PDF obj) - PDF report object
        
        output_path (str) - Path where graph images are located and PDF

    Returns:
        pdf (PDF obj) - PDF report object with graph images included
    """
    for root, dirs, files in os.walk(output_path):
        # TDH (2019-12-23): Trying to keep the graphs in a consistent
        # order so they appear in the report in the same order from report
        # to report.
        files.sort()
        for file in files:
            name, extension = os.path.splitext(file)
            if extension == '.png':
                graph_file_path = os.path.join(output_path, file)
                pdf.image(graph_file_path, x=15, w=175, h=100)
                logging.info('Added graph file {} to PDF'.format(output_path))
    return pdf


def make_benchmark_track_graphs(meta_bmk_df, output_path):
    """This function creates the graphs for the 'tracking' benchmarks'
    data analysis report.
    
    Args:
        meta_bmk_df (pandas dataframe) - Contains all of the 'tracking'
        benchmarks' data.
        
        output_path (str) - Path to send the graphs.
        
    Returns:
        (null)
    """
    meta_bmk_df.date = pd.to_datetime(meta_bmk_df.date)
    meta_bmk_df['DATE'] = [str(d.date()) for d in meta_bmk_df.date]
    for benchmark in meta_bmk_df.benchmark.unique():
        if benchmark == 'echoMessageBenchmark':
            track = meta_bmk_df[meta_bmk_df.benchmark == 'echoMessageBenchmark']
            bmk_plotting.sa_plot(
                track, 'DATE', 'real_time', 
                'tracking', by_bool=True, by_name='core_type', 
                run_id='echoMessage', output_path=output_path)
        elif benchmark == 'echoBenchmark':
            track = meta_bmk_df[meta_bmk_df.benchmark == 'echoBenchmark']
            bmk_plotting.sa_plot(
                track, 'DATE', 'real_time', 
                'tracking', by_bool=True, by_name='core_type', 
                run_id='echo', output_path=output_path)
        elif benchmark == 'messageLookupBenchmark':
            track = meta_bmk_df[meta_bmk_df.benchmark == 'messageLookupBenchmark']
            bmk_plotting.sa_plot(
                track, 'DATE', 'real_time', 
                'tracking', by_bool=True, by_name='core_type', 
                run_id='messageLookup', output_path=output_path)
        elif benchmark == 'timingBenchmark':
            track = meta_bmk_df[meta_bmk_df.benchmark == 'timingBenchmark']
            bmk_plotting.sa_plot(
                track, 'DATE', 'real_time', 
                'tracking', by_bool=True, by_name='core_type', 
                run_id='timing', output_path=output_path)
        else:
            logging.error('Invalid benchmark {}'.format(benchmark))
        

def _auto_run(args):
    """This function executes when the script is called as a stand-alone
    executable. It is used both for development/testing as well as the
    primary executable for generating the benchmark tracking PDF report.

    A more complete description of this code can be found in the
    docstring at the beginning of this file.

    Args:
        '-r' or '--benchmark_results_dir' - Path of top-level folder
        that contains the benchmark results folders/files to be
        processed.
        
        '-j' or '--json_file' - JSON file that contains all the
        benchmark results data to be processed.
        
        '-d' or '--delete_all_reports' - "True" or "False" to indicate
        if existing reports should be over-written.
        
        '-o' or '--output_path' - Path to send the images and the
        benchmark tracking report.
        
    Returns:
        (nothing)
    """
    # Checking whether to delete all reports
    run_id_dict = sa.find_runs(args.benchmark_results_dir)
    run_id_dict = sa.add_report_path(run_id_dict)
    if args.delete_all_reports:
        run_id_dict = sa.remove_all_reports(run_id_dict)
    
    # Creating the report PDF
    meta_bmk_df = md.make_dataframe1(args.json_file)
    conv_df = meta_bmk_df[
        (meta_bmk_df.benchmark == 'conversionBenchmark')]
    meta_bmk_df = meta_bmk_df[
        (meta_bmk_df.benchmark_type == 'key') & 
        (meta_bmk_df.host_processor == 'x86_64') & 
        (meta_bmk_df.system == 'Linux') & 
        (meta_bmk_df.cxx_compiler == 'GNU') & 
        (meta_bmk_df.generator == 'Unix Makefiles') & 
        (meta_bmk_df.system_version == '4.15.0-1052-aws:') & 
        (meta_bmk_df.num_cpus == 36) & 
        (meta_bmk_df.cxx_compiler_version == '9.2.1') & 
        (meta_bmk_df.mhz_per_cpu >= 3300) &
        (meta_bmk_df.mhz_per_cpu <= 3450)]
    output_path = os.path.join(args.output_path)
    make_benchmark_track_graphs(meta_bmk_df, output_path)
    create_benchmark_tracking_report(output_path,
                                     meta_bmk_df)
    # Creating 
    conv_df = conv_df.replace(
        {'run_name': {
            'BM_conversion/double_conv': 'BMconversion/double_conv',
            'BM_conversion/int64_conv': 'BMconversion/int64_conv',
            'BM_conversion/uint64_conv': 'BMconversion/uint64_conv',
            'BM_conversion/int_conv': 'BMconversion/int_conv',
            'BM_conversion/complex_conv': 'BMconversion/complex_conv',
            'BM_conversion/string_conv': 'BMconversion/string_conv',
            'BM_conversion/string_conv_med': 'BMconversion/string_conv_med',
            'BM_conversion/string_conv_long': 'BMconversion/string_conv_long',
            'BM_conversion/vector_conv': 'BMconversion/vector_conv',
            'BM_interpret/double_interp': 'BMinterpret/double_interp',
            'BM_interpret/int64_interp': 'BMinterpret/int64_interp',
            'BM_interpret/uint64_interp': 'BMinterpret/uint64_interp',
            'BM_interpret/int_interp': 'BMinterpret/int_interp',
            'BM_interpret/complex_interp': 'BMinterpret/complex_interp',
            'BM_interpret/string_interp': 'BMinterpret/string_interp',
            'BM_interpret/string_interp_med': 'BMinterpret/string_interp_med',
            'BM_interpret/string_interp_long':
                'BMinterpret/string_interp_long',
            'BM_interpret/vector_interp': 'BMinterpret/vector_interp'}})
    conv_df.date = pd.to_datetime(conv_df.date)
    conv_df['DATE'] = [str(d.date()) for d in conv_df.date]
    conv_df = conv_df.groupby(
                ['run_name', 
                 'DATE', 
                 'benchmark_type'])['real_time'].min().reset_index()
    min_y = conv_df['real_time'].min()
    df1 = conv_df[conv_df.benchmark_type == 'full']
    df2 = conv_df[conv_df.benchmark_type == 'key']
    plot1 = df1.sort_values('DATE').hvplot.line(
        'DATE',
        'real_time',
        ylabel='real_time (s)',
        line_width=3,
        by='run_name',
        rot=90,
        alpha=0.75).opts(
            width=1000, height=550,
            logx=True, logy=True,
            yformatter='%.3f', ylim=(min_y*10.0**(-1), None),
            title='conversion - full: DATE vs real_time', fontsize={
                'title': 8.5, 'labels': 10, 'legend': 6.5,
                'legend_title': 8, 'xticks': 8, 'yticks': 10})
    plot2 = df2.sort_values('DATE').hvplot.line(
        'DATE',
        'real_time',
        ylabel='real_time (s)',
        line_width=3,
        by='run_name',
        rot=90,
        alpha=0.75).opts(
            width=1000, height=550,
            logx=True, logy=True,
            yformatter='%.3f', ylim=(min_y*10.0**(-1), None),
            title='conversion - key: DATE vs real_time', fontsize={
                'title': 8.5, 'labels': 10, 'legend': 6.5,
                'legend_title': 8, 'xticks': 8, 'yticks': 10})
    head, tail = os.path.split(output_path)
    hvplot.save(plot1, os.path.join(head, 'conversion_tracking_full.png'))
    hvplot.save(plot2, os.path.join(head, 'conversion_tracking_key.png'))


if __name__ == '__main__':
    fileHandle = logging.FileHandler("benchmark_tracking_PDF.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])

    # TDH (2020-01-13): Standard argument parsing
    parser = argparse.ArgumentParser(description='Generate PDF report.')
    script_path = os.path.dirname(os.path.realpath(__file__))
    head, tail = os.path.split(script_path)
    benchmark_results_dir = os.path.join(head, 'benchmark_results')
    parser.add_argument('-r',
                        '--benchmark_results_dir',
                        nargs='?',
                        default='../benchmark_results/2019-11-27')
    parser.add_argument('-j',
                        '--json_file',
                        nargs='?',
                        default='bm_results.json')
    parser.add_argument('-d',
                        '--delete_all_reports',
                        nargs='?',
                        default=False)
    args = parser.parse_args()
    default_output_path = os.path.join(head, 'benchmark_tracking')
    parser.add_argument('-o', 
                        '--output_path', 
                        nargs='?',
                        default=default_output_path)
    args = parser.parse_args()
    # TDH (2020-01-13) - Create the PDF for a standard analysis
    _auto_run(args)