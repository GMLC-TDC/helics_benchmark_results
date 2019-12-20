# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 19:03:59 2019

@author: barn553
"""

from pprint import pprint
from functools import reduce
import make_dataframe as md
import benchmark_postprocessing as bmpp
import numpy as np
import holoviews as hv
import json
import numpy as np
import glob
import os
import datetime
import pandas as pd
import hvplot.pandas
from holoviews.operation.datashader import datashade, dynspread
hv.extension('bokeh', 'matplotlib', width=100)


#file_list = bmpp.get_benchmark_files('C:\Users\barn553\Documents\GitHub\helics_benchmark_results\benchmark_results\2019-11-28')
#json_results = bmpp.parse_files(file_list)
#json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
json_file = 'bm_results.json'
meta_bmk_df = md.make_dataframe(json_file)
#print(meta_bmk_df.shape)
meta_bmk_df.sort_values('federate_count').hvplot.line('federate_count', 'real_time')


def plot_echo_msg(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    echoMessageBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type'.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        echo_msg (obj): IPython holoviews plot of the data.
    """
    
    echo_df = dataframe[ dataframe.benchmark == 'echoMessageBenchmark']
    echo_df = echo_df[ echo_df.run_id == '{}'.format(run_id)]
    echo_msg = echo_df.sort_values('federate_count').hvplot.line(
            'federate_count', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} echoMessageBenchmark: federate_count vs real_time'.format(run_id), 
            by='core_type', 
            alpha=0.5).opts(
                    width=1000, 
                    height=600, 
                    logx=True, 
                    logy=True)
    return echo_msg

def plot_echo_result(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    echoBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type'.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        echo_res (obj): IPython holoviews plot of the data.
    """
    echo_df = dataframe[ dataframe.benchmark == 'echoBenchmark']
    echo_df = echo_df[ echo_df.run_id == '{}'.format(run_id)]
    echo_res = echo_df.sort_values('federate_count').hvplot.line(
            'federate_count', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} echoBenchmark: federate_count vs real_time'.format(run_id),
            by='core_type', 
            alpha=0.5).opts(
                    width=1000, 
                    height=600, 
                    logx=True, 
                    logy=True)
    return echo_res

def plot_msg_lookup(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    messageLookupBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'inproc'.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        msg_lookup (obj): IPython holoviews plot of the data.
    """
    msg_lkp_df = dataframe[ dataframe.benchmark == 'messageLookupBenchmark']
    inproc_df = msg_lkp_df[ msg_lkp_df.core_type == 'inproc']
    inproc_df = inproc_df[ inproc_df.run_id == '{}'.format(run_id)]
    msg_lookup = inproc_df.sort_values('federate_count').hvplot.bar(
            'federate_count', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} messageLookupBenchmark: federate_count vs real_time'.format(run_id),
            alpha=0.5).opts(
                    width=1000, 
                    height=600, 
                    logx=True, 
                    logy=True)
    return msg_lookup

def plot_msg_send_1(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    messageSendBenchmark, of 'message_size' versus 'real_time' and
    it is organized by a single 'core_type': 'singleFed'.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        msg_send (obj): IPython holoviews plot of the data.
    """
    msg_snd_df = dataframe[ dataframe.benchmark == 'messageSendBenchmark']
    msg_snd_df = msg_snd_df[ msg_snd_df.core_type == 'singleFed']
    msg_snd_df = msg_snd_df[ msg_snd_df.run_id == '{}'.format(run_id)]
    msg_send = msg_snd_df.sort_values('message_size').hvplot.line(
            'message_size', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} messageSendBenchmark, core_type {}: message_size vs real_time'.format(run_id, 'singleFed'),
            alpha=0.5).opts(
                    width=1000, 
                    height=600, 
                    logx=True, 
                    logy=True)
    return msg_send

def plot_msg_send_2(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    messageSendBenchmark, of 'message_size' versus 'real_time' and
    it is organized by 'core_type' and 'message_count'= 1.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        msg_count (obj): IPython holoviews plot of the data.
    """
    msg_snd_df = dataframe[ dataframe.benchmark == 'messageSendBenchmark']
    msg_ct_df = msg_snd_df[ msg_snd_df.run_id == '{}'.format(run_id)]
    msg_ct_df = msg_ct_df[ msg_ct_df.message_count == 1]
    msg_count = msg_ct_df.sort_values('message_size').hvplot.line(
            'message_size', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} messageSendBenchmark, message_count = 1: message_size vs real_time'.format(run_id),
            by='core_type', 
            alpha=0.5).opts(
                    width=1000, 
                    height=600, 
                    logx=True, 
                    logy=True)
    return msg_count

