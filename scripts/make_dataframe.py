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
import benchmark_postprocessing as bmpp


### TODO: turn these into function(s) and figure out how to combine them
### into one meta-data frame.
### Creating benchmarks dataframe.

def make_dataframe1(json_results):
    """This function creates a meta data frame to be used for 
    post-processing the Benchmark Results.
    
    Args:
        json_file (file): json file to be used for creating a dataframe
        
    Returns:
        meta_df: a data frame of all benckmark information
    """
    
    # TDH (2019-12-23): Doing some datatype checking to figure out if we were 
    #   passed in a json dictionary (in which case we really need to do little
    #   else) or something else. I assume "something else" is a path as a string
    #   to a JSON file that contains the results.
    if isinstance(json_results, dict):
        dct = json_results
    else: 
        with open(json_results, 'r') as f:
            dct = json.load(f)
    # pprint(f_dict)
    
    ### Getting the benchmarks columns and creating a data frame.
    lists1 = []
    columns1 = [
    'cpu_time', 
    'core_type', 
    'filter_location',
    'iterations', 
    'name', 
    'real_time', 
    'repetition_index', 
    'repetitions', 
    'run_name', 
    'run_type', 
    'threads', 
    'time_unit', 
    'federate_count', 
    'interface_count', 
    'EvCount', 
    'message_count', 
    'message_size'
    ]

    for f, f_dict in dct.items():
        for i, b_dict in enumerate(f_dict['benchmarks']):
            c_list1 = []
            for c in columns1:
                ### If any of the benchmark dictionaries don't have a column in our columns list,
                ### then set the value to np.nan.
                v = b_dict.get(c, np.nan)
                ### Append to the list of np.nans.
                c_list1.append(v)
            ### Append to lists with our list of np.nans, and columns with values
            ### that belong to our columns list; in other words, if there IS a value
            ### in 'federate_count', append that to lists, along with c_list.
            lists1.append(np.concatenate([[f, i], c_list1]))
    bmk_df = pd.DataFrame(lists1, columns=np.concatenate([['identifier_id', 'benchmark_id'], columns1]))
#    print(bmk_df.columns)
    
#    with open('bm_results.json', 'r') as f:
#        dct2 = json.load(f)
    # pprint(f_dict)
    
    ### Getting the cache data and creating a data frame.
    lists2 = []
    columns2 = [
        'type', 
        'level', 
        'size', 
        'num_sharing'
    ]
    
    for f, f_dict in dct.items():
        for i, b_dict in enumerate(f_dict['caches']):
            ### If any of the caches dictionaries don't have a column in our columns list,
            ### then set the value to np.nan
            c_list2 = []
            for c in columns2:
                ### Append to the list of np.nans.
                v = b_dict.get(c, np.nan)
                c_list2.append(v)
            ### Append to lists with our list of np.nans, and columns with values
            ### that belong to our columns list; in other words, if there IS a value
            ### in 'type', append that to lists, along with c_list.
            lists2.append(np.concatenate([[f, i], c_list2]))
    cache_df = pd.DataFrame(lists2, columns=np.concatenate([['identifier_id', 'cache_id'], columns2]))
    #print(cache_df.head())
    
#    with open('bm_results.json', 'r') as f:
#        dct3 = json.load(f)
    # pprint(f_dict)
    
    ### Getting the general benchmark info and creating a data frame.
    lists3 = []
    columns3 = [
    'filename', 
    'path', 
    'benchmark',
    'benchmark_type',
    'helics_version_string', 
    'helics_version', 
    'zmq_version_string', 
    'zmq_version', 
    'compiler_info_string', 
    'generator', 
    'system', 
    'system_version', 
    'platform', 
    'cxx_compiler', 
    'cxx_compiler_version',
    'build_flags_string', 
    'host_processor', 
    'host_processor_string', 
    'date', 
    'host_name', 
    'executable', 
    'num_cpus', 
    'mhz_per_cpu', 
    'cpu_scaling_enabled', 
    'load_avg', 
    'library_build_type',
    'run_id'
    ]
    
    for f, f_dict in dct.items():
        c_list3 = []
        for c in columns3:
            ### If any of the identifier dictionaries don't have a column in our columns list,
            ### then set the value to np.nan.
            v = f_dict.get(c, np.nan)
            ### Append to the list of np.nans.
            c_list3.append(v)
        ### Append to lists with our list of np.nans, and columns with values
        ### that belong to our columns list; in other words, if there IS a value
        ### in 'date', append that to lists, along with c_list.
        lists3.append(np.concatenate([[f, i], c_list3]))
    info_df = pd.DataFrame(lists3, columns=np.concatenate([['identifier_id', 'info_id'], columns3]))
    #print(info_df.columns)
    #print(info_df.head())
    
    ### Concatenating all three data frames into one meta data frame
    ### and sending to csv.
    meta_bmk_df = reduce(lambda x, y: pd.merge(x, y, on='identifier_id', how='outer'), [info_df, cache_df, bmk_df])
    real_time = []
    cpu_time = []
    ### CGR (2020-02-06): Converting 'real_time' from nanoseconds or 
    ### milliseconds to seconds.
    for t in meta_bmk_df.real_time:
        t_idx = meta_bmk_df[meta_bmk_df.real_time == t].index[0]
        if meta_bmk_df.at[t_idx, 'time_unit'] == 'ns':
            time = float(t) * (float(10) ** (float(-9)))
            real_time.append(t)
        elif meta_bmk_df.at[t_idx, 'time_unit'] == 'ms':
            time = float(t) * (float(10) ** (float(-3)))
            real_time.append(time)
    for c in meta_bmk_df.cpu_time:
        c_idx = meta_bmk_df[meta_bmk_df.cpu_time == c].index[0]
        if meta_bmk_df.at[c_idx, 'time_unit'] == 'ns':
            c_time = float(c) * (float(10) ** (float(-9)))
            cpu_time.append(c_time)
        elif meta_bmk_df.at[c_idx, 'time_unit'] == 'ms':
            c_time = float(c) * (float(10) ** (float(-3)))
            cpu_time.append(c_time)        
    meta_bmk_df['real_time'] = real_time
    meta_bmk_df['cpu_time'] = cpu_time
    csv_path = os.path.join(os.getcwd(), 'bmk_meta_df.csv')
    meta_bmk_df.to_csv(r'{}'.format(csv_path))
    
    ### Reading in the csv; seems unnecessary, but works due to
    ### plotting difficulties.
    final_meta_bmk_df = pd.read_csv(csv_path, index_col='Unnamed: 0', dtype={'platform': object, 'filter_location': object})
    os.remove(csv_path)
    
    return final_meta_bmk_df


