# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 07:40:00 2020

Creates metrics and calculates ratios for analysis
of HELICS performance for a given benchmark.  For each
benchmark, a spreadsheet and csv that summarizes the calculated
metrics and ratios are generated.  A spreadsheet for all 
the benchmarks is created and saved as a single Excel 
spreadsheet and csv file.

This script can be run as a standalone script to generate the summary
spreadsheet for all the benchmarks results.

The command line arguments for the function can be found in the code
following the lines following the "if __name__ == '__main__':" line
at the end of this file.

@author: barn553
"""

import argparse
import pandas as pd
import numpy as np
from scipy.stats import linregress as lr
import logging
import pprint
import os
from make_dataframe import make_dataframe1, make_dataframe2
import sys

# Setting up logger
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

def get_ratio(dataframe, groupby_columns, index_columns, filter_columns,
              value_columns, metric_columns, time):
    """This function gets all the metrics' ratios for the entire dataframe.
    
    Args:
        dataframe (str) - Pandas dataframe object that contains the 
        desired information for calculating metrics' ratios.
        
        groupby_columns (list) - List of columns to group the dataframe
        by.
        
        index_columns (list) - List of columns to set as the index
        after calculating the ratios.
        
        filter_columns (list) - List of columns to filter the grouped
        dataframe by for calculating the ratios.
        
        value_columns (list) - List of specific values to locate in the
        dataframe to be used for the denominator of the ratios.
        
        metric_columns (list) - List of metrics to get ratios for.
        
        time (str) - Used to assert there is a one-to-one relationship
        between a metric value and the time value; should be 'real_time'
        or 'elapsed_time'.
    
    Returns:
        final_df (pandas dataframe) - Contains the original
        information plus the metrics' ratios' results.
    """
    lst = []
    for fs, vs, ms in zip(filter_columns, value_columns, metric_columns):
        for g, df in dataframe.groupby(groupby_columns):
            a_df = df
            for f in a_df['{}'.format(fs)].unique():
                a_df = a_df[a_df['{}'.format(fs)] == f]
                a_df = a_df.set_index('core_type')
                try:
                    a_df['{}_ratio'.format(ms)] = np.ma.array(
                        a_df['{}'.format(ms)], 
                        mask=np.isnan(a_df['{}'.format(ms)]))/float(
                            a_df.loc['{}'.format(vs), 
                                     '{}'.format(ms)])
                    a_df['{}_ratio'.format(time)] = np.ma.array(
                        a_df['{}'.format(time)], 
                        mask=np.isnan(a_df['{}'.format(time)]))/float(
                            a_df.loc['{}'.format(vs), 
                                     '{}'.format(time)])
                except Exception as e:
                    logging.error('core type {} is not in the index'.format(e))
                    a_df['{}_ratio'.format(ms)] = np.nan
                    a_df['{}_ratio'.format(time)] = np.nan
                a_df = a_df.reset_index()
                cols = index_columns+['{}'.format(ms), 
                                      '{}_ratio'.format(ms), 
                                      '{}_ratio'.format(time)]
                a_df = a_df[cols]
                lst.append(a_df)
    ratio_df = pd.concat(lst).set_index(index_columns).reset_index()
    return ratio_df


def get_slopes(dataframe, benchmark, xdatas, ydatas):
    """This function gets all the slopes for the benchmarks
    and the core_types.
    
    Args:
        dataframe (pandas dataframe) - Contains all the 
        desired information along with the results of the
        metrics' ratios' calculations.
        
        benchmark (str) - Specific benchmark to get slopes for.
        
        xdatas (list) - List of values to be considered as x-values
        in a linear regression approach to get the slope.
        
        ydatas (list) - List of values to be considered as y-values
        in a linear regression approach to get the slope.
    
    Returns:
        slope_df (pandas dataframe) - Contains the original
        desired information, the mterics' ratios' results, and the
        calculated slopes for the metrics' ratios.
    """
    df_list = []
    for xs, ys in zip(xdatas, ydatas):
        benchmarks = []
        run_ids = []
        core_types = []
        slopes = []
        for run_id in dataframe.run_id.unique():
            for core_type in dataframe.core_type.unique():
                df = dataframe[(dataframe.run_id == run_id) & 
                               (dataframe.core_type == core_type)]
                x = np.nan_to_num(np.asarray(df['{}'.format(xs)]))
                y = np.nan_to_num(np.asarray(df['{}'.format(ys)]))
                if len(x) == 0 or len(y) == 0:
                    continue
                m, intercept, r_value, p_value, std_err = lr(x, y)
                slopes.append(m)
                benchmarks.append(benchmark)
                run_ids.append(run_id)
                core_types.append(core_type)
        data = {'benchmark': benchmarks, 
                'run_id': run_ids, 
                'core_type': core_types, 
                '{}_vs_{}_slope'.format(xs, ys): slopes}
        df = pd.DataFrame(data, index=[s for s in range(len(slopes))])
        df_list.append(df)
    slope_df = pd.concat(df_list, axis=0, ignore_index=True)
    return slope_df


def create_metrics(dataframe, filter_columns, groupby_columns, metric_names, 
                   columns, operations, time):
    """This function creates/calculates the desired metrics for analysis.
    
    Args:
        dataframe (pandas dataframe) - Contains all the 
        desired information for analysis.
        
        filter_columns (list) - List of columns to use to create a
        subset of the original dataframe.
        
        groupby_columns (list) - List of columns to use to group the
        dataframe subset.
        
        metric_names (list) - List of names for the metrics that are
        to be created/calculated.
        
        columns (list) - List of tuples of columns to use for calculating
        the metrics.
        
        operations (list) - List of mathematical operations to perform
        when calculating the metrics; should be either '*' or '/'.
        
        time (str) - Used for getting a ratio of the times; should be
        'real_time' or 'elapsed_time'.
        
    Returns:
        main_df (pandas dataframe) - Contains the original
        desired information and the new created/calculated metrics to
        be used for analysis.
    """
    # Making sure there is a one-to-one relationship between real_time
    # and federate_count, etc.
    df = dataframe[filter_columns].groupby(
        groupby_columns)['{}'.format(time)].min()
    df.name = '{}'.format(time)
    df = df.reset_index()
    for m, c, o in zip(metric_names, columns, operations):
        if o == '/':
            df['{}'.format(m)] = np.array(df['{}'.format(c[0])])\
                /np.array(df['{}'.format(c[1])]).astype(float)
        elif o == '*':
            df['{}'.format(m)] = np.array(df['{}'.format(c[0])])\
                *np.array(df['{}'.format(c[1])]).astype(float)
        else:
            logging.error('Invalid operation; should be "/" or "*".')
    
    main_df = df
    return main_df


def cpu_score(dataframe, bm_type):
    """This function calculates the CPU Benchmark Score
    for a given dataframe and benchmark type.
    
    Args:
        dataframe (pandas dataframe) - Contains all the information
        for calculating the CPU Benchmark Score.
        
        bm_type (str) - The type of benchmark; 'full', 'key', or 
        'multinode'.
        
    Returns:
        score_df (pandas dataframe) - A dataframe that contains the 
        original information along with the calculates CPU
        benchmark score(s).
    """
    if bm_type == 'full':
        dataframe = dataframe[dataframe.benchmark != 'cEchoBenchmark']
        df_list = []
        for g, df in dataframe.groupby('helics_version_string'):
            score_df = df
            score_df = score_df.set_index('benchmark')
            try:
                fed_scores = [score_df.loc[i, 'spf'].mean()\
                              for i in score_df.index.unique()\
                                  if i != 'messageSendBenchmark']
                cycles = [score_df.loc[i, 'cpf'].mean()\
                          for i in score_df.index.unique()\
                              if i != 'messageSendBenchmark']
                if 'messageSendBenchmark' in score_df.index\
                    and 'messageLookupBenchmark' in score_df.index:
                    spi = score_df.loc['messageLookupBenchmark', 'spi'].mean()
                    cpi = score_df.loc['messageLookupBenchmark', 'cpi'].mean()
                    spms = score_df.loc['messageSendBenchmark', 'spms'].mean()
                    cpms = score_df.loc['messageSendBenchmark', 'cpms'].mean()
                    spmc = score_df.loc['messageSendBenchmark', 'spmc'].mean()
                    cpmc = score_df.loc['messageSendBenchmark', 'cpmc'].mean()
                    all_scores = np.array(
                        fed_scores+cycles+[spi, cpi, spms, cpms, spmc, cpmc])
                    score_df['cpu_score'] = np.round(
                        np.mean((all_scores/(np.median(all_scores)))),
                        decimals=0)
                elif 'messageSendBenchmark' in score_df.index\
                    and 'messageLookupBenchmark' not in score_df.index:
                    spms = score_df.loc['messageSendBenchmark', 'spms'].mean()
                    cpms = score_df.loc['messageSendBenchmark', 'cpms'].mean()
                    spmc = score_df.loc['messageSendBenchmark', 'spmc'].mean()
                    cpmc = score_df.loc['messageSendBenchmark', 'cpmc'].mean()
                    all_scores = np.array(
                        fed_scores+cycles+[spms, cpms, spmc, cpmc])
                    score_df['cpu_score'] = np.round(
                        np.mean((all_scores/(np.median(all_scores)))), 
                        decimals=0)
                elif 'messageSendBenchmark' not in score_df.index\
                    and 'messageLookupBenchmark' in score_df.index:
                    spi = score_df.loc['messageLookupBenchmark', 'spi'].mean()
                    cpi = score_df.loc['messageLookupBenchmark', 'cpi'].mean()
                    all_scores = np.array(fed_scores+cycles+[spi, cpi])
                    score_df['cpu_score'] = np.round(
                        np.mean((all_scores/(np.median(all_scores)))), 
                        decimals=0)
                elif 'messageSendBenchmark' not in score_df.index\
                    and 'messageLookupBenchmark' not in score_df.index:
                    all_scores = np.array(fed_scores+cycles)
                    score_df['cpu_score'] = np.round(
                        np.mean((all_scores/(np.median(all_scores)))), 
                        decimals=0)
                else:
                    logging.error('Failed to calculate score for {}'.format(g))
            except Exception as e:
                logging.error('benchmark {} does not exist'.format(e))
                score_df['cpu_score'] = np.nan
            score_df = score_df.reset_index()
            score_df = score_df[['helics_version_string', 'date', 'benchmark', 
                                 'cpu_score', 'cpf', 'cpi', 
                                 'cpms', 'cpmc', 'spf', 
                                 'spi', 'spmc', 'spms']]
            df_list.append(score_df)
        score_df = pd.concat(df_list).set_index(
            'helics_version_string').reset_index()
    elif bm_type == 'key':
        df_list = []
        for g, df in dataframe.groupby('helics_version_string'):
            score_df = df
            score_df = score_df.set_index('benchmark')
            try:
                fed_scores = [score_df.loc[i, 'spf'].mean()\
                              for i in score_df.index.unique()]
                cycles = [score_df.loc[i, 'cpf'].mean()\
                          for i in score_df.index.unique()]
                if 'messageLookupBenchmark' in score_df.index:
                    spi = score_df.loc['messageLookupBenchmark', 'spi'].mean()
                    cpi = score_df.loc['messageLookupBenchmark', 'cpi'].mean()
                    all_scores = np.array(
                        fed_scores+cycles+[spi, cpi])
                    score_df['cpu_score'] = np.round(
                        np.mean((all_scores/(np.median(all_scores)))),
                        decimals=0)
                elif 'messageLookupBenchmark' not in score_df.index:
                    all_scores = np.array(fed_scores+cycles)
                    score_df['cpu_score'] = np.round(
                        np.mean((all_scores/(np.median(all_scores)))), 
                        decimals=0)
                else:
                    logging.error('Failed to calculate score for {}'.format(g))
            except Exception as e:
                logging.error('benchmark {} does not exist'.format(e))
                score_df['cpu_score'] = np.nan
            score_df = score_df.reset_index()
            score_df = score_df[[
                'helics_version_string', 'date', 'benchmark', 'cpu_score', 
                'cpf', 'cpi', 'spf', 'spi'
                ]]
            df_list.append(score_df)
        score_df = pd.concat(df_list).set_index(
            'helics_version_string').reset_index()
    elif bm_type == 'multinode':
        df_list = []
        for g, df in dataframe.groupby('helics_version_string'):
            score_df = df
            score_df = score_df.set_index('benchmark')
            try:
                fed_scores = [score_df.loc[i, 'spf'].mean()\
                              for i in score_df.index.unique()\
                                  if i != 'MessageExchangeFederate']
                cycles = [score_df.loc[i, 'cpf'].mean()\
                          for i in score_df.index.unique()\
                              if i != 'MessageExchangeFederate']
                if 'MessageExchangeFederate' in score_df.index\
                    and 'PholdFederate' in score_df.index:
                    spe = score_df.loc['PholdFederate', 'spe'].mean()
                    cpe = score_df.loc['PholdFederate', 'cpe'].mean()
                    cpmc = score_df.loc[
                        'MessageExchangeFederate', 'cpmc'].mean()
                    cpms = score_df.loc[
                        'MessageExchangeFederate', 'cpms'].mean()
                    spms = score_df.loc[
                        'MessageExchangeFederate', 'spms'].mean()
                    spmc = score_df.loc[
                        'MessageExchangeFederate', 'spmc'].mean()
                    all_scores = np.array(
                        fed_scores+cycles+[spe, cpe, cpmc, cpms, spms, spmc])
                    score_df['cpu_score'] = np.round(
                        np.mean((all_scores/(np.median(all_scores)))),
                        decimals=0)
                elif 'MessageExchangeFederate' in score_df.index\
                    and 'PholdFederate' not in score_df.index:
                    cpmc = score_df.loc[
                        'MessageExchangeFederate', 'cpmc'].mean()
                    cpms = score_df.loc[
                        'MessageExchangeFederate', 'cpms'].mean()
                    spms = score_df.loc[
                        'MessageExchangeFederate', 'spms'].mean()
                    spmc = score_df.loc[
                        'MessageExchangeFederate', 'spmc'].mean()
                    all_scores = np.array(
                        fed_scores+cycles+[spms, spmc, cpmc, cpms])
                    score_df['cpu_score'] = np.round(
                        np.mean((all_scores/(np.median(all_scores)))), 
                        decimals=0)
                elif 'MessageExchangeFederate' not in score_df.index\
                    and 'PholdFederate' in score_df.index:
                    spe = score_df.loc['PholdFederate', 'spe'].mean()
                    cpe = score_df.loc['PholdFederate', 'cpe'].mean()
                    all_scores = np.array(
                        fed_scores+cycles+[spe, cpe])
                    score_df['cpu_score'] = np.round(
                        np.mean((all_scores/(np.median(all_scores)))), 
                        decimals=0)
                elif 'MessageExchangeFederate' not in score_df.index\
                    and 'messageLookupBenchmark' not in score_df.index:
                    all_scores = np.array(
                        fed_scores+cycles)
                    score_df['cpu_score'] = np.round(
                        np.mean((all_scores/(np.median(all_scores)))), 
                        decimals=0)
                else:
                    logging.error('Failed to calculate score for {}'.format(g))
            except Exception as e:
                logging.error('benchmark {} does not exist'.format(e))
                score_df['cpu_score'] = np.nan
            score_df = score_df.reset_index()
            score_df = score_df[[
                'helics_version_string', 'date', 'benchmark', 'cpu_score', 
                'cpf', 'cpe', 'spf', 'spe', 
                'spmc', 'spms', 'cpms', 'cpmc'
                ]]
            df_list.append(score_df)
        score_df = pd.concat(df_list).set_index(
            'helics_version_string').reset_index()
    else:
        logging.error('Invalid value; should be "full", "key" or "multinode".')
    return score_df


def relative_standard_deviation(x):
    """This function calculates the relative standard deviation;
    simply put, it is a statistical calculation that compares the
    standard deviation in relation to the mean.
    
    Args:
        x (array) - Array of float values for calculating the
        relative standard deviation
    
    Returns:
        np.std(x) / np.mean(x) (float) - The relative standard
        deviation.
    """
    return np.std(x) / np.mean(x)


def create_pivot_tables(dataframe, index_columns, value_columns):
    """This function creates all the pivot tables to send to an Excel
    spreadsheet.
    
    Args:
        dataframe (pandas dataframe) - Final formatted dataframe that 
        contains all the information, results/calculations for analysis.
        
        index_columns (list) - List of columns to be the indices
        for the pivot table.
        
        value_columns (list) - List of metrics for the pivot table
        to compute values; the default computation is mean.
    
    Returns:
        p (pandas pivot table) - Pivot table of the final dataframe.
    """    
    # Creating pivot_tables:
    p = pd.pivot_table(
        dataframe, index=index_columns, values=value_columns, fill_value='')
    return p


def create_spreadsheet1(dataframe, filename, output_path):
    """This function combines all the above functions and
    creates a spreadsheet and csv for 'benchmark_type' = 'full'.
    
    Args:
        dataframe (pandas dataframe) - Contains all the information
        for analysis.
        
        filename (str) - Name of the file for saving the results as
        an excel spreadsheet and csv file.
        
        output_path (str) - Location to send the analysis files.
    
    Returns:
        (null)
    """
    print('Filtering it to just bmk_type = "full"...')
    dataframe = dataframe[(dataframe.benchmark_type == 'full') & 
                          (dataframe.benchmark != 'actionMessageBenchmark') &
                          (dataframe.benchmark != 'conversionBenchmark')]
    c_echo_df = dataframe[dataframe.benchmark == 'cEchoBenchmark']
    echo_res_df = dataframe[dataframe.benchmark == 'echoBenchmark']
    echo_msg_df = dataframe[dataframe.benchmark == 'echoMessageBenchmark']
    msg_lkp_df = dataframe[dataframe.benchmark == 'messageLookupBenchmark']
    msg_send_df = dataframe[dataframe.benchmark == 'messageSendBenchmark']
    ring_df = dataframe[dataframe.benchmark == 'ringBenchmark']
    ring_msg_df = dataframe[dataframe.benchmark == 'ringMessageBenchmark']
    phold_df = dataframe[dataframe.benchmark == 'pholdBenchmark']
    filter_df = dataframe[dataframe.benchmark == 'filterBenchmark']
    timing_df = dataframe[dataframe.benchmark == 'timingBenchmark']
    # Getting all necessary info for the functions
    print('Saving the necessary information to memory...')
    met_fed_cols = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 'core_type', 
        'num_cpus', 'mhz_per_cpu', 'federate_count', 'real_time'
        ]
    met_fed_groupby_cols = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'core_type', 'num_cpus', 'mhz_per_cpu', 'federate_count'
        ]
    met_fed_metrics = ['spf', 'new_mhz_per_cpu', 'cpf']
    met_fed_cols_tuples = [
        ('real_time', 'federate_count'), ('real_time', 'mhz_per_cpu'), 
        ('spf', 'new_mhz_per_cpu')
        ] 
    met_fed_ops = ['/', '*', '*']
    r_fed_groupby_columns = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'num_cpus', 'mhz_per_cpu', 'federate_count'
        ]
    r_fed_index_columns = met_fed_cols
    r_fed_filter_columns = ['federate_count']*2
    r_fed_value_columns = ['inproc']*2
    r_fed_metric_columns = ['spf', 'cpf']
    
    met_filt_cols = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'core_type', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
        'filter_location', 'real_time'
        ]
    met_filt_groupby_cols = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 'core_type', 
        'num_cpus', 'mhz_per_cpu', 'federate_count', 'filter_location'
        ]
    met_filt_metrics = met_fed_metrics
    met_filt_cols_tuples = met_fed_cols_tuples
    met_filt_ops = met_fed_ops
    r_filt_groupby_columns = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'num_cpus', 'mhz_per_cpu', 'filter_location', 'federate_count'
        ]
    r_filt_index_columns = met_filt_cols
    r_filt_filter_columns = r_fed_filter_columns
    r_filt_value_columns = r_fed_value_columns
    r_filt_metric_columns = r_fed_metric_columns
    
    met_int_cols = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'core_type', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
        'interface_count', 'real_time'
        ]
    met_int_groupby_cols = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 'core_type', 
        'num_cpus', 'mhz_per_cpu', 'federate_count', 'interface_count'
        ]
    met_int_metrics = ['spf', 'spi', 'new_mhz_per_cpu', 'cpf', 'cpi']
    met_int_cols_tuples = [
        ('real_time', 'federate_count'), ('real_time', 'interface_count'), 
        ('real_time', 'mhz_per_cpu'), ('spf', 'new_mhz_per_cpu'), 
        ('spi', 'new_mhz_per_cpu')
        ]
    met_int_ops = ['/', '/', '*', '*', '*']
    r_int_groupby_columns = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'num_cpus', 'mhz_per_cpu', 'federate_count', 'interface_count'
        ]
    r_int_index_columns = met_int_cols
    r_int_filter_columns = ['interface_count']*4
    r_int_value_columns = ['inproc']*4
    r_int_metric_columns = ['spf', 'spi', 'cpf', 'cpi']
    
    met_msg_cols = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'core_type', 'num_cpus', 'mhz_per_cpu', 'message_count', 
        'message_size', 'real_time'
        ]
    met_msg_groupby_cols = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 'core_type', 
        'num_cpus', 'mhz_per_cpu', 'message_count', 'message_size'
        ]
    met_msg_metrics = ['spms', 'spmc', 'new_mhz_per_cpu', 'cpms', 'cpmc']
    met_msg_cols_tuples = [
        ('real_time', 'message_size'), ('real_time', 'message_count'), 
        ('real_time', 'mhz_per_cpu'), ('spms', 'new_mhz_per_cpu'), 
        ('spmc', 'new_mhz_per_cpu')
        ]
    met_msg_ops = ['/', '/', '*', '*', '*']
    r_msg_groupby_columns = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'num_cpus', 'mhz_per_cpu', 'message_size', 'message_count'
        ]
    r_msg_index_columns = met_msg_cols
    r_msg_filter_columns = ['message_count']*4
    r_msg_value_columns = ['inproc']*4
    r_msg_metric_columns = ['spms', 'spmc', 'cpms', 'cpmc']
    
    # Applying the functions
    print('Creating the desired metrics and getting the ratios...')
    c_echo_ratio = get_ratio(
        create_metrics(c_echo_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                        'real_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'real_time')
    echo_ratio = get_ratio(
        create_metrics(echo_res_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'real_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'real_time')
    echo_msg_ratio = get_ratio(
        create_metrics(echo_msg_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'real_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'real_time')
    ring_ratio = get_ratio(
        create_metrics(ring_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'real_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'real_time')
    ring_msg_ratio = get_ratio(
        create_metrics(ring_msg_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'real_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'real_time')
    phold_ratio = get_ratio(
        create_metrics(phold_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'real_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'real_time')
    filter_ratio = get_ratio(
        create_metrics(filter_df, met_filt_cols, met_filt_groupby_cols, 
                       met_filt_metrics, met_filt_cols_tuples,  met_filt_ops, 
                       'real_time'),
        r_filt_groupby_columns, r_filt_index_columns, r_filt_filter_columns, 
        r_filt_value_columns, r_filt_metric_columns, 'real_time')
    timing_ratio = get_ratio(
        create_metrics(timing_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'real_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'real_time')
    msg_lkp_ratio = get_ratio(
        create_metrics(msg_lkp_df, met_int_cols, met_int_groupby_cols, 
                       met_int_metrics, met_int_cols_tuples, met_int_ops, 
                       'real_time'),
        r_int_groupby_columns, r_int_index_columns, r_int_filter_columns, 
        r_int_value_columns, r_int_metric_columns, 'real_time')
    msg_send_ratio = get_ratio(
        create_metrics(msg_send_df, met_msg_cols, met_msg_groupby_cols, 
                       met_msg_metrics, met_msg_cols_tuples, met_msg_ops, 
                       'real_time'),
        r_msg_groupby_columns, r_msg_index_columns, r_msg_filter_columns, 
        r_msg_value_columns, r_msg_metric_columns, 'real_time')
    
    print('Calculating CPU benchmark score...')
    ratio_df = pd.concat(
        [c_echo_ratio, echo_msg_ratio, echo_ratio, filter_ratio,
         msg_lkp_ratio, msg_send_ratio, phold_ratio, ring_msg_ratio,
         ring_ratio, timing_ratio], axis=0, ignore_index=True)
    score_df = cpu_score(ratio_df, 'full')
    score_p = create_pivot_tables(
        score_df, 
        ['helics_version_string', 'cpu_score', 'benchmark', 'date'],
        ['cpf', 'cpi', 'cpmc', 'cpms', 'spf', 'spi', 'spmc', 'spms'])
    
    print('Creating the pivot table and saving to excel...')
    c_echo_p = create_pivot_tables(
        c_echo_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    echo_p = create_pivot_tables(
        echo_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    echo_msg_p = create_pivot_tables(
        echo_msg_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    ring_p = create_pivot_tables(
        ring_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    ring_msg_p = create_pivot_tables(
        ring_msg_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    phold_p = create_pivot_tables(
        phold_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    timing_p = create_pivot_tables(
        timing_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    filter_p = create_pivot_tables(
        filter_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    msg_lkp_p = create_pivot_tables(
        msg_lkp_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'spi_ratio', 'cpi_ratio', 'cpf_ratio', 
         'real_time_ratio'])
    msg_send_p = create_pivot_tables(
        msg_send_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'message_size', 
         'message_count', 'core_type'], 
        ['spms_ratio', 'spmc_ratio', 'cpms_ratio', 'cpmc_ratio', 
         'real_time_ratio'])
    file_path = os.path.join(output_path, '{}.xlsx'.format(filename))
    with pd.ExcelWriter(file_path) as writer:
        score_p.to_excel(writer, 
                         sheet_name='CPU Benchmark Score')
        c_echo_p.to_excel(writer, 
                          sheet_name='{}'.format('cEchoBenchmark'))
        echo_p.to_excel(writer, 
                        sheet_name='{}'.format('echoBenchmark'))
        echo_msg_p.to_excel(writer, 
                            sheet_name='{}'.format('echoMessageBenchmark'))
        ring_p.to_excel(writer, 
                        sheet_name='{}'.format('ringBenchmark'))
        ring_msg_p.to_excel(writer, 
                            sheet_name='{}'.format('ringMessageBenchmark'))
        phold_p.to_excel(writer, 
                         sheet_name='{}'.format('pholdBenchmark'))
        timing_p.to_excel(writer, 
                          sheet_name='{}'.format('timingBenchmark'))
        filter_p.to_excel(writer, 
                          sheet_name='{}'.format('filterBenchmark'))
        msg_lkp_p.to_excel(writer, 
                           sheet_name='{}'.format('messageLookupBenchmark'))
        msg_send_p.to_excel(writer, 
                            sheet_name='{}'.format('messageSendBenchmark'))
    print('Successfully saved the data to excel.')
    
    print('Saving data as .csv file...')
    main_df = pd.merge(
        ratio_df, score_df, how='outer', on=[
            'benchmark', 'helics_version_string', 'date', 'cpi', 
            'cpf', 'cpmc', 'cpms', 'spf', 
            'spi', 'spmc', 'spms'
            ])
    main_df.to_csv(r'{}\{}.csv'.format(os.path.join(output_path), filename))
    print('Successfully saved data as .csv file.')

def create_spreadsheet2(dataframe, filename, output_path):
    """This function combines all the above functions and
    creates a spreadsheet and csv for 'benchmark_type' = 'key'.
    
    Args:
        dataframe (pandas dataframe) - Contains all the information
        for analysis.
        
        filename (str) - Name of the file for saving the results as
        an excel spreadsheet and csv file.
        
        output_path (str) - Location to send the analysis files.
    
    Returns:
        (null)
    """
    print('Filtering it to just bmk_type = "key"...')
    dataframe = dataframe[(dataframe.benchmark_type == 'key') &
                          (dataframe.benchmark != 'conversionBenchmark')]
    echo_res_df = dataframe[dataframe.benchmark == 'echoBenchmark']
    echo_msg_df = dataframe[dataframe.benchmark == 'echoMessageBenchmark']
    msg_lkp_df = dataframe[dataframe.benchmark == 'messageLookupBenchmark']
    timing_df = dataframe[dataframe.benchmark == 'timingBenchmark']
    # Getting all necessary info for the functions
    print('Saving the necessary information to memory...')
    met_fed_cols = [
        'benchmark', 'helics_version_string', 'date',
        'run_id', 'core_type', 'num_cpus', 
        'mhz_per_cpu', 'federate_count', 'real_time'
        ]
    met_fed_groupby_cols = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'core_type', 'num_cpus', 'mhz_per_cpu', 'federate_count'
        ]
    met_fed_metrics = ['spf', 'new_mhz_per_cpu', 'cpf']
    met_fed_cols_tuples = [('real_time', 'federate_count'), 
                           ('real_time', 'mhz_per_cpu'), 
                           ('spf', 'new_mhz_per_cpu')] 
    met_fed_ops = ['/', '*', '*']
    r_fed_groupby_columns = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'num_cpus', 'mhz_per_cpu', 'federate_count']
    r_fed_index_columns = met_fed_cols
    r_fed_filter_columns = ['federate_count']*2
    r_fed_value_columns = ['inproc']*2
    r_fed_metric_columns = ['spf', 'cpf']
    
    met_int_cols = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'core_type', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
        'interface_count', 'real_time'
        ]
    met_int_groupby_cols = [
        'benchmark', 'helics_version_string', 'date', 
        'run_id', 'core_type', 'num_cpus', 
        'mhz_per_cpu', 'federate_count', 'interface_count'
        ]
    met_int_metrics = ['spf', 'spi', 'new_mhz_per_cpu', 'cpf', 'cpi']
    met_int_cols_tuples = [('real_time', 'federate_count'), 
                           ('real_time', 'interface_count'), 
                           ('real_time', 'mhz_per_cpu'), 
                           ('spf', 'new_mhz_per_cpu'), 
                           ('spi', 'new_mhz_per_cpu')]
    met_int_ops = ['/', '/', '*', '*', '*']
    r_int_groupby_columns = [
        'benchmark', 'helics_version_string', 'date', 'run_id', 
        'num_cpus', 'mhz_per_cpu', 'federate_count', 'interface_count'
        ]
    r_int_index_columns = met_int_cols
    r_int_filter_columns = ['interface_count']*4
    r_int_value_columns = ['inproc']*4
    r_int_metric_columns = ['spf', 'spi', 'cpf', 'cpi']
    
    # Applying the functions
    print('Creating the desired metrics and getting the ratios...')
    echo_ratio = get_ratio(
        create_metrics(echo_res_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'real_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'real_time')
    echo_msg_ratio = get_ratio(
        create_metrics(echo_msg_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'real_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'real_time')
    timing_ratio = get_ratio(
        create_metrics(timing_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'real_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'real_time')
    msg_lkp_ratio = get_ratio(
        create_metrics(msg_lkp_df, met_int_cols, met_int_groupby_cols, 
                       met_int_metrics, met_int_cols_tuples, met_int_ops, 
                       'real_time'),
        r_int_groupby_columns, r_int_index_columns, r_int_filter_columns, 
        r_int_value_columns, r_int_metric_columns, 'real_time')
    
    print('Calculating CPU benchmark score...')
    ratio_df = pd.concat(
        [echo_msg_ratio, echo_ratio, msg_lkp_ratio, timing_ratio], 
        axis=0, 
        ignore_index=True)
    score_df = cpu_score(ratio_df, 'key')
    score_p = create_pivot_tables(
        score_df, 
        ['helics_version_string', 'cpu_score', 'benchmark', 'date'],
        ['cpf', 'cpi', 'spf', 'spi'])
    
    print('Creating the pivot table and saving to excel...')
    echo_p = create_pivot_tables(
        echo_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    echo_msg_p = create_pivot_tables(
        echo_msg_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    timing_p = create_pivot_tables(
        timing_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'cpf_ratio', 'real_time_ratio'])
    msg_lkp_p = create_pivot_tables(
        msg_lkp_ratio, 
        ['benchmark', 'run_id', 'num_cpus', 'mhz_per_cpu', 'federate_count', 
         'core_type'], 
        ['spf_ratio', 'spi_ratio', 'cpi_ratio', 'cpf_ratio', 
         'real_time_ratio'])
    file_path = os.path.join(output_path, '{}.xlsx'.format(filename))
    with pd.ExcelWriter(file_path) as writer:
        score_p.to_excel(writer, 
                         sheet_name='CPU Benchmark Score')
        echo_p.to_excel(writer, 
                        sheet_name='{}'.format('echoBenchmark'))
        echo_msg_p.to_excel(writer, 
                            sheet_name='{}'.format('echoMessageBenchmark'))
        timing_p.to_excel(writer, 
                          sheet_name='{}'.format('timingBenchmark'))
        msg_lkp_p.to_excel(writer, 
                           sheet_name='{}'.format('messageLookupBenchmark'))
    print('Successfully saved the data to excel.')
    
    print('Saving data as .csv file...')
    main_df = pd.merge(
        ratio_df, score_df, how='outer', on=[
            'benchmark', 'helics_version_string', 'date', 'cpi', 
            'cpf', 'spf', 'spi'
            ])
    main_df.to_csv(r'{}\{}.csv'.format(os.path.join(output_path), filename))
    print('Successfully saved data as .csv file.')
        
def create_spreadsheet3(dataframe, filename, output_path):
    """This function combines all the above functions and
    creates a spreadhsheet and for multinode benchmark results.
    
    Args:
        dataframe (pandas dataframe) - Contains all the information
        for analysis.
        
        filename (str) - Name of the file for saving the results as
        an excel spreadsheet and csv file.
        
        output_path (str) - Location to send the analysis files.
    
    Returns:
        (null)
    """
    print('Processing data for multinode benchmark results...')
    echo_df = dataframe[dataframe.benchmark == 'EchoLeafFederate']
    echo_msg_df = dataframe[dataframe.benchmark == 'EchoMessageLeafFederate']
    msg_df = dataframe[dataframe.benchmark == 'MessageExchangeFederate']
    phold_df = dataframe[dataframe.benchmark == 'PholdFederate']
    ring_df = dataframe[dataframe.benchmark == 'RingTransmitFederate']
    timing_df = dataframe[dataframe.benchmark == 'TimingLeafFederate']
    # Getting all necessary info for the functions
    print('Saving the necessary information to memory...')
    met_fed_cols = [
        'benchmark', 'helics_version_string', 'date', 'mhz_per_cpu', 
        'core_type', 'federate_count', 'elapsed_time'
        ]
    met_fed_groupby_cols = [
        'benchmark', 'helics_version_string', 'date', 
        'mhz_per_cpu', 'core_type', 'federate_count'
        ]
    met_fed_metrics = ['spf', 'new_mhz_per_cpu', 'cpf']
    met_fed_cols_tuples = [('elapsed_time', 'federate_count'), 
                           ('elapsed_time', 'mhz_per_cpu'), 
                           ('spf', 'new_mhz_per_cpu')] 
    met_fed_ops = ['/', '*', '*']
    r_fed_groupby_columns = [
        'benchmark', 'helics_version_string', 'date', 
        'mhz_per_cpu', 'federate_count'
        ]
    r_fed_index_columns = met_fed_cols
    r_fed_filter_columns = ['federate_count']*2
    r_fed_value_columns = ['tcp']*2
    r_fed_metric_columns = ['spf', 'cpf']
    
    met_p_cols = [
        'benchmark', 'helics_version_string', 'date', 'core_type', 
        'mhz_per_cpu', 'federate_count', 'EvCount', 'elapsed_time'
        ]
    met_p_groupby_cols = [
        'benchmark', 'helics_version_string', 'date', 'core_type', 
        'mhz_per_cpu', 'federate_count', 'EvCount'
        ]
    met_p_metrics = ['spf', 'spe', 'new_mhz_per_cpu', 'cpf', 'cpe']
    met_p_cols_tuples = [('elapsed_time', 'federate_count'), 
                         ('elapsed_time', 'EvCount'), 
                         ('elapsed_time', 'mhz_per_cpu'), 
                         ('spf', 'new_mhz_per_cpu'), 
                         ('spe', 'new_mhz_per_cpu')] 
    met_p_ops = ['/', '/', '*', '*', '*']
    r_p_groupby_columns = [
        'benchmark', 'helics_version_string', 'date', 
        'mhz_per_cpu', 'federate_count', 'EvCount'
        ]
    r_p_index_columns = met_fed_cols
    r_p_filter_columns = ['federate_count']*4
    r_p_value_columns = ['tcp']*4
    r_p_metric_columns = ['spf', 'spe', 'cpf', 'cpe']
    
    met_msg_cols = [
        'benchmark', 'helics_version_string', 'date', 'core_type', 
        'mhz_per_cpu', 'message_count', 'message_size', 'elapsed_time'
        ]
    met_msg_groupby_cols = [
        'benchmark', 'helics_version_string', 'date', 'core_type', 
        'mhz_per_cpu','message_count', 'message_size'
        ]
    met_msg_metrics = ['spms', 'spmc', 'new_mhz_per_cpu', 'cpms', 'cpmc']
    met_msg_cols_tuples = [('elapsed_time', 'message_size'), 
                           ('elapsed_time', 'message_count'), 
                           ('elapsed_time', 'mhz_per_cpu'), 
                           ('spms', 'new_mhz_per_cpu'), 
                           ('spmc', 'new_mhz_per_cpu')]
    met_msg_ops = ['/', '/', '*', '*', '*']
    r_msg_groupby_columns = [
        'benchmark', 'helics_version_string', 'date', 
        'mhz_per_cpu', 'message_size', 'message_count']
    r_msg_index_columns = met_msg_cols
    r_msg_filter_columns = ['message_count']*4
    r_msg_value_columns = ['tcp']*4
    r_msg_metric_columns = ['spms', 'spmc', 'cpms', 'cpmc']
    
    # Applying the functions
    print('Creating the desired metrics and getting the ratios...')
    echo_ratio = get_ratio(
        create_metrics(echo_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'elapsed_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'elapsed_time')
    echo_msg_ratio = get_ratio(
        create_metrics(echo_msg_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'elapsed_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'elapsed_time')
    timing_ratio = get_ratio(
        create_metrics(timing_df, met_fed_cols, met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'elapsed_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'elapsed_time')
    ring_ratio = timing_ratio = get_ratio(
        create_metrics(ring_df, met_fed_cols,  met_fed_groupby_cols, 
                       met_fed_metrics, met_fed_cols_tuples, met_fed_ops, 
                       'elapsed_time'),
        r_fed_groupby_columns, r_fed_index_columns, r_fed_filter_columns, 
        r_fed_value_columns, r_fed_metric_columns, 'elapsed_time')
    msg_ratio = get_ratio(
        create_metrics(msg_df, met_msg_cols, met_msg_groupby_cols, 
                       met_msg_metrics, met_msg_cols_tuples, met_msg_ops, 
                       'elapsed_time'),
        r_msg_groupby_columns, r_msg_index_columns, r_msg_filter_columns, 
        r_msg_value_columns, r_msg_metric_columns, 'elapsed_time')
    phold_ratio = get_ratio(
        create_metrics(phold_df, met_p_cols, met_p_groupby_cols, 
                       met_p_metrics, met_p_cols_tuples, met_p_ops, 
                       'elapsed_time'),
        r_p_groupby_columns, r_p_index_columns, r_p_filter_columns, 
        r_p_value_columns, r_p_metric_columns, 'elapsed_time')
    print('Calculating CPU benchmark score...')
    ratio_df = pd.concat(
        [echo_msg_ratio, echo_ratio, msg_ratio, 
          phold_ratio, ring_ratio, timing_ratio], axis=0, ignore_index=True)
    score_df = cpu_score(ratio_df, 'multinode')
    score_p = create_pivot_tables(
        score_df, 
        ['helics_version_string', 'cpu_score', 'benchmark', 'date'],
        ['cpf', 'cpe', 'cpmc', 'cpms', 'spf', 'spe', 'spmc', 'spms'])
    
    print('Creating the pivot table and saving to excel...')
    echo_p = create_pivot_tables(
        echo_ratio, 
        ['benchmark', 'federate_count', 'core_type'], 
        ['spf_ratio', 'elapsed_time_ratio'])
    echo_msg_p = create_pivot_tables(
        echo_msg_ratio, 
        ['benchmark', 'federate_count', 'core_type'], 
        ['spf_ratio', 'elapsed_time_ratio'])
    timing_p = create_pivot_tables(
        timing_ratio, 
        ['benchmark', 'federate_count', 'core_type'], 
        ['spf_ratio', 'elapsed_time_ratio'])
    ring_p = create_pivot_tables(
        ring_ratio, 
        ['benchmark', 'federate_count', 'core_type'], 
        ['spf_ratio', 'elapsed_time_ratio'])
    phold_p = create_pivot_tables(
        phold_ratio, 
        ['benchmark', 'federate_count', 'core_type'], 
        ['spf_ratio', 'spe_ratio', 'cpf_ratio', 'cpe_ratio', 
          'elapsed_time_ratio'])
    msg_p = create_pivot_tables(
        msg_ratio, 
        ['benchmark', 'message_size', 'message_count', 'core_type'], 
        ['spms_ratio', 'spmc_ratio', 'elapsed_time_ratio'])
    file_path = os.path.join(output_path, '{}.xlsx'.format(filename))
    with pd.ExcelWriter(file_path) as writer:
        score_p.to_excel(writer, 
                          sheet_name='CPU Benchmark Score')
        echo_p.to_excel(writer, 
                        sheet_name='{}'.format('EchoLeafFederate'))
        echo_msg_p.to_excel(writer, 
                            sheet_name='{}'.format('EchoMessageLeafFederate'))
        ring_p.to_excel(writer, 
                        sheet_name='{}'.format('RingTransmitFederate'))
        timing_p.to_excel(writer, 
                          sheet_name='{}'.format('TimingLeafFederate'))
        phold_p.to_excel(writer, 
                          sheet_name='{}'.format('PholdFederate'))
        msg_p.to_excel(writer, 
                        sheet_name='{}'.format('MessageExchangeFederate'))
            
    print('Successfully saved the data to excel.')
    
    print('Saving data as .csv file.')
    main_df = pd.merge(ratio_df, score_df, how='outer', on=[
        'benchmark', 'helics_version_string', 'date', 'cpe', 
            'cpf', 'spf', 'cpmc', 'cpms',
            'spe', 'spmc', 'spms'])
    main_df.to_csv(r'{}\{}.csv'.format(os.path.join(output_path), filename))
    print('Successfully saved data as .csv file.')
    
    
def create_table(
        dataframe, drop_columns, subset_columns, output_path, filename):
    """This function creates a metadata reference table for
    each run-id in the (multinode) benchmark results files.
    
    Args:
        dataframe (pandas dataframe) - Contains all the information
        for each run-id.
        
        drop_columns (list) - List of columns to ignore in the reference
        table; the summary spreadsheet/csv contains counts and metrics,
        which we don't need for the reference table.
        
        subset_columns (list) - List of columns for creating a subset
        for getting rid of duplicates.
        
        output_path (path) - Path to send the reference table.
        
        filename (str) - Name of the reference table.
        
    Returns:
        (null)
    """
    dataframe = dataframe.drop(columns=drop_columns)
    dataframe = dataframe.sort_values(subset_columns).set_index(
        subset_columns).reset_index()
    dataframe = dataframe.drop_duplicates(
        subset=subset_columns, keep='last')
    dataframe.index = list(range(len(dataframe.run_id)))
    # dataframe = dataframe.set_index('index').reset_index()
    dataframe.to_csv(r'{}\{}.csv'.format(output_path, filename))


def _auto_run(args):
    """This function executes when the script is called as a stand-alone
    executable.  It is used both for development/testing as well as the
    primary executable for generating the results summary files.

    A more complete description of this code can be found in the
    docstring at the beginning of this file.
    
    Args:
        '-b' or '--bmk_type' - Identifier for type of summary results
        should be produced; should be "full", "key", or "multinode" and
        "json_file" should be changed accordingly.
        
        '-j' or '--json_file' - JSON file of all the benchmark results
        data.
        
        '-o' or '--output_path' - Path to send the spreadsheet.
    Returns:
        (null)
        
    """
    if args.bmk_type == 'full':
        print('Creating the meta benchmark dataframe...')
        dataframe = make_dataframe1(args.json_file)
        create_spreadsheet1(dataframe, 
                            'full_benchmark_results_summary', 
                            args.output_path)
        dataframe = dataframe[
            (dataframe.benchmark_type == 'full') & 
            (dataframe.benchmark != 'actionMessageBenchmark') &
            (dataframe.benchmark != 'conversionBenchmark')
            ]
        create_table(
            dataframe, 
            ['federate_count', 'EvCount', 'interface_count', 
             'message_size', 'message_count', 'real_time', 'cpu_time', 
             'info_id', 'benchmark_id', 'cache_id', 'executable', 
             'name', 'identifier_id', 'benchmark', 'core_type', 
             'filename', 'run_name'], 
            ['run_id'],
            args.output_path, 
            'bmk_type_full_metadata')
    elif args.bmk_type == 'key':
        print('Creating the meta benchmark dataframe...')
        dataframe = make_dataframe1(args.json_file)
        create_spreadsheet2(dataframe, 
                            'key_benchmark_results_summary', 
                            args.output_path)
        dataframe = dataframe[
            (dataframe.benchmark_type == 'key') &
            (dataframe.benchmark != 'conversionBenchmark')
            ]
        create_table(
            dataframe, 
            ['federate_count', 'EvCount', 'interface_count', 
             'message_size', 'message_count', 'real_time', 'cpu_time', 
             'info_id', 'benchmark_id', 'cache_id', 'executable', 
             'name', 'identifier_id', 'benchmark', 'core_type', 
             'filename', 'run_name'], 
            ['run_id'],
            args.output_path, 
            'bmk_type_key_metadata')
    elif args.bmk_type == 'multinode':
        print('Creating the meta benchmark dataframe...')
        dataframe = make_dataframe2(args.json_file)
        create_spreadsheet3(dataframe, 
                            'multinode_benchmark_results_summary', 
                            args.output_path)
        create_table(
            dataframe, 
            ['index', 'federate_count', 'EvCount', 'message_size', 
             'message_count', 'elapsed_time', 'benchmark_type', 'identifier_id', 
             'benchmark', 'core_type', 'filename'], 
            ['run_id'],
            args.output_path, 
            'multinode_metadata')
    else:
        logging.error(
            'Invalid; bmk_type should be "full", "key", or "multinode".')
    

if __name__ == '__main__':
    fileHandle = logging.FileHandler(
        "benchmark_results_summary.log", mode='w')
    fileHandle.setLevel(logging.DEBUG)
    streamHandle = logging.StreamHandler(sys.stdout)
    streamHandle.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO,
                        handlers=[fileHandle, streamHandle])

    parser = argparse.ArgumentParser(description='Produce results summary.')
    # TDH: Have to do a little bit of work to generate a good default
    # path for the results folder. Default only works if being run
    # from the "scripts" directory in the repository structure.
    script_path = os.path.dirname(os.path.realpath(__file__))
    head, tail = os.path.split(script_path)
#    benchmark_summary_dir = os.path.join(head, )
    parser.add_argument('-j', 
                        '--json_file', 
                        nargs='?', 
                        default='multinode_bm_results.json')
    parser.add_argument('-b', 
                        '--bmk_type', 
                        nargs='?', 
                        default='multinode')
    parser.add_argument('-o', 
                        '--output_path', 
                        nargs='?', 
                        default=os.path.join(head, 
                                             'summary_spreadsheets'))
    args = parser.parse_args()
    _auto_run(args)