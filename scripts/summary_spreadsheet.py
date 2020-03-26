# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 07:40:00 2020

@author: barn553
"""

import argparse
import pandas as pd
import numpy as np
import scipy
from scipy.stats import linregress as lr
import logging
import pprint
import os
import shutil
import benchmark_postprocessing as bmpp
import make_dataframe as md
import sys

# Setting up logger
logger = logging.getLogger(__name__)

# Setting up pretty printing, mostly for debugging.
pp = pprint.PrettyPrinter(indent=4)

def get_all_ratios(dataframe):
    """This function gets all the metrics' ratios for the entire dataframe.
    
    Args:
        dataframe (str) - Pandas dataframe object that contains the 
        desired information for calculating metrics' ratios.
    
    Returns:
        final_df (str) - Pandas dataframe that contains the original
        information plus the mterics' ratios' results.
    """
    
    df_list = []
    for benchmark in dataframe.benchmark.unique():
        print('getting ratios for benchmark: ', benchmark)
        if benchmark == 'echoBenchmark':
            echo_df = dataframe[dataframe.benchmark == benchmark]
            echo_lst = []
            for g, df in echo_df.groupby(['benchmark', 'run_id', 
                                          'num_cpus', 'mhz_per_cpu', 
                                          'federate_count']):
                a_df = df
                for f in a_df.federate_count.unique():
                    a_df = a_df[a_df.federate_count == f]
                    a_df = a_df.set_index('core_type')
                    try:
                        a_df['spf_ratio'] = np.ma.array(a_df.spf, mask=np.isnan(a_df.spf))\
                        /float(a_df.loc['inproc', 'spf'])
                        a_df['cpf_ratio'] = np.ma.array(a_df.cpf, mask=np.isnan(a_df.cpf))\
                        /float(a_df.loc['inproc', 'cpf'])
                    except Exception as e:
                        logging.error('core type "{}" does not exist'.format(e))
                        value = np.nan
                        a_df['spf_ratio'] = value
                        a_df['cpf_ratio'] = value
                    a_df = a_df.reset_index()
                    a_df = a_df[[
                            'benchmark', 'run_id', 'num_cpus', 
                            'mhz_per_cpu', 'federate_count', 'core_type', 
                            'real_time', 'spf', 'spf_ratio', 
                            'new_mhz_per_cpu', 'cpf', 'cpf_ratio'
                            ]]
                    echo_lst.append(a_df)
            echo_df = pd.concat(echo_lst).set_index([
                    'benchmark', 'run_id', 
                    'num_cpus', 'mhz_per_cpu',
                    'federate_count', 'core_type', 
                    'real_time'
                    ])
            echo_df = echo_df.reset_index()
            df_list.append(echo_df)
        elif benchmark == 'echoMessageBenchmark':
            echo_msg_df = dataframe[dataframe.benchmark == benchmark]
            echo_msg_lst = []
            for g, df in echo_msg_df.groupby(['benchmark', 'run_id', 
                                              'num_cpus', 'mhz_per_cpu', 
                                              'federate_count']):
                a_df = df
                for f in a_df.federate_count.unique():
                    a_df = a_df[a_df.federate_count == f]
                    a_df = a_df.set_index('core_type')
                    try:
                        a_df['spf_ratio'] = np.ma.array(a_df.spf, mask=np.isnan(a_df.spf))\
                        /float(a_df.loc['inproc', 'spf'])
                        a_df['cpf_ratio'] = np.ma.array(a_df.cpf, mask=np.isnan(a_df.cpf))\
                        /float(a_df.loc['inproc', 'cpf'])
                    except Exception as e:
                        logging.error('core type "{}" does not exist'.format(e))
                        value = np.nan
                        a_df['spf_ratio'] = value
                        a_df['cpf_ratio'] = value
                    a_df = a_df.reset_index()
                    a_df = a_df[[
                            'benchmark', 'run_id', 'num_cpus', 
                            'mhz_per_cpu', 'federate_count', 'core_type', 
                            'real_time', 'spf', 'spf_ratio', 
                            'new_mhz_per_cpu', 'cpf', 'cpf_ratio'
                            ]]
                    echo_msg_lst.append(a_df)
            echo_msg_df = pd.concat(echo_msg_lst).set_index([
                    'benchmark', 'run_id', 
                    'num_cpus', 'mhz_per_cpu',
                    'federate_count', 'core_type', 
                    'real_time'
                    ])
            echo_msg_df = echo_msg_df.reset_index()
            df_list.append(echo_msg_df)
        elif benchmark == 'cEchoBenchmark':
            c_echo_df = dataframe[dataframe.benchmark == benchmark]
            c_echo_lst = []
            for g, df in c_echo_df.groupby(['benchmark', 'run_id', 
                                            'num_cpus', 'mhz_per_cpu', 
                                            'federate_count']):
                a_df = df
                for f in a_df.federate_count.unique():
                    a_df = a_df[a_df.federate_count == f]
                    a_df = a_df.set_index('core_type')
                    try:
                        a_df['spf_ratio'] = np.ma.array(a_df.spf, mask=np.isnan(a_df.spf))\
                        /float(a_df.loc['inproc', 'spf'])
                        a_df['cpf_ratio'] = np.ma.array(a_df.cpf, mask=np.isnan(a_df.cpf))\
                        /float(a_df.loc['inproc', 'cpf'])
                    except Exception as e:
                        logging.error('core type "{}" does not exist'.format(e))
                        value = np.nan
                        a_df['spf_ratio'] = value
                        a_df['cpf_ratio'] = value
                    a_df = a_df.reset_index()
                    a_df = a_df[[
                            'benchmark', 'run_id', 'num_cpus', 
                            'mhz_per_cpu', 'federate_count', 'core_type', 
                            'real_time', 'spf', 'spf_ratio', 
                            'new_mhz_per_cpu', 'cpf', 'cpf_ratio'
                            ]]
                    c_echo_lst.append(a_df)
            c_echo_df = pd.concat(c_echo_lst).set_index([
                    'benchmark', 'run_id', 
                    'num_cpus', 'mhz_per_cpu',
                    'federate_count', 'core_type', 
                    'real_time'
                    ])
            c_echo_df = c_echo_df.reset_index()
            df_list.append(c_echo_df)
        elif benchmark == 'ringBenchmark':
            ring_df = dataframe[dataframe.benchmark == benchmark]
            ring_lst = []
            for g, df in ring_df.groupby(['benchmark', 'run_id', 
                                          'num_cpus', 'mhz_per_cpu', 
                                          'federate_count']):
                a_df = df
                for f in a_df.federate_count.unique():
                    a_df = a_df[a_df.federate_count == f]
                    a_df = a_df.set_index('core_type')
                    try:
                        a_df['spf_ratio'] = np.ma.array(a_df.spf, mask=np.isnan(a_df.spf))\
                        /float(a_df.loc['inproc', 'spf'])
                        a_df['cpf_ratio'] = np.ma.array(a_df.cpf, mask=np.isnan(a_df.cpf))\
                        /float(a_df.loc['inproc', 'cpf'])
                    except Exception as e:
                        logging.error('core type "{}" does not exist'.format(e))
                        value = np.nan
                        a_df['spf_ratio'] = value
                        a_df['cpf_ratio'] = value
                    a_df = a_df.reset_index()
                    a_df = a_df[[
                            'benchmark', 'run_id', 'num_cpus', 
                            'mhz_per_cpu', 'federate_count', 'core_type', 
                            'real_time', 'spf', 'spf_ratio', 
                            'new_mhz_per_cpu', 'cpf', 'cpf_ratio'
                            ]]
                    ring_lst.append(a_df)
            ring_df = pd.concat(ring_lst).set_index([
                    'benchmark', 'run_id', 
                    'num_cpus', 'mhz_per_cpu',
                    'federate_count', 'core_type', 
                    'real_time'
                    ])
            ring_df = ring_df.reset_index()
            df_list.append(ring_df)
        elif benchmark == 'ringMessageBenchmark':
            ring_msg_df = dataframe[dataframe.benchmark == benchmark]
            ring_msg_lst = []
            for g, df in ring_msg_df.groupby(['benchmark', 'run_id', 
                                              'num_cpus', 'mhz_per_cpu', 
                                              'federate_count']):
                a_df = df
                for f in a_df.federate_count.unique():
                    a_df = a_df[a_df.federate_count == f]
                    a_df = a_df.set_index('core_type')
                    try:
                        a_df['spf_ratio'] = np.ma.array(a_df.spf, mask=np.isnan(a_df.spf))\
                        /float(a_df.loc['inproc', 'spf'])
                        a_df['cpf_ratio'] = np.ma.array(a_df.cpf, mask=np.isnan(a_df.cpf))\
                        /float(a_df.loc['inproc', 'cpf'])
                    except Exception as e:
                        logging.error('core type "{}" does not exist'.format(e))
                        value = np.nan
                        a_df['spf_ratio'] = value
                        a_df['cpf_ratio'] = value
                    a_df = a_df.reset_index()
                    a_df = a_df[[
                            'benchmark', 'run_id', 'num_cpus', 
                            'mhz_per_cpu', 'federate_count', 'core_type', 
                            'real_time', 'spf', 'spf_ratio', 
                            'new_mhz_per_cpu', 'cpf', 'cpf_ratio'
                            ]]
                    ring_msg_lst.append(a_df)
            ring_msg_df = pd.concat(ring_msg_lst).set_index([
                    'benchmark', 'run_id', 
                    'num_cpus', 'mhz_per_cpu',
                    'federate_count', 'core_type', 
                    'real_time'
                    ])
            ring_msg_df = ring_msg_df.reset_index()
            df_list.append(ring_msg_df)
        elif benchmark == 'pholdBenchmark':
            phold_df = dataframe[dataframe.benchmark == benchmark]
            phold_lst = []
            for g, df in phold_df.groupby(['benchmark', 'run_id', 
                                           'num_cpus', 'mhz_per_cpu', 
                                           'federate_count']):
                a_df = df
                for f in a_df.federate_count.unique():
                    a_df = a_df[a_df.federate_count == f]
                    a_df = a_df.set_index('core_type')
                    try:
                        a_df['spf_ratio'] = np.ma.array(a_df.spf, mask=np.isnan(a_df.spf))\
                        /float(a_df.loc['inproc', 'spf'])
                        a_df['cpf_ratio'] = np.ma.array(a_df.cpf, mask=np.isnan(a_df.cpf))\
                        /float(a_df.loc['inproc', 'cpf'])
                    except Exception as e:
                        logging.error('core type "{}" does not exist'.format(e))
                        value = np.nan
                        a_df['spf_ratio'] = value
                        a_df['cpf_ratio'] = value
                    a_df = a_df.reset_index()
                    a_df = a_df[[
                            'benchmark', 'run_id', 'num_cpus', 
                            'mhz_per_cpu', 'federate_count', 'core_type', 
                            'real_time', 'spf', 'spf_ratio', 
                            'new_mhz_per_cpu', 'cpf', 'cpf_ratio'
                            ]]
                    phold_lst.append(a_df)
            phold_df = pd.concat(phold_lst).set_index([
                    'benchmark', 'run_id', 
                    'num_cpus', 'mhz_per_cpu',
                    'federate_count', 'core_type', 
                    'real_time'
                    ])
            phold_df = phold_df.reset_index()
            df_list.append(phold_df)
        elif benchmark == 'filterBenchmark':
            filter_df = dataframe[dataframe.benchmark == benchmark]
            filter_lst = []
            for g, df in filter_df.groupby(['benchmark', 'run_id', 
                                            'num_cpus', 'mhz_per_cpu', 
                                            'filter_location', 'federate_count']):
                a_df = df
                for f in a_df.federate_count.unique():
                    a_df = a_df[a_df.federate_count == f]
                    a_df = a_df.set_index('core_type')
                    try:
                        a_df['spf_ratio'] = np.ma.array(a_df.spf, mask=np.isnan(a_df.spf))\
                        /float(a_df.loc['inproc', 'spf'])
                        a_df['cpf_ratio'] = np.ma.array(a_df.cpf, mask=np.isnan(a_df.cpf))\
                        /float(a_df.loc['inproc', 'cpf'])
                    except Exception as e:
                        logging.error('core type "{}" does not exist'.format(e))
                        value = np.nan
                        a_df['spf_ratio'] = value
                        a_df['cpf_ratio'] = value
                    a_df = a_df.reset_index()
                    a_df = a_df[[
                            'benchmark', 'run_id', 'num_cpus', 
                            'mhz_per_cpu', 'filter_location', 'federate_count', 
                            'core_type', 'real_time', 'spf', 
                            'spf_ratio', 'new_mhz_per_cpu', 'cpf', 
                            'cpf_ratio'
                            ]]
                    filter_lst.append(a_df)
            filt_df = pd.concat(filter_lst).set_index([
                    'benchmark', 'run_id', 
                    'num_cpus', 'mhz_per_cpu',
                    'federate_count', 'filter_location', 
                    'core_type', 'real_time'
                    ])
            filt_df = filt_df.reset_index()
            df_list.append(filt_df)
        elif benchmark == 'timingBenchmark':
            time_df = dataframe[dataframe.benchmark == benchmark]
            time_lst = []
            for g, df in time_df.groupby(['benchmark', 'run_id', 
                                          'num_cpus', 'mhz_per_cpu', 
                                          'federate_count']):
                a_df = df
                for f in a_df.federate_count.unique():
                    a_df = a_df[a_df.federate_count == f]
                    a_df = a_df.set_index('core_type')
                    try:
                        a_df['spf_ratio'] = np.ma.array(a_df.spf, mask=np.isnan(a_df.spf))\
                        /float(a_df.loc['inproc', 'spf'])
                        a_df['cpf_ratio'] = np.ma.array(a_df.cpf, mask=np.isnan(a_df.cpf))\
                        /float(a_df.loc['inproc', 'cpf'])
                    except Exception as e:
                        logging.error('core type "{}" does not exist'.format(e))
                        value = np.nan
                        a_df['spf_ratio'] = value
                        a_df['cpf_ratio'] = value
                    a_df = a_df.reset_index()
                    a_df = a_df[[
                            'benchmark', 'run_id', 'num_cpus', 
                            'mhz_per_cpu', 'federate_count', 'core_type', 
                            'real_time', 'spf', 'spf_ratio', 
                            'new_mhz_per_cpu', 'cpf', 'cpf_ratio'
                            ]]
                    time_lst.append(a_df)
            time_df = pd.concat(time_lst).set_index([
                    'benchmark', 'run_id', 
                    'num_cpus', 'mhz_per_cpu',
                    'federate_count', 'core_type', 
                    'real_time'
                    ])
            time_df = time_df.reset_index()
            df_list.append(time_df)
        elif benchmark == 'messageLookupBenchmark':
            msg_lkp_df = dataframe[dataframe.benchmark == 'messageLookupBenchmark']
            msg_lkp_lst = []
            for g, df in msg_lkp_df.groupby(['benchmark', 'run_id', 
                                             'num_cpus', 'mhz_per_cpu', 
                                             'federate_count', 'interface_count']):
                a_df = df
                for a in a_df.interface_count.unique():
                    a_df = a_df[a_df.interface_count == a]
                    a_df = a_df.set_index('core_type')
                    try:
                        a_df['spf_ratio'] = np.ma.array(a_df.spf, mask=np.isnan(a_df.spf))\
                        /float(a_df.loc['inproc', 'spf'])
                        a_df['spi_ratio'] = np.ma.array(a_df.spi, mask=np.isnan(a_df.spi))\
                        /float(a_df.loc['inproc', 'spi'])
                        a_df['cpf_ratio'] = np.ma.array(a_df.cpf, mask=np.isnan(a_df.cpf))\
                        /float(a_df.loc['inproc', 'cpf'])
                        a_df['cpi_ratio'] = np.ma.array(a_df.cpi, mask=np.isnan(a_df.cpi))\
                        /float(a_df.loc['inproc', 'cpi'])
                    except Exception as e:
                        logging.error('core type "{}" does not exist'.format(e))
                        value = np.nan
                        a_df['spf_ratio'] = value
                        a_df['spi_ratio'] = value
                        a_df['cpf_ratio'] = value
                        a_df['cpi_ratio'] = value
                    a_df = a_df.reset_index()
                    a_df = a_df[[
                            'benchmark', 'run_id', 'num_cpus', 
                            'mhz_per_cpu', 'federate_count', 'interface_count', 
                            'core_type', 'real_time', 'spf', 
                            'spf_ratio', 'spi', 'spi_ratio', 
                            'new_mhz_per_cpu', 'cpf', 'cpf_ratio', 
                            'cpi', 'cpi_ratio'
                            ]]
                    msg_lkp_lst.append(a_df)
            msg_lkp_df = pd.concat(msg_lkp_lst).set_index([
                    'benchmark', 'run_id', 
                    'num_cpus', 'mhz_per_cpu',
                    'federate_count', 'interface_count', 
                    'core_type', 'real_time'
                    ])
            msg_lkp_df = msg_lkp_df.reset_index()
            df_list.append(msg_lkp_df)
        elif benchmark == 'messageSendBenchmark':
            msg_send_df = dataframe[dataframe.benchmark == 'messageSendBenchmark']
            msg_send_lst = []
            for g, df in msg_send_df.groupby(['benchmark', 'run_id', 
                                              'num_cpus', 'mhz_per_cpu', 
                                              'message_size', 'message_count']):
                a_df = df
                for a in a_df.message_count.unique():
                    a_df = a_df[a_df.message_count == a]
                    a_df = a_df.set_index('core_type')
                    try:
                        a_df['spms_ratio'] = a_df.spms.values/float(a_df.loc['inproc', 'spms'])
                        a_df['spmc_ratio'] = a_df.spmc.values/float(a_df.loc['inproc', 'spmc'])
                        a_df['cpms_ratio'] = a_df.cpms.values/float(a_df.loc['inproc', 'cpms'])
                        a_df['cpmc_ratio'] = a_df.cpmc.values/float(a_df.loc['inproc', 'cpmc'])
                    except Exception as e:
                        logging.error('core type "{}" does not exist'.format(e))
                        value = np.nan
                        a_df['spms_ratio'] = value
                        a_df['spmc_ratio'] = value
                        a_df['cpms_ratio'] = value
                        a_df['cpmc_ratio'] = value
                    a_df = a_df.reset_index()
                    a_df = a_df[[
                            'benchmark', 'run_id', 'num_cpus', 
                            'mhz_per_cpu', 'message_size', 'message_count', 
                            'core_type', 'real_time', 'spms', 
                            'spmc', 'spms_ratio', 'spmc_ratio', 
                            'new_mhz_per_cpu', 'cpms', 'cpmc', 
                            'cpms_ratio', 'cpmc_ratio'
                            ]]
                    msg_send_lst.append(a_df)
            msg_send_df = pd.concat(msg_send_lst).set_index([
                    'benchmark', 'run_id', 
                    'num_cpus', 'mhz_per_cpu',
                    'message_size', 'message_count', 
                    'core_type', 'real_time'
                    ])
            msg_send_df = msg_send_df.reset_index()
            df_list.append(msg_send_df)
    final_df = pd.concat(df_list, axis=0, ignore_index=True)
    return final_df


def get_slopes(dataframe):
    """This function gets all the slopes for the benchmarks
    and the core_types.
    
    Args:
        dataframe (str) - Pandas dataframe that contains all the 
        desired information along with the results of the
        metrics' ratios' calculations.
    
    Returns:
        slope_df (str) - Pandas dataframe with the original
        desired information, the mterics' ratios' results, and the
        calculated slopes for the metrics' ratios.
    """
    
    fed_bmks = [
            'echoBenchmark', 'ringBenchmark', 
            'echoMessageBenchmark', 'pholdBenchmark', 
            'filterBenchmark', 'cEchoBenchmark', 
            'timingBenchmark', 'ringMessageBenchmark'
            ]
    df_list = []
    for benchmark in dataframe.benchmark.unique():
        print('calculating slopes for benchmark: ', benchmark)
        tf_slopes = []
        ti_slopes = []
        cf_slopes = []
        ci_slopes = []
        tms_ratio_slopes = []
        tmc_ratio_slopes = []
        ms_v_cpms_ratio_slopes = []
        mc_v_cpmc_ratio_slopes = []
        benchmarks = []
        run_ids = []
        core_types = []
        if benchmark in fed_bmks:
            for run_id in dataframe.run_id.unique():
                for core_type in dataframe.core_type.unique():
                    df = dataframe[(dataframe.benchmark == benchmark) &
                                   (dataframe.run_id == run_id) & 
                                   (dataframe.core_type == core_type)]
                    x = np.nan_to_num(np.asarray(df.federate_count))
                    y1 = np.nan_to_num(np.asarray(df.spf_ratio))
                    y2 = np.nan_to_num(np.asarray(df.cpf_ratio))
                    if (len(x) == 0 or 
                        len(y1) == 0 or 
                        len(y2) == 0):
                        continue
                    m1, intercept1, r_value1, p_value1, std_err1 = lr(x, y1)
                    m2, intercept2, r_value2, p_value2, std_err2 = lr(x, y2)
                    tf_slopes.append(m1)
                    cf_slopes.append(m2)
                    benchmarks.append(benchmark)
                    run_ids.append(run_id)
                    core_types.append(core_type)
            an_array = np.empty((1, len(benchmarks)))
            an_array[:] = np.nan
            data = {'benchmark': benchmarks, 
                    'run_id': run_ids, 
                    'core_type': core_types, 
                    'fed_ct_vs_spf_ratio_slope': tf_slopes, 
                    'int_ct_vs_spi_ratio_slope': an_array[0], 
                    'fed_ct_vs_cpf_ratio_slope': cf_slopes, 
                    'int_ct_vs_cpi_ratio_slope': an_array[0], 
                    'msg_size_vs_cpms_ratio_slope': an_array[0],
                    'msg_count_vs_cpmc_ratio_slope': an_array[0],
                    'msg_size_vs_spms_ratio_slope': an_array[0], 
                    'msg_count_vs_spmc_ratio_slope': an_array[0]}
            slope_df = pd.DataFrame(data)
            df_list.append(slope_df)
        elif benchmark not in fed_bmks and benchmark == 'messageLookupBenchmark':
            for run_id in dataframe.run_id.unique():
                for core_type in dataframe.core_type.unique():
                    df = dataframe[(dataframe.benchmark == benchmark) &
                                   (dataframe.run_id == run_id) & 
                                   (dataframe.core_type == core_type)]
                    x1 = np.nan_to_num(np.asarray(df.federate_count))
                    x2 = np.nan_to_num(np.asarray(df.interface_count))
                    y1 = np.nan_to_num(np.asarray(df.spi_ratio))
                    y2 = np.nan_to_num(np.asarray(df.cpi_ratio))
                    y3 = np.nan_to_num(np.asarray(df.spf_ratio))
                    y4 = np.nan_to_num(np.asarray(df.cpf_ratio))
                    if (len(x1) == 0 or 
                        len(x2) == 0 or
                        len(y1) == 0 or 
                        len(y2) == 0 or 
                        len(y3) == 0 or
                        len(y4) == 0):
                        continue
                    m1, intercept1, r_value1, p_value1, std_err1 = lr(x1, y3)
                    m2, intercept2, r_value2, p_value2, std_err2 = lr(x1, y4)
                    m3, intercept3, r_value3, p_value3, std_err3 = lr(x2, y1)
                    m4, intercept4, r_value4, p_value4, std_err4 = lr(x2, y2)
                    tf_slopes.append(m1)
                    cf_slopes.append(m2)
                    ti_slopes.append(m3)
                    ci_slopes.append(m4)
                    benchmarks.append(benchmark)
                    run_ids.append(run_id)
                    core_types.append(core_type)
            an_array = np.empty((1, len(benchmarks)))
            an_array[:] = np.nan
            data = {'benchmark': benchmarks, 
                    'run_id': run_ids, 
                    'core_type': core_types, 
                    'fed_ct_vs_spf_ratio_slope': tf_slopes,
                    'int_ct_vs_spi_ratio_slope': ti_slopes, 
                    'fed_ct_vs_cpf_ratio_slope': cf_slopes, 
                    'int_ct_vs_cpi_ratio_slope': ci_slopes, 
                    'msg_size_vs_real_time_ratio_slope': an_array[0],
                    'msg_count_vs_real_time_ratio_slope': an_array[0],
                    'msg_size_vs_spms_ratio_slope': an_array[0], 
                    'msg_count_vs_spmc_ratio_slope': an_array[0]}
            slope_df = pd.DataFrame(data)
            df_list.append(slope_df)
        elif benchmark not in fed_bmks and benchmark == 'messageSendBenchmark':
            for run_id in dataframe.run_id.unique():
                for core_type in dataframe.core_type.unique():
                    df = dataframe[(dataframe.benchmark == benchmark) &
                                   (dataframe.run_id == run_id) & 
                                   (dataframe.core_type == core_type)]
                    x1 = np.nan_to_num(np.asarray(df.message_size))
                    x2 = np.nan_to_num(np.asarray(df.message_count))
                    y1 = np.nan_to_num(np.asarray(df.spms_ratio))
                    y2 = np.nan_to_num(np.asarray(df.spmc_ratio))
                    y3 = np.nan_to_num(np.asarray(df.cpms_ratio))
                    y4 = np.nan_to_num(np.asarray(df.cpmc_ratio))
                    if (len(x1) == 0 or 
                        len(x2) == 0 or 
                        len(y1) == 0 or 
                        len(y2) == 0 or 
                        len(y3) == 0 or
                        len(y4) == 0):
                        continue
                    m1, intercept1, r_value1, p_value1, std_err1 = lr(x1, y1)
                    m2, intercept2, r_value2, p_value2, std_err2 = lr(x1, y3)
                    m3, intercept3, r_value3, p_value3, std_err3 = lr(x2, y2)
                    m4, intercept4, r_value4, p_value4, std_err4 = lr(x2, y4)
                    tms_ratio_slopes.append(m1)
                    tmc_ratio_slopes.append(m3)
                    ms_v_cpms_ratio_slopes.append(m2)
                    mc_v_cpmc_ratio_slopes.append(m4)
                    benchmarks.append(benchmark)
                    run_ids.append(run_id)
                    core_types.append(core_type)
            an_array = np.empty((1, len(benchmarks)))
            an_array[:] = np.nan
            data = {'benchmark': benchmarks, 
                    'run_id': run_ids, 
                    'core_type': core_types, 
                    'fed_ct_vs_spf_ratio_slope': an_array[0],
                    'int_ct_vs_spi_ratio_slope': an_array[0],
                    'fed_ct_vs_cpf_ratio_slope': an_array[0], 
                    'int_ct_vs_cpi_ratio_slope': an_array[0], 
                    'msg_size_vs_cpms_ratio_slope': ms_v_cpms_ratio_slopes,
                    'msg_count_vs_cpmc_ratio_slope': mc_v_cpmc_ratio_slopes,
                    'msg_size_vs_spms_ratio_slope': tms_ratio_slopes, 
                    'msg_count_vs_spmc_ratio_slope': tmc_ratio_slopes}
            slope_df = pd.DataFrame(data)
            df_list.append(slope_df)
    slope_df = pd.concat(df_list, axis=0, ignore_index=True)
    return slope_df


def create_metrics(dataframe):
    """This function creates/calculates the desired metrics for analysis.
    
    Args:
        dataframe (str) - Pandas dataframe that contains all the 
        desired information for analysis.
        
    Returns:
        main_df (str) - Pandas dataframe that contains the original
        desired information and the new created/calculated metrics to
        be used for analysis.
    """
    
    # Filtering:
    dataframe = dataframe[(dataframe.benchmark_type == 'full') & 
                          (dataframe.benchmark != 'actionMessageBenchmark') & 
                          (dataframe.benchmark != 'conversionBenchmark')]
    ### Making sure there is a one-to-one relationship between real_time
    ### and federate_count, etc.
    fed_cols = [
            'benchmark', 'run_id', 
            'core_type', 'num_cpus', 
            'mhz_per_cpu', 'federate_count', 
            'real_time'
            ]
    fed_groupby_cols = [
            'benchmark', 'run_id', 
            'core_type', 'num_cpus', 
            'mhz_per_cpu', 'federate_count'
            ]
    filt_cols = [
            'benchmark', 'run_id', 
            'core_type', 'num_cpus', 
            'mhz_per_cpu', 'federate_count', 
            'filter_location', 'real_time'
            ]
    filt_groupby_cols = [
            'benchmark', 'run_id', 
            'core_type', 'num_cpus', 
            'mhz_per_cpu', 'federate_count', 
            'filter_location'
            ]
    int_cols = [
            'benchmark', 'run_id', 
            'core_type', 'num_cpus', 
            'mhz_per_cpu', 'federate_count', 
            'interface_count', 'real_time'
            ]
    int_groupby_cols = [
            'benchmark', 'run_id', 
            'core_type', 'num_cpus', 
            'mhz_per_cpu', 'federate_count', 
            'interface_count'
            ]
    msg_cols = [
            'benchmark', 'run_id', 
            'core_type', 'num_cpus', 
            'mhz_per_cpu', 'message_count', 
            'message_size', 'real_time'
            ]
    msg_groupby_cols = [
            'benchmark', 'run_id', 
            'core_type', 'num_cpus', 
            'mhz_per_cpu', 'message_count', 
            'message_size'
            ]
    fed_df = dataframe[fed_cols].groupby(fed_groupby_cols)['real_time'].min()
    fed_df.name = 'real_time'
    fed_df = fed_df.reset_index()
    filt_df = dataframe[filt_cols].groupby(filt_groupby_cols)['real_time'].min()
    filt_df.name = 'real_time'
    filt_df = filt_df.reset_index()
    int_df = dataframe[int_cols].groupby(int_groupby_cols)['real_time'].min()
    int_df.name = 'real_time'
    int_df = int_df.reset_index()
    msg_df = dataframe[msg_cols].groupby(msg_groupby_cols)['real_time'].min()
    msg_df.name = 'real_time'
    msg_df = msg_df.reset_index()
    
    # Calculating metrics:
    fed_df['spf'] = np.ma.array(fed_df.real_time, mask=np.isnan(fed_df.real_time))\
    /np.ma.array(fed_df.federate_count, mask=np.isnan(fed_df.federate_count))
    fed_df['new_mhz_per_cpu'] = np.ma.array(fed_df.mhz_per_cpu, mask=np.isnan(fed_df.mhz_per_cpu))\
    *np.ma.array(fed_df.real_time, mask=np.isnan(fed_df.real_time))
    fed_df['cpf'] = np.ma.array(fed_df.new_mhz_per_cpu, mask=np.isnan(fed_df.new_mhz_per_cpu))\
    *np.ma.array(fed_df.spf, mask=np.isnan(fed_df.spf))
    
    filt_df['spf'] = np.ma.array(filt_df.real_time, mask=np.isnan(filt_df.real_time))\
    /np.ma.array(filt_df.federate_count, mask=np.isnan(filt_df.federate_count))
    filt_df['new_mhz_per_cpu'] = np.ma.array(filt_df.mhz_per_cpu, mask=np.isnan(filt_df.mhz_per_cpu))\
    *np.ma.array(filt_df.real_time, mask=np.isnan(filt_df.real_time))
    filt_df['cpf'] = np.ma.array(filt_df.new_mhz_per_cpu, mask=np.isnan(filt_df.new_mhz_per_cpu))\
    *np.ma.array(filt_df.spf, mask=np.isnan(filt_df.spf))
    
    int_df['spi'] = np.ma.array(int_df.real_time, mask=np.isnan(int_df.real_time))\
    /np.ma.array(int_df.interface_count, mask=np.isnan(int_df.interface_count))
    int_df['spf'] = np.ma.array(int_df.real_time, mask=np.isnan(int_df.real_time))\
    /np.ma.array(int_df.federate_count, mask=np.isnan(int_df.federate_count))
    int_df['new_mhz_per_cpu'] = np.ma.array(int_df.mhz_per_cpu, mask=np.isnan(int_df.mhz_per_cpu))\
    *np.ma.array(int_df.real_time, mask=np.isnan(int_df.real_time))
    int_df['cpi'] = np.ma.array(int_df.new_mhz_per_cpu, mask=np.isnan(int_df.new_mhz_per_cpu))\
    *np.ma.array(int_df.spi, mask=np.isnan(int_df.spi))
    int_df['cpf'] = np.ma.array(int_df.new_mhz_per_cpu, mask=np.isnan(int_df.new_mhz_per_cpu))\
    *np.ma.array(int_df.spf, mask=np.isnan(int_df.spf))
        
    msg_df['spms'] = np.ma.array(msg_df.real_time, mask=np.isnan(msg_df.real_time))\
    /np.ma.array(msg_df.message_size, mask=np.isnan(msg_df.message_size))
    msg_df['spmc'] = np.ma.array(msg_df.real_time, mask=np.isnan(msg_df.real_time))\
    /np.ma.array(msg_df.message_count, mask=np.isnan(msg_df.message_count))
    msg_df['new_mhz_per_cpu'] = np.ma.array(msg_df.mhz_per_cpu, mask=np.isnan(msg_df.mhz_per_cpu))\
    *np.ma.array(msg_df.real_time, mask=np.isnan(msg_df.real_time))
    msg_df['cpms'] = np.ma.array(msg_df.new_mhz_per_cpu, mask=np.isnan(msg_df.new_mhz_per_cpu))\
    *np.ma.array(msg_df.spms, mask=np.isnan(msg_df.spms))
    msg_df['cpmc'] = np.ma.array(msg_df.new_mhz_per_cpu, mask=np.isnan(msg_df.new_mhz_per_cpu))\
    *np.ma.array(msg_df.spmc, mask=np.isnan(msg_df.spmc))
    
    # Combining dataframes into one dataframe
    df1 = pd.merge(
            fed_df, 
            filt_df, 
            how='outer', 
            on=['benchmark', 'run_id', 
                'core_type', 'num_cpus', 
                'mhz_per_cpu', 'real_time', 
                'new_mhz_per_cpu', 'federate_count', 
                'spf', 'cpf'
                ])
    df2 = pd.merge(
            int_df, 
            msg_df, 
            how='outer', 
            on=['benchmark', 'run_id', 
                'core_type', 'num_cpus', 
                'mhz_per_cpu', 'real_time', 
                'new_mhz_per_cpu'
                ])
    df_combo = pd.merge(
            df1, 
            df2, 
            how='outer', 
            on=['benchmark', 'run_id', 
                'core_type', 'num_cpus', 
                'mhz_per_cpu', 'real_time', 
                'new_mhz_per_cpu', 'federate_count', 
                'spf', 'cpf'
                ])
    ratio_df = get_all_ratios(df_combo)
    slope_df = get_slopes(ratio_df)
    print('combining dataframes for creating pivot tables')
    main_df = pd.merge(ratio_df, 
                       slope_df, 
                       how='outer', 
                       on=['benchmark', 'run_id', 'core_type']).fillna(np.nan)
    
    return main_df


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


def create_pivot_tables(dataframe, output_path):
    """This function creates all the pivot tables to send to an Excel
    spreadsheet.
    
    Args:
        dataframe (str) - Final formatted dataframe that contains
        all the information, results/calculations for analysis.
        output_path (str) - Path to send the Excel spreadsheet.
    
    Returns:
        (null)
    """
    # Filtering dataframe to a specific benchmark; helping to prepare
    # for making pivot tables.
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
    
    # Creating pivot_tables:
    p1 = pd.pivot_table(
            c_echo_df, 
            index=['benchmark', 'run_id', 
                   'num_cpus', 'mhz_per_cpu', 
                   'core_type'], 
            values=['spf_ratio', 'cpf_ratio',
                    'fed_ct_vs_cpf_ratio_slope', 'fed_ct_vs_spf_ratio_slope'], 
            aggfunc={'spf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'cpf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'fed_ct_vs_spf_ratio_slope': [np.mean], 
                     'fed_ct_vs_cpf_ratio_slope': [np.mean]})
    p2 = pd.pivot_table(
            echo_res_df, 
            index=['benchmark', 'run_id', 
                   'num_cpus', 'mhz_per_cpu', 
                   'core_type'], 
            values=['spf_ratio', 'cpf_ratio',
                    'fed_ct_vs_cpf_ratio_slope', 'fed_ct_vs_spf_ratio_slope'], 
            aggfunc={'spf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'cpf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'fed_ct_vs_spf_ratio_slope': [np.mean], 
                     'fed_ct_vs_cpf_ratio_slope': [np.mean]})
    p3 = pd.pivot_table(
            echo_msg_df, 
            index=['benchmark', 'run_id', 
                   'num_cpus', 'mhz_per_cpu', 
                   'core_type'], 
            values=['spf_ratio', 'cpf_ratio',
                    'fed_ct_vs_cpf_ratio_slope', 'fed_ct_vs_spf_ratio_slope'], 
            aggfunc={'spf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'cpf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'fed_ct_vs_spf_ratio_slope': [np.mean], 
                     'fed_ct_vs_cpf_ratio_slope': [np.mean]})
    p4 = pd.pivot_table(
            ring_df, 
            index=['benchmark', 'run_id', 
                   'num_cpus', 'mhz_per_cpu', 
                   'core_type'], 
            values=['spf_ratio', 'cpf_ratio',
                    'fed_ct_vs_cpf_ratio_slope', 'fed_ct_vs_spf_ratio_slope'], 
            aggfunc={'spf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'cpf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'fed_ct_vs_spf_ratio_slope': [np.mean], 
                     'fed_ct_vs_cpf_ratio_slope': [np.mean]})
    p5 = pd.pivot_table(
            ring_msg_df, 
            index=['benchmark', 'run_id', 
                   'num_cpus', 'mhz_per_cpu', 
                   'core_type'], 
            values=['spf_ratio', 'cpf_ratio',
                    'fed_ct_vs_cpf_ratio_slope', 'fed_ct_vs_spf_ratio_slope'], 
            aggfunc={'spf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'cpf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'fed_ct_vs_spf_ratio_slope': [np.mean], 
                     'fed_ct_vs_cpf_ratio_slope': [np.mean]})
    p6 = pd.pivot_table(
            phold_df, 
            index=['benchmark', 'run_id', 
                   'num_cpus', 'mhz_per_cpu', 
                   'core_type'], 
            values=['spf_ratio', 'cpf_ratio',
                    'fed_ct_vs_cpf_ratio_slope', 'fed_ct_vs_spf_ratio_slope'], 
            aggfunc={'spf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'cpf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'fed_ct_vs_spf_ratio_slope': [np.mean], 
                     'fed_ct_vs_cpf_ratio_slope': [np.mean]})
    p7 = pd.pivot_table(
            filter_df, 
            index=['benchmark', 'run_id', 
                   'num_cpus', 'mhz_per_cpu', 
                   'filter_location', 'core_type'], 
            values=['spf_ratio', 'cpf_ratio',
                    'fed_ct_vs_cpf_ratio_slope', 'fed_ct_vs_spf_ratio_slope'], 
            aggfunc={'spf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'cpf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'fed_ct_vs_spf_ratio_slope': [np.mean], 
                     'fed_ct_vs_cpf_ratio_slope': [np.mean]})
    p8 = pd.pivot_table(
            timing_df, 
            index=['benchmark', 'run_id', 
                   'num_cpus', 'mhz_per_cpu', 
                   'core_type'], 
            values=['spf_ratio', 'cpf_ratio',
                    'fed_ct_vs_cpf_ratio_slope', 'fed_ct_vs_spf_ratio_slope'], 
            aggfunc={'spf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'cpf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'fed_ct_vs_spf_ratio_slope': [np.mean], 
                     'fed_ct_vs_cpf_ratio_slope': [np.mean]})
    p9 = pd.pivot_table(
            msg_lkp_df, 
            index=['benchmark', 'run_id', 
                   'num_cpus', 'mhz_per_cpu', 
                   'federate_count','core_type'], 
            values=['spf_ratio', 'spi_ratio', 
                    'cpf_ratio', 'cpi_ratio',
                    'fed_ct_vs_spf_ratio_slope', 'int_ct_vs_spi_ratio_slope', 
                    'fed_ct_vs_cpf_ratio_slope', 'int_ct_vs_cpi_ratio_slope'], 
            aggfunc={'spf_ratio': [np.mean, 
                                   relative_standard_deviation],
                     'spi_ratio': [np.mean, 
                                   relative_standard_deviation],
                     'cpf_ratio': [np.mean, 
                                   relative_standard_deviation], 
                     'cpi_ratio': [np.mean, 
                                   relative_standard_deviation],
                     'fed_ct_vs_spf_ratio_slope': [np.mean], 
                     'int_ct_vs_spi_ratio_slope': [np.mean], 
                     'fed_ct_vs_cpf_ratio_slope': [np.mean], 
                     'int_ct_vs_cpi_ratio_slope': [np.mean]})
    p10 = pd.pivot_table(
            msg_send_df, 
            index=['benchmark', 'run_id', 
                   'num_cpus', 'mhz_per_cpu', 
                   'core_type'], 
            values=['spms_ratio', 'spmc_ratio',
                    'cpms_ratio', 'cpmc_ratio', 
                    'msg_size_vs_cpms_ratio_slope', 'msg_count_vs_cpmc_ratio_slope',
                    'msg_size_vs_spms_ratio_slope',  'msg_count_vs_spmc_ratio_slope'], 
            aggfunc={'spms_ratio': [np.mean, 
                                    relative_standard_deviation], 
                     'spmc_ratio': [np.mean, 
                                    relative_standard_deviation],
                     'cpms_ratio': [np.mean, 
                                    relative_standard_deviation], 
                     'cpmc_ratio': [np.mean, 
                                    relative_standard_deviation],  
                     'msg_size_vs_cpms_ratio_slope': [np.mean], 
                     'msg_count_vs_cpmc_ratio_slope': [np.mean], 
                     'msg_size_vs_spms_ratio_slope': [np.mean], 
                     'msg_count_vs_spmc_ratio_slope': [np.mean]})
    print('sending pivot tables to excel spreadsheet')
    with pd.ExcelWriter(os.path.join(output_path, 'benchmark_results_summary.xlsx')) as writer:
        p1.to_excel(writer, sheet_name='cEchoBenchmark')
        p2.to_excel(writer, sheet_name='echoBenchmark')
        p3.to_excel(writer, sheet_name='echoMessageBenchmark')
        p4.to_excel(writer, sheet_name='ringBenchmark')
        p5.to_excel(writer, sheet_name='ringMessageBenchmark')
        p6.to_excel(writer, sheet_name='pholdBenchmark')
        p7.to_excel(writer, sheet_name='filterBenchmark')
        p8.to_excel(writer, sheet_name='timingMessageBenchmark')
        p9.to_excel(writer, sheet_name='messageLookupBenchmark')
        p10.to_excel(writer, sheet_name='messageSendBenchmark')

def _auto_run(args):
    """This function executes when the script is called as a stand-alone
    executable.
    
    Args:
        -j or --json_file (str) - JSON file of all the benchmark results
        data.
        
        -o or --output_path (str) - Path to send the spreadsheet.
    Returns:
        (null)
        
    """
    print('creating the initial dataframe...')
    df = md.make_dataframe1(args.json_file)
    df = create_metrics(df)
    create_pivot_tables(df, args.output_path)
    

if __name__ == '__main__':
    fileHandle = logging.FileHandler("benchmark_results_summary.log", mode='w')
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
#    print(script_path)
    head, tail = os.path.split(script_path)
#    print('head: ', head)
#    print('tail: ', tail)
#    benchmark_summary_dir = os.path.join(head, )
    parser.add_argument('-j', 
                        '--json_file', 
                        nargs='?', 
                        default='bm_results.json')
    parser.add_argument('-o', 
                        '--output_path', 
                        nargs='?', 
                        default=os.path.join(os.getcwd()))
    args = parser.parse_args()
    
    _auto_run(args)