def make_dataframe2(json_results):
    """This function creates a meta data frame to be used for 
    post-processing the Benchmark Results.
    
    Args:
        json_file (file): json file to be used for creating a dataframe
        
    Returns:
        meta_df: a data frame of all benckmark information
    """
    #print(cache_df.head())
    
#    with open('bm_results.json', 'r') as f:
#        dct3 = json.load(f)
    # pprint(f_dict)
    if isinstance(json_results, dict):
        dct = json_results
    else: 
        with open(json_results, 'r') as f:
            dct = json.load(f)
    
    ### Getting the general benchmark info and creating a data frame.
    lists = []
    columns = [
    'filename', 
    'path',
    'date',
    'cluster',
    'topology',
    'number_of_leaves',
    'number_of_nodes',
    'federate_count',
    'message_size', 
    'message_count',
    'benchmark',
    'benchmark_type',
    'helics_version_string', 
    'helics_version', 
    'zmq_version_string', 
    'zmq_version', 
    'compiler_info_string', 
    'generator', 
    'system', 
    'system_version', 
    'platform',
    'core_type',
    'cxx_compiler', 
    'cxx_compiler_version',
    'build_flags_string', 
    'host_processor', 
    'host_processor_string',
    'run_id',
    'elapsed_time',
    'time_unit',
    'EvCount'
    ]
    
    for f, f_dict in dct.items():
        for d, d_dict in f_dict.items():
            c_list = []
            for c in columns:
                ### If any of the identifier dictionaries don't have a column in our columns list,
                ### then set the value to np.nan.
                v = d_dict.get(c, np.nan)
                ### Append to the list of np.nans.
                c_list.append(v)
            ### Append to lists with our list of np.nans, and columns with values
            ### that belong to our columns list; in other words, if there IS a value
            ### in 'date', append that to lists, along with c_list.
            lists.append(np.concatenate([[f], c_list]))
    info_df = pd.DataFrame(lists, columns=np.concatenate([['identifier_id'], columns]))
    #print(info_df.columns)
    #print(info_df.head())
    
    ### Concatenating all three data frames into one meta data frame
    ### and sending to csv.
    meta_bmk_df = reduce(lambda x, y: pd.merge(x, y, on='identifier_id', how='outer'), [info_df])
    ### CGR (2020-02-06): Converting 'elapsed_time' from nanoseconds  
    ### to seconds.
    elapsed_time = [(float(e) * float(10) ** float(-9)) for e in meta_bmk_df.elapsed_time]
    meta_bmk_df['elapsed_time'] = elapsed_time
    meta_bmk_df['time_unit'] = 's'
    csv_path = os.path.join(os.getcwd(), 'multinode_bmk_meta_df.csv')
    meta_bmk_df.to_csv(r'{}'.format(csv_path))
    
    ### Reading in the csv; seems unnecessary, but works due to
    ### plotting difficulties.
    final_meta_bmk_df = pd.read_csv(csv_path, index_col='Unnamed: 0', dtype={'platform': object})
    os.remove(csv_path)
    
    return final_meta_bmk_df


### Testing that my function works
if __name__ == '__main__':
#    json_file1 = 'bm_results.json'
#    final_meta_bmk_df = make_dataframe1(json_file1)
#    
#    json_file2 = 'multinode_bm_results.json'
#    multi_bmk_df = make_dataframe2(json_file2)
    
    json_file3 = 'multinode_bm_results_test.json'
    multi_bmk_df = make_dataframe2(json_file3)
#    print(final_meta_bmk_df.columns)
#    print(final_meta_bmk_df.head())
#    print(final_meta_bmk_df.shape)
