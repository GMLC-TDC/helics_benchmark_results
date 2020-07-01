# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 11:10:55 2019

@author: barn553
"""

import numpy as np
import json
import pandas as pd
import os
from functools import reduce
import logging

# Setting up logger
logger = logging.getLogger(__name__)

# Creating benchmarks dataframe.
def make_dataframe1(json_results):
    """This function creates a meta data frame to be used for 
    post-processing the Benchmark Results.
    
    Args:
        json_file (file): json file to be used for creating a dataframe
        
    Returns:
        meta_df: a data frame of all benckmark information
    """
    
    # TDH (2019-12-23): Doing some datatype checking to figure out if we were 
    # passed in a json dictionary (in which case we really need to do little
    # else) or something else. I assume "something else" is a path as a string
    # to a JSON file that contains the results.
#    print('Checking what type "json_results" is...')
    if isinstance(json_results, dict):
        dct = json_results
    else: 
        with open(json_results, 'r') as f:
            dct = json.load(f)
    
    # Getting the benchmarks columns and creating a data frame.
    lists1 = []
    columns1 = [
    'cpu_time', 'core_type', 'filter_location', 'iterations', 
    'name', 'real_time', 'repetition_index', 'repetitions', 
    'run_name', 'run_type', 'threads', 'time_unit', 
    'federate_count', 'interface_count', 'EvCount', 'message_count', 
    'message_size'
    ]
    for f, f_dict in dct.items():
        for i, b_dict in enumerate(f_dict['benchmarks']):
            c_list1 = []
            for c in columns1:
                # If any of the benchmark dictionaries don't have a 
                # column in our columns list, then set the value to np.nan.
                v = b_dict.get(c, np.nan)
                # Append to the list of np.nans.
                c_list1.append(v)
            # Append to lists with our list of np.nans, and columns with 
            # values that belong to our columns list; in other words, if 
            # there IS a value in 'federate_count', append that to lists, 
            # along with c_list.
            lists1.append(np.concatenate([[f, i], c_list1]))
    bmk_df = pd.DataFrame(
        lists1, 
        columns=np.concatenate([['identifier_id', 'benchmark_id'], columns1]))
    
    # Getting the cache data and creating a data frame.
    lists2 = []
    columns2 = ['type', 'level', 'size', 'num_sharing']
    for f, f_dict in dct.items():
        for i, b_dict in enumerate(f_dict['caches']):
            # If any of the caches dictionaries don't have a column in 
            # our columns list, then set the value to np.nan
            c_list2 = []
            for c in columns2:
                # Append to the list of np.nans.
                v = b_dict.get(c, np.nan)
                c_list2.append(v)
            # Append to lists with our list of np.nans, and columns with 
            # values that belong to our columns list; in other words, 
            # if there IS a value in 'type', append that to lists, along 
            # with c_list.
            lists2.append(np.concatenate([[f, i], c_list2]))
    cache_df = pd.DataFrame(
        lists2, 
        columns=np.concatenate([['identifier_id', 'cache_id'], columns2]))
    
    # Getting the general benchmark info and creating a data frame.
    lists3 = []
    columns3 = [
    'filename', 'zmq_version', 'benchmark', 'benchmark_type', 
    'helics_version_string', 'helics_version', 'zmq_version_string', 'path', 
    'compiler_info_string', 'generator', 'system', 'system_version', 
    'platform', 'cxx_compiler', 'cxx_compiler_version', 'build_flags_string', 
    'host_processor', 'host_processor_string', 'date', 'host_name', 
    'executable', 'num_cpus', 'mhz_per_cpu', 'cpu_scaling_enabled', 
    'load_avg', 'library_build_type', 'run_id'
    ]
    for f, f_dict in dct.items():
        c_list3 = []
        for c in columns3:
            # If any of the identifier dictionaries don't have a column 
            # in our columns list, then set the value to np.nan.
            v = f_dict.get(c, np.nan)
            # Append to the list of np.nans.
            c_list3.append(v)
        # Append to lists with our list of np.nans, and columns with 
        # values that belong to our columns list; in other words, 
        # if there IS a value in 'date', append that to lists, along 
        # with c_list.
        lists3.append(np.concatenate([[f, i], c_list3]))
    info_df = pd.DataFrame(
        lists3, 
        columns=np.concatenate([['identifier_id', 'info_id'], columns3]))
    
    # Concatenating all three data frames into one meta data frame
    # and sending to csv.
    meta_bmk_df = reduce(lambda x, y: pd.merge(
        x, y, on='identifier_id', how='outer'), [info_df, cache_df, bmk_df])
    # Converting 'real_time' from nanoseconds or milliseconds to seconds.
    df1 = meta_bmk_df[meta_bmk_df.time_unit == 'ns']
    df2 = meta_bmk_df[meta_bmk_df.time_unit == 'ms']
    df3 = meta_bmk_df[meta_bmk_df.time_unit == 's']
    df1.real_time = df1.real_time.apply(lambda x: float(x)*10**(-9))
    df1.cpu_time = df1.cpu_time.apply(lambda x: float(x)*10**(-9))
    df2.real_time = df2.real_time.apply(lambda x: float(x)*10**(-3))
    df2.cpu_time = df2.cpu_time.apply(lambda x: float(x)*10**(-3))
    df3.real_time = df3.real_time.apply(lambda x: float(x)*1)
    df3.cpu_time = df3.cpu_time.apply(lambda x: float(x)*1)
    meta_bmk_df = pd.concat([df1, df2, df3], axis=0, ignore_index=True)
    # Making sure results have the correct units and are the correct
    # data type
    meta_bmk_df = meta_bmk_df.replace({'time_unit': {'ns': 's',
                                                     'ms': 's'}}).reset_index()
    meta_bmk_df['date'] = pd.to_datetime(meta_bmk_df.date)
    meta_bmk_df['date'] = meta_bmk_df['date'].astype(str)
    meta_bmk_df['federate_count'] = meta_bmk_df['federate_count'].astype(float)
    meta_bmk_df['interface_count'] = meta_bmk_df['interface_count'].astype(float)
    meta_bmk_df['EvCount'] = meta_bmk_df['EvCount'].astype(float)
    meta_bmk_df['message_size'] = meta_bmk_df['message_size'].astype(float)
    meta_bmk_df['message_count'] = meta_bmk_df['message_count'].astype(float)
    return meta_bmk_df


def make_dataframe2(json_results):
    """This function creates a meta data frame to be used for 
    post-processing the Benchmark Results.
    
    Args:
        json_file (file): json file to be used for creating a dataframe
        
    Returns:
        meta_df: a data frame of all benckmark information
    """
    if isinstance(json_results, dict):
        dct = json_results
    else: 
        with open(json_results, 'r') as f:
            dct = json.load(f)
    
    # Getting the general benchmark info and creating a data frame.
    lists = []
    columns = [
    'filename', 'zmq_version', 'mhz_per_cpu', 'cluster',
    'topology', 'number_of_leaves', 'number_of_nodes', 'federate_count',
    'message_size', 'message_count', 'benchmark', 'benchmark_type',
    'helics_version_string', 'helics_version', 'zmq_version_string', 'path', 
    'compiler_info_string', 'generator', 'system', 'system_version', 
    'platform', 'core_type', 'cxx_compiler', 'cxx_compiler_version',
    'build_flags_string', 'host_processor', 'host_processor_string', 'date',
    'run_id', 'elapsed_time', 'time_unit', 'EvCount'
    ]
    for f, f_dict in dct.items():
        for d, d_dict in f_dict.items():
            c_list = []
            for c in columns:
                # If any of the identifier dictionaries don't have a 
                # column in our columns list, then set the value to np.nan.
                v = d_dict.get(c, np.nan)
                # Append to the list of np.nans.
                c_list.append(v)
            # Append to lists with our list of np.nans, and columns 
            # with values that belong to our columns list; in other words, 
            # if there IS a value in 'date', append that to lists, along 
            # with c_list.
            lists.append(np.concatenate([[f], c_list]))
    info_df = pd.DataFrame(
        lists, columns=np.concatenate([['identifier_id'], columns]))
    
    # Concatenating all three data frames into one meta data frame
    # and sending to csv.
    meta_bmk_df = reduce(lambda x, y: pd.merge(
        x, y, on='identifier_id', how='outer'), [info_df])
    # Converting 'elapsed_time' from nanoseconds to seconds.
    meta_bmk_df['elapsed_time'] = meta_bmk_df['elapsed_time'].apply(
        lambda x: float(x)*10**(-9))
    meta_bmk_df = meta_bmk_df.reset_index()
    meta_bmk_df['date'] = pd.to_datetime(meta_bmk_df.date.astype(str))
    meta_bmk_df['date'] = meta_bmk_df['date'].astype(str)
    meta_bmk_df = meta_bmk_df.replace({'time_unit': {'ns': 's', 
                                                     'nan': 's'}})
    meta_bmk_df = meta_bmk_df.replace({'federate_count': {'1.0': 1.0,
                                                          '2.0': 2.0,
                                                          '4.0': 4.0,
                                                          '8.0': 8.0,
                                                          '': np.nan,
                                                          '3.0': 3.0,
                                                          '9.0': 9.0}})
    meta_bmk_df['EvCount'] = meta_bmk_df['EvCount'].astype(float)
    meta_bmk_df['message_size'] = meta_bmk_df['message_size'].astype(float)
    meta_bmk_df['message_count'] = meta_bmk_df['message_count'].astype(float)
    meta_bmk_df['elapsed_time'] = meta_bmk_df['elapsed_time'].astype(float)
    my_list = []
    # Creating a map from "summary.txt" files to the other
    # multinode benchmark results files.
    for g, df in meta_bmk_df.groupby(['path', 'benchmark', 'core_type']):
        a_df = df
        a_df = a_df.set_index('filename')
        try: 
            values = {
                'message_size': float(
                    a_df.loc['summary.txt', 'message_size']), 
                'message_count': float(
                    a_df.loc['summary.txt', 'message_count']), 
                'cluster': str(a_df.loc['summary.txt', 'cluster']), 
                'topology': str(a_df.loc['summary.txt', 'topology']), 
                'number_of_leaves': float(
                    a_df.loc['summary.txt', 'number_of_leaves'])}
            a_df = a_df.fillna(value=values)
        except Exception as e:
            print('{} does not exist for {} benchmark'.format(
                e, a_df.benchmark.values[0]))
        a_df = a_df.reset_index()
        my_list.append(a_df)
    main_df = pd.concat(my_list, axis=0, ignore_index=True)
    return main_df


# Testing that my function works
# if __name__ == '__main__':
#     json_file1 = 'bm_results.json'
#     final_meta_bmk_df = make_dataframe1(json_file1)
#     final_meta_bmk_df.to_csv(r'{}/bmk_df_test.csv'.format(
#         os.path.join(os.getcwd())))
#     json_file2 = 'multinode_bm_results.json'
#     multi_bmk_df = make_dataframe2(json_file2)
#     multi_bmk_df.to_csv(r'{}/multi_bmk_df.csv'.format(
#         os.path.join(os.getcwd())))
#    json_file3 = 'multinode_bm_results_test.json'
#    multi_bmk_df = make_dataframe2(json_file3)
#    print('COLUMNS:', multi_bmk_df.columns.unique())
#    print(final_meta_bmk_df.columns)
#    print(final_meta_bmk_df.head())
#    print(final_meta_bmk_df.shape)
