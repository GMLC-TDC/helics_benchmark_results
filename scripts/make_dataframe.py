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

def make_dataframe(json_results):
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
    
    indices1 = {c_i: i for i, c_i in enumerate(columns1)}
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
    
    indices = {c_i: i for i, c_i in enumerate(columns2)}
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
    indices3 = {c_i: i for i, c_i in enumerate(columns3)}
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
    csv_path = os.path.join(os.getcwd(), 'bmk_meta_df.csv')
    meta_bmk_df.to_csv(r'{}'.format(csv_path))
    
    ### Reading in the csv; seems unnecessary, but works due to
    ### plotting difficulties.
    final_meta_bmk_df = pd.read_csv(csv_path, index_col='Unnamed: 0')
    os.remove(csv_path)
    
    return final_meta_bmk_df


### Testing that my function works
#def main():
#    """THe main script that runs this package; mainly for testing 
#    to make sure I created the above function like I wanted to.
#    """
#    json_file = 'bm_results.json'
#    final_meta_bmk_df = make_dataframe(json_file)
##    print(final_meta_bmk_df.columns)
##    print(final_meta_bmk_df.head())
#    print(final_meta_bmk_df.shape)
#    
#main()