def plot_msg_send_3(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    messageSendBenchmark, of 'message_count' versus 'real_time' and
    it is organized by 'core_type' and 'message_size'= 1.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        msg_size (obj): IPython holoviews plot of the data.
    """
    msg_snd_df = dataframe[ dataframe.benchmark == 'messageSendBenchmark']
    msg_sz_df = msg_snd_df[ msg_snd_df.message_size == 1]
    msg_sz_df = msg_sz_df[ msg_sz_df.run_id == '{}'.format(run_id)]
    msg_size = msg_sz_df.sort_values('message_count').hvplot.line(
            'message_count', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} messageSendBenchmark, message_size = 1: message_count vs real_time'.format(run_id),
            by='core_type', 
            alpha=0.5).opts(
                    width=1000, 
                    height=600, 
                    logx=True, 
                    logy=True)
    return msg_size

def plot_phold(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    pholdBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type'.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        phold (obj): IPython holoviews plot of the data.
    """
    phold_df = dataframe[ dataframe.benchmark == 'pholdBenchmark']
    phold_df = phold_df[ phold_df.run_id == '{}'.format(run_id)]
    phold = phold_df.sort_values('federate_count').hvplot.line(
            'federate_count', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} pholdBenchmark: federate_count vs real_time'.format(run_id),
            by='core_type', 
            alpha=0.5).opts(
                    width=1000, 
                    height=600, 
                    logx=True, 
                    logy=True)
    return phold

def plot_ring(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    ringBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type'.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        ring (obj): IPython holoviews plot of the data.
    """
    ring_df = dataframe[ dataframe.benchmark == 'ringBenchmark']
    ring_df = ring_df[ ring_df.run_id == '{}'.format(run_id)]
    ring = ring_df.sort_values('federate_count').hvplot.line(
            'federate_count', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} ringBenchmark: federate_count vs real_time'.format(run_id),
            by='core_type', 
            alpha=0.5).opts(
                    width=1000, 
                    height=600, 
                    logx=True, 
                    logy=True)
    return ring

def plot_filter(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type': 'singleCore'.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        filtr (obj): IPython holoviews plot of the data.
    """
    filter_df = dataframe[ dataframe.benchmark == 'filterBenchmark']
    filter_df = filter_df[ filter_df.core_type == 'singleCore']
    filter_df = filter_df[ filter_df.run_id == '{}'.format(run_id)]
    filtr = filter_df.sort_values('federate_count').hvplot.line(
            'federate_count', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} filterBenchmark, core_type {}: federate_count vs real_time'.format(run_id, 'singleCore'), 
            by='filter_location',
            alpha=0.5).opts(
                    width=1000, 
                    height=600)
    return filtr

def plot_src(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type' and 'filter_location' = 'source'.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        source (obj): IPython holoviews plot of the data.
    """
    filter_df = dataframe[ dataframe.benchmark == 'filterBenchmark']
    filter_df = filter_df[ filter_df.filter_location == 'source']
    filter_df = filter_df[ filter_df.run_id == '{}'.format(run_id)]
    source = filter_df.sort_values('federate_count').hvplot.line(
            'federate_count', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} filterBenchmark, filter_location {}: federate_count vs real_time'.format(run_id, 'source'),
            by='core_type', 
            alpha=0.5).opts(
                    width=1000, 
                    height=600, 
                    logx=True, 
                    logy=True)
    return source

def plot_dest(dataframe, run_id):
    """This function creates a multi-line graph for the benchmark, 
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type' and 'filter_location' = 'destination'.
    
    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        dest (obj): IPython holoviews plot of the data.
    """
    filter_df = dataframe[ dataframe.benchmark == 'filterBenchmark']
    filter_df = filter_df[ filter_df.filter_location == 'destination']
    filter_df = filter_df[ filter_df.run_id == '{}'.format(run_id)]
    dest = filter_df.sort_values('federate_count').hvplot.line(
            'federate_count', 
            'real_time', 
            ylabel='real_time (ns)', 
            title='run_id {} filterBenchmark, filter_location {}: federate_count vs real_time'.format(run_id, 'destination'),
            by='core_type', 
            alpha=0.5).opts(
                    width=1000, 
                    height=600, 
                    logx=True, 
                    logy=True)
    return dest

def save_plots(plot_list, run_id):
    """This function saves the desired plots as .png files.
    
    Args:
        plot_list (list): List of plots desired to save.
        run_id (str): Specific run_id used to create this plot.
    """

    i = 1
    plot_list = plot_list
    for p in plot_list:
        hvplot.save(p, 'run_id {} plot_{}.png'.format(run_id, i))
        i += 1


### Testing
def main():
    """The main function that tests the above functions."""
    echo_message = plot_echo_msg(meta_bmk_df, 'r1Nr5')
    echo_result = plot_echo_result(meta_bmk_df, 'r1Nr5')
    message_lookup = plot_msg_lookup(meta_bmk_df, 'r1Nr5')
#    message_send_1 = plot_msg_send_1(meta_bmk_df, 'Md3vp')
    message_send_2 = plot_msg_send_2(meta_bmk_df, 'r1Nr5')
    message_send_3 = plot_msg_send_3(meta_bmk_df, 'r1Nr5')
    phold = plot_phold(meta_bmk_df, 'r1Nr5')
    ring = plot_ring(meta_bmk_df, 'r1Nr5')
    filtr = plot_filter(meta_bmk_df, 'r1Nr5')
    source = plot_src(meta_bmk_df, 'r1Nr5')
    destination = plot_dest(meta_bmk_df, 'r1Nr5')
    plot_list = [echo_message, 
                 echo_result, 
                 message_lookup,
                 message_send_2,
                 message_send_3,
                 phold,
                 ring,
                 filtr,
                 source,
                 destination]
    
    save_plots(plot_list, 'r1Nr5')
    
main()