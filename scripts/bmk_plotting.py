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


# file_list = bmpp.get_benchmark_files('C:\Users\barn553\Documents\GitHub\helics_benchmark_results\benchmark_results\2019-11-28')
# json_results = bmpp.parse_files(file_list)
# json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
# json_file = 'bm_results.json'
# meta_bmk_df = md.make_dataframe(json_file)
# print(meta_bmk_df.shape)
# meta_bmk_df.sort_values('federate_count').hvplot.line('federate_count', 'real_time')


def plot_echo_msg(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    echoMessageBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        echo_msg (obj): IPython holoviews plot of the data.
    """
    echo_df = dataframe[(dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
    echo_msg = echo_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        #(range(0, (int(float(echo_df.federate_count.max()))+1), 4)),
        title='run_id {} echoMessageBenchmark: federate_count vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        legend_position='bottom_right',
        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_echoMessage.png'.format(run_id))
    hvplot.save(echo_msg, save_path)
    return echo_msg


def plot_echo_result(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    echoBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        echo_res (obj): IPython holoviews plot of the data.
    """
    echo_df = dataframe[(dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
    echo_res = echo_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        #(range(0, (int(float(echo_df.federate_count.max()))+1), 1)),
        title='run_id {} echoBenchmark: federate_count vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        legend_position='bottom_right',
        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_echoResult.png'.format(run_id))
    hvplot.save(echo_res, save_path)
    return echo_res


def plot_echo_c(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    cEchoBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        echo_c_res (obj): IPython holoviews plot of the data.
    """
    echo_c = dataframe[(dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
    echo_c_res = echo_c.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        #(range(0, (int(float(echo_df.federate_count.max()))+1), 1)),
        title='run_id {} cEchoBenchmark: federate_count vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        legend_position='bottom_right',
        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_echo_cResult.png'.format(run_id))
    hvplot.save(echo_c_res, save_path)
    return echo_c_res


def plot_msg_lookup_1(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    messageLookupBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'inproc'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        msg_lookup (obj): IPython holoviews plot of the data.
    """
    inproc_df = dataframe[(dataframe.core_type == 'inproc') & (dataframe.benchmark_type == 'full')]
    inproc_df = inproc_df[inproc_df.run_id == '{}'.format(run_id)]
    inproc_df = inproc_df[inproc_df.federate_count == 2]
    msg_lookup = inproc_df.sort_values('interface_count').hvplot.line(
        'interface_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} messageLookupBenchmark: interface_count vs real_time'.format(run_id),
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_messageLookup.png'.format(run_id))
    hvplot.save(msg_lookup, save_path)
    return msg_lookup

def plot_msg_lookup_2(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    messageLookupBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'inproc'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        msg_lookup (obj): IPython holoviews plot of the data.
    """
    inproc_df = dataframe[(dataframe.core_type == 'inproc') & (dataframe.benchmark_type == 'full')]
    inproc_df = inproc_df[inproc_df.run_id == '{}'.format(run_id)]
    inproc_df = inproc_df[inproc_df.federate_count == 8]
    msg_lookup = inproc_df.sort_values('interface_count').hvplot.line(
        'interface_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} messageLookupBenchmark: interface_count vs real_time'.format(run_id),
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_messageLookup.png'.format(run_id))
    hvplot.save(msg_lookup, save_path)
    return msg_lookup

def plot_msg_lookup_3(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    messageLookupBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'inproc'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        msg_lookup (obj): IPython holoviews plot of the data.
    """
    inproc_df = dataframe[(dataframe.core_type == 'inproc') & (dataframe.benchmark_type == 'full')]
    inproc_df = inproc_df[inproc_df.run_id == '{}'.format(run_id)]
    inproc_df = inproc_df[inproc_df.federate_count == 64]
    msg_lookup = inproc_df.sort_values('interface_count').hvplot.line(
        'interface_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} messageLookupBenchmark: interface_count vs real_time'.format(run_id),
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_messageLookup.png'.format(run_id))
    hvplot.save(msg_lookup, save_path)
    return msg_lookup


def plot_msg_send_1(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    messageSendBenchmark, of 'message_size' versus 'real_time' and
    it is organized by a single 'core_type': 'singleCore'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        msg_send (obj): IPython holoviews plot of the data.
    """
    msg_snd_df = dataframe[(dataframe.core_type == 'singleCore') & (dataframe.benchmark_type == 'full')]
    msg_snd_df = msg_snd_df[msg_snd_df.run_id == '{}'.format(run_id)]
    msg_send = msg_snd_df.sort_values('message_size').hvplot.line(
        'message_size',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} messageSendBenchmark, core_type {}: message_size vs real_time'.format(run_id, 'singleCore'),
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        legend_position='bottom_right',
        fontsize={'title': 9, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_messageSend1.png'.format(run_id))
    hvplot.save(msg_send, save_path)
    return msg_send


def plot_msg_send_2(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    messageSendBenchmark, of 'message_size' versus 'real_time' and
    it is organized by 'core_type' and 'message_count'= 1.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        msg_count (obj): IPython holoviews plot of the data.
    """
    msg_ct_df = dataframe[(dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
    msg_ct_df = msg_ct_df[msg_ct_df.message_count == 1]
    msg_count = msg_ct_df.sort_values('message_size').hvplot.line(
        'message_size',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} messageSendBenchmark, message_count = 1: message_size vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        legend_position='bottom_right',
        fontsize={'title': 9, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_messageSend2.png'.format(run_id))
    hvplot.save(msg_count, save_path)
    return msg_count


def plot_msg_send_3(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    messageSendBenchmark, of 'message_count' versus 'real_time' and
    it is organized by 'core_type' and 'message_size'= 1.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        msg_size (obj): IPython holoviews plot of the data.
    """
    msg_sz_df = dataframe[dataframe.message_size == 1]
    msg_sz_df = msg_sz_df[(msg_sz_df.run_id == '{}'.format(run_id)) & (msg_sz_df.benchmark_type == 'full')]
    msg_size = msg_sz_df.sort_values('message_count').hvplot.line(
        'message_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} messageSendBenchmark, message_size = 1: message_count vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        legend_position='bottom_right',
        fontsize={'title': 9, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_messageSend3.png'.format(run_id))
    hvplot.save(msg_size, save_path)
    return msg_size


def plot_phold(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    pholdBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        phold (obj): IPython holoviews plot of the data.
    """
    phold_df = dataframe[(dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
    phold = phold_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        #(range(0, (int(float(phold_df.federate_count.max()))+1), 5)),
        title='run_id {} pholdBenchmark: federate_count vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        legend_position='bottom_right',
        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_pHold.png'.format(run_id))
    hvplot.save(phold, save_path)
    return phold


def plot_ring(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    ringBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        ring (obj): IPython holoviews plot of the data.
    """
    ring_df = dataframe[(dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
    ring = ring_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        #(range(0, (int(float(ring_df.federate_count.max()))+2), 1)),
        title='run_id {} ringBenchmark: federate_count vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        legend_position='bottom_right',
        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_ring.png'.format(run_id))
    hvplot.save(ring, save_path)
    return ring


def plot_filter(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type': 'singleCore'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        filtr (obj): IPython holoviews plot of the data.
    """
    filter_df = dataframe[(dataframe.core_type == 'singleCore') & (dataframe.benchmark_type == 'full')]
    filter_df = filter_df[filter_df.run_id == '{}'.format(run_id)]
    filtr = filter_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        #(range(0, (int(float(filter_df.federate_count.max()))+1), 2)),
        title='run_id {} filterBenchmark, core_type {}: federate_count vs real_time'.format(run_id, 'singleCore'),
        by='filter_location',
        alpha=0.5).opts(
        width=600,
        height=360,
        legend_position='bottom_right',
        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_filter.png'.format(run_id))
    hvplot.save(filtr, save_path)
    return filtr


def plot_src(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type' and 'filter_location' = 'source'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        source (obj): IPython holoviews plot of the data.
    """
    filter_df = dataframe[(dataframe.filter_location == 'source') & (dataframe.benchmark_type == 'full')]
    filter_df = filter_df[filter_df.run_id == '{}'.format(run_id)]
    source = filter_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        #(range(0, (int(float(filter_df.federate_count.max()))+4), 4)),
        title='run_id {} filterBenchmark, filter_location {}: federate_count vs real_time'.format(run_id, 'source'),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        legend_position='bottom_right',
        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_source.png'.format(run_id))
    hvplot.save(source, save_path)
    return source


def plot_dest(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type' and 'filter_location' = 'destination'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        dest (obj): IPython holoviews plot of the data.
    """
    filter_df = dataframe[(dataframe.filter_location == 'destination') & (dataframe.benchmark_type == 'full')]
    filter_df = filter_df[filter_df.run_id == '{}'.format(run_id)]
    dest = filter_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        #(range(0, (int(float(filter_df.federate_count.max()))+1), 4)),
        title='run_id {} filterBenchmark, filter_location {}: federate_count vs real_time'.format(run_id,
                                                                                                  'destination'),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        legen_position='bottom_right',
        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_destination.png'.format(run_id))
    hvplot.save(dest, save_path)
    return dest


def plot_timing(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    timingBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by 'core_type'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        timing (obj): IPython holoviews plot of the data.
    """
    time_df = dataframe[(dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
    timing = time_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        #(range(0, (int(float(echo_df.federate_count.max()))+1), 4)),
        title='run_id {} timingBenchmark: federate_count vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        legend_position='bottom_right',
        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    save_path = os.path.join(output_path, '{}_timing.png'.format(run_id))
    hvplot.save(timing, save_path)
    return timing

#-----------------------------------------------------------------------#
#------------------  Cross-run_id comparison plots ---------------------#
def plot_echo_msg_cr(dataframe, run_id_list, core_type, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    echoMessageBenchmark, of 'federate_count' versus 'real_time', and
    it is organized by a single 'core_type' and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        echo_msg_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    echo_msgs = []
    for run_id in run_id_list:
        echo_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & (
                        dataframe.run_id == '{}'.format(run_id)) & (
                                dataframe.benchmark_type == 'full')]
        echo_msg = echo_df.sort_values('federate_count').hvplot.line(
                'federate_count', 
                'real_time', 
                ylabel='real_time (ns)',
                #(range(0, (int(float(echo_df.federate_count.max()))+1), 4)),
                title='echoMessageBenchmark: federate_count vs real_time', 
                label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, echo_df['{}'.format(comparison_parameter)].unique()),
                alpha=0.5)
        echo_msgs.append(echo_msg)
    echo_msg_plot = (reduce((lambda x, y: x*y), echo_msgs)).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_echoMessage_{}Core.png'.format(run_id_str, core_type))
    hvplot.save(echo_msg_plot, save_path)
    return echo_msg_plot


def plot_echo_result_cr(dataframe, run_id_list, core_type, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    echoBenchmark, of 'federate_count' versus 'real_time' and
    it is organized a single 'core_type' and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        echo_res_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    echo_ress = []
    for run_id in run_id_list:
        echo_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & (
                    dataframe.run_id == '{}'.format(run_id)) & (
                            dataframe.benchmark_type == 'full')]
        echo_res = echo_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            #(range(0, (int(float(echo_df.federate_count.max()))+1), 1)),
            title='echoBenchmark: federate_count vs real_time',
            label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, echo_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        echo_ress.append(echo_res)
    echo_res_plot = (reduce((lambda x, y: x*y), echo_ress)).opts(
                        width=600, 
                        height=360,
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_echo_{}Core.png'.format(run_id_str, core_type))
    hvplot.save(echo_res_plot, save_path)
    return echo_res_plot


def plot_echo_c_cr(dataframe, run_id_list, core_type, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    cEchoBenchmark, of 'federate_count' versus 'real_time' and
    it is organized a single 'core_type' and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        echo_c_res_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    echo_cs = []
    for run_id in run_id_list:
        echo_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & (
                    dataframe.run_id == '{}'.format(run_id)) & (
                            dataframe.benchmark_type == 'full')]
        echo_c_res = echo_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            #(range(0, (int(float(echo_df.federate_count.max()))+1), 1)),
            title='cEchoBenchmark: federate_count vs real_time',
            label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, echo_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        echo_cs.append(echo_c_res)
    echo_c_res_plot = (reduce((lambda x, y: x*y), echo_cs)).opts(
                        width=600, 
                        height=360,
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_echo_c_{}Core.png'.format(run_id_str, core_type))
    hvplot.save(echo_c_res_plot, save_path)
    return echo_c_res_plot


def plot_msg_lookup_1_cr(dataframe, run_id_list, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    messageLookupBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'inproc' and compares
    run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        msg_lookup_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    msg_lookups = []
    for run_id in run_id_list:
        msg_lkp_df = dataframe[(dataframe.core_type == 'inproc') & (
                    dataframe.run_id == '{}'.format(run_id)) & (dataframe.federate_count == 2) & (
                            dataframe.benchmark_type == 'full')]
        msg_lookup = msg_lkp_df.sort_values('interface_count').hvplot.line(
            'interface_count',
            'real_time',
            ylabel='real_time (ns)',
            title='fed_ct = 2, messageLookup: interface_count vs real_time',
            label='run_id: {}, core_type: inproc, {}: {}'.format(run_id, comparison_parameter, msg_lkp_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_lookups.append(msg_lookup)
    msg_lookup_plot = reduce((lambda x, y: x*y), msg_lookups).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_messageLookup.png'.format(run_id_str))
    hvplot.save(msg_lookup_plot, save_path)
    return msg_lookup_plot


def plot_msg_lookup_2_cr(dataframe, run_id_list, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    messageLookupBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'inproc' and compares
    run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        msg_lookup_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    msg_lookups = []
    for run_id in run_id_list:
        msg_lkp_df = dataframe[(dataframe.core_type == 'inproc') & (
                    dataframe.run_id == '{}'.format(run_id)) & (dataframe.federate_count == 8) & (
                            dataframe.benchmark_type == 'full')]
        msg_lookup = msg_lkp_df.sort_values('interface_count').hvplot.line(
            'interface_count',
            'real_time',
            ylabel='real_time (ns)',
            title='fed_ct = 8, messageLookup: interface_count vs real_time',
            label='run_id: {}, core_type: inproc, {}: {}'.format(run_id, comparison_parameter, msg_lkp_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_lookups.append(msg_lookup)
    msg_lookup_plot = reduce((lambda x, y: x*y), msg_lookups).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_messageLookup.png'.format(run_id_str))
    hvplot.save(msg_lookup_plot, save_path)
    return msg_lookup_plot


def plot_msg_lookup_3_cr(dataframe, run_id_list, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    messageLookupBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'inproc' and compares
    run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        msg_lookup_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    msg_lookups = []
    for run_id in run_id_list:
        msg_lkp_df = dataframe[(dataframe.core_type == 'inproc') & (
                    dataframe.run_id == '{}'.format(run_id)) & (dataframe.federate_count == 64) & (
                            dataframe.benchmark_type == 'full')]
        msg_lookup = msg_lkp_df.sort_values('interface_count').hvplot.line(
            'interface_count',
            'real_time',
            ylabel='real_time (ns)',
            title='fed_ct = 64, messageLookup: interface_count vs real_time',
            label='run_id: {}, core_type: inproc, {}: {}'.format(run_id, comparison_parameter, msg_lkp_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_lookups.append(msg_lookup)
    msg_lookup_plot = reduce((lambda x, y: x*y), msg_lookups).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='bottom_right',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}__messageLookup.png'.format(run_id_str))
    hvplot.save(msg_lookup_plot, save_path)
    return msg_lookup_plot


def plot_msg_send_1_cr(dataframe, run_id_list, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    messageSendBenchmark, of 'message_size' versus 'real_time' and
    it is organized by a single 'core_type': 'singleCore' and compares
    run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        msg_send_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    msg_sends = []
    for run_id in run_id_list:
        msg_snd_df = dataframe[(dataframe.core_type == 'singleCore') & (
                        dataframe.run_id == '{}'.format(run_id)) & (
                                dataframe.benchmark_type == 'full')]
        msg_send = msg_snd_df.sort_values('message_size').hvplot.line(
            'message_size',
            'real_time',
            ylabel='real_time (ns)',
            title='messageSendBenchmark: message_size vs real_time',
            label='run_id: {}, core_type: singleCore, {}: {}'.format(run_id, comparison_parameter, msg_snd_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_sends.append(msg_send)
    msg_send_plot = (reduce((lambda x, y: x*y), msg_sends)).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_messageSend1.png'.format(run_id_str))
    hvplot.save(msg_send_plot, save_path)
    return msg_send_plot


def plot_msg_send_2_cr(dataframe, run_id_list, core_type, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    messageSendBenchmark, of 'message_size' versus 'real_time' and
    it is organized by a single 'core_type', 'message_count'= 1, and
    compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        msg_count_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    msg_cts = []
    for run_id in run_id_list:
        msg_ct_df = dataframe[(dataframe.core_type == 'singleCore') & (
                dataframe.run_id == '{}'.format(run_id)) & (dataframe.message_count == 1) & (
                        dataframe.benchmark_type == 'full')]
        msg_count = msg_ct_df.sort_values('message_size').hvplot.line(
            'message_size',
            'real_time',
            ylabel='real_time (ns)',
            title='msg_ct = 1, messageSendBenchmark: message_size vs real_time', 
            label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, msg_ct_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_cts.append(msg_count)
    msg_count_plot = (reduce((lambda x, y: x*y), msg_cts)).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_messageSend2_{}Core.png'.format(run_id_str, core_type))
    hvplot.save(msg_count_plot, save_path)
    return msg_count_plot


def plot_msg_send_3_cr(dataframe, run_id_list, core_type, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    messageSendBenchmark, of 'message_count' versus 'real_time' and
    it is organized by a single 'core_type', 'message_size'= 1, and
    compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        msg_size_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    msg_sizes = []
    for run_id in run_id_list:
        msg_sz_df = dataframe[(dataframe.core_type == 'singleCore') & (
                dataframe.run_id == '{}'.format(run_id)) & (dataframe.message_size == 1) & (
                        dataframe.benchmark_type == 'full')]
        msg_size = msg_sz_df.sort_values('message_count').hvplot.line(
            'message_count',
            'real_time',
            ylabel='real_time (ns)',
            title='msg_sz = 1, messageSendBenchmark: message_count vs real_time',
            label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, msg_sz_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_sizes.append(msg_size)
    msg_size_plot = (reduce((lambda x, y: x*y), msg_sizes)).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_messageSend3_{}Core.png'.format(run_id_str, core_type))
    hvplot.save(msg_size_plot, save_path)
    return msg_size_plot


def plot_phold_cr(dataframe, run_id_list, core_type, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    pholdBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type' and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Sepcific parameter to view.
        
    Returns:
        phold_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    pholds = []
    for run_id in run_id_list:
        phold_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & (
                    dataframe.run_id == '{}'.format(run_id)) & (
                            dataframe.benchmark_type == 'full')]
        phold = phold_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            #(range(0, (int(float(phold_df.federate_count.max()))+1), 5)),
            title='pholdBenchmark: federate_count vs real_time',
            label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, phold_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        pholds.append(phold)
    phold_plot = (reduce((lambda x, y: x*y), pholds)).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_phold_{}Core.png'.format(run_id_str, core_type))
    hvplot.save(phold_plot, save_path)
    return phold_plot


def plot_ring_cr(dataframe, run_id_list, core_type, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    ringBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type' and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        ring_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    rings = []
    if core_type == 'singleCore':
        for run_id in run_id_list:
            ring_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & (
                        dataframe.run_id == '{}'.format(run_id)) & (
                                dataframe.benchmark_type == 'full')]
            ring = ring_df.hvplot.bar(
                'run_id',
                'real_time',
                ylabel='real_time (ns)',
                #(range(0, (int(float(ring_df.federate_count.max()))+2), 1)),
                title='ringBenchmark: federate_count vs real_time',
                label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, ring_df['{}'.format(comparison_parameter)].unique()),
                alpha=0.5)
            rings.append(ring)
        ring_plot = (reduce((lambda x, y: x*y), rings)).opts(
                            width=600, 
                            height=360, 
                            legend_position='top_left',
                            fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    else:
        for run_id in run_id_list:
            ring_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & (
                        dataframe.run_id == '{}'.format(run_id))]
            ring = ring_df.sort_values('federate_count').hvplot.line(
                'federate_count',
                'real_time',
                ylabel='real_time (ns)',
                #(range(0, (int(float(ring_df.federate_count.max()))+2), 1)),
                title='ringBenchmark: federate_count vs real_time',
                label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, ring_df['{}'.format(comparison_parameter)].unique()),
                alpha=0.5)
            rings.append(ring)
        ring_plot = (reduce((lambda x, y: x*y), rings)).opts(
                            width=600, 
                            height=360,
                            logx=True,
                            logy=True,
                            legend_position='top_left',
                            fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_ring_{}Core.png'.format(run_id_str, core_type))
    hvplot.save(ring_plot, save_path)
    return ring_plot


def plot_filter_cr(dataframe, run_id_list, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'singleCore' and compares
    run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        filter_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    filters = []
    for run_id in run_id_list:
        filter_df = dataframe[(dataframe.core_type == 'singleCore') & (
                dataframe.run_id == '{}'.format(run_id)) & (
                        dataframe.benchmark_type == 'full')]
        filtr = filter_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            #(range(0, (int(float(filter_df.federate_count.max()))+1), 2)),
            title='filterBenchmark: federate_count vs real_time',
            label='run_id: {}, core_type: singleCore, {}: {}'.format(run_id, comparison_parameter, filter_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        filters.append(filtr)
    filter_plot = (reduce((lambda x, y: x*y), filters)).opts(
                        width=600, 
                        height=360,
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_filter.png'.format(run_id_str))
    hvplot.save(filter_plot, save_path)
    return filter_plot


def plot_src_cr(dataframe, run_id_list, core_type, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type', 'filter_location' = 'source',
    and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        source_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    sources = []
    for run_id in run_id_list:
        filter_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & (
                    dataframe.run_id == '{}'.format(run_id)) & (dataframe.filter_location == 'source') & (
                            dataframe.benchmark_type == 'full')]
        source = filter_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            #(range(0, (int(float(filter_df.federate_count.max()))+4), 4)),
            title='filter_location-source, filterBenchmark: federate_count vs real_time',
            label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, filter_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        sources.append(source)
    source_plot = (reduce((lambda x, y: x*y), sources)).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_srcFilter_{}Core.png'.format(run_id_str, core_type))
    hvplot.save(source_plot, save_path)
    return source_plot


def plot_dest_cr(dataframe, run_id_list, core_type, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type', 'filter_location' = 'destination',
    and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        dest_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    dests = []
    for run_id in run_id_list:
        filter_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & (
                    dataframe.run_id == '{}'.format(run_id)) & (dataframe.filter_location == 'destination') & (
                            dataframe.benchmark_type == 'full')]
        filter_df = filter_df[filter_df.run_id == '{}'.format(run_id)]
        dest = filter_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            #(range(0, (int(float(filter_df.federate_count.max()))+1), 4)),
            title='filter_location-destination, filterBenchmark: federate_count vs real_time',
            label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, filter_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        dests.append(dest)
    dest_plot = (reduce((lambda x, y: x*y), dests)).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_destFilter_{}Core.png'.format(run_id_str, core_type))
    hvplot.save(dest_plot, save_path)
    return dest_plot


def plot_timing_cr(dataframe, run_id_list, core_type, output_path, comparison_parameter):
    """This function creates a multi-line graph for the benchmark,
    timingBenchmark, of 'federate_count' versus 'real_time', and
    it is organized by a single 'core_type' and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
        output_path (path): Location to send the graph.
        comparison_parameter (str): Specific parameter to view.
        
    Returns:
        timing_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    times = []
    for run_id in run_id_list:
        time_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & (
                        dataframe.run_id == '{}'.format(run_id)) (
                                dataframe.benchmark_type == 'full')]
        time = time_df.sort_values('federate_count').hvplot.line(
                'federate_count', 
                'real_time', 
                ylabel='real_time (ns)',
                #(range(0, (int(float(echo_df.federate_count.max()))+1), 4)),
                title='timingBenchmark: federate_count vs real_time', 
                label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, time_df['{}'.format(comparison_parameter)].unique()),
                alpha=0.5)
        times.append(time)
    timing_plot = (reduce((lambda x, y: x*y), times)).opts(
                        width=600, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_timing_{}Core.png'.format(run_id_str, core_type))
    hvplot.save(timing_plot, save_path)
    return timing_plot


#-----------------------------------------------------------------------#
#------------------  Cross-benchmark comparison plots ------------------#
def plot_echo_vs_timing(dataframe1, dataframe2, run_id, core_type_list, output_path):
    """This function creates a multi-line graph for the benchmarks,
    echoBenchmark and timingBenchmark, of 'federate_count' versus 'real_time' 
    and it is organized by a single 'run_id' and (potential) list of
    core_types.

    Args:
        dataframe1 (obj): A data frame created by make_dataframe filtered by a specific benchmark.
        dataframe2 (obj): A data frame created by make_dataframe filtered by a specific benchmark.
        run_id (str): Specific run_id used to create this plot.
        core_type_list: Specific core_types used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        echo_v_timing (obj): IPython holoviews plot of the data.
    """
    core_type_list = core_type_list
    evts = []
    for core_type in core_type_list:
            df1 = dataframe1[(dataframe1.core_type == '{}'.format(core_type)) & (
                        dataframe1.run_id == '{}'.format(run_id))]
            evt1 = df1.sort_values('federate_count').hvplot.line(
                'federate_count',
                'real_time',
                ylabel='real_time (ns)',
                #(range(0, (int(float(echo_df.federate_count.max()))+1), 1)),
                title='timing vs echoBenchmark: federate_count vs real_time',
                label='{}, run_id: {}, core_type: {}'.format(df1.benchmark.unique(), run_id, core_type),
                alpha=0.5)
            df2 = dataframe2[(dataframe2.core_type == '{}'.format(core_type)) & (
                        dataframe2.run_id == '{}'.format(run_id))]
            evt2 = df2.sort_values('federate_count').hvplot.line(
                'federate_count',
                'real_time',
                ylabel='real_time (ns)',
                #(range(0, (int(float(echo_df.federate_count.max()))+1), 1)),
                title='timing vs echo: federate_count vs real_time',
                label='{}, run_id: {}, core_type: {}'.format(df2.benchmark.unique(), run_id, core_type),
                alpha=0.5)
            evts.append(evt1*evt2)
    echo_v_timing = (reduce((lambda x, y: x*y), evts)).opts(
                            width=600, 
                            height=360,
                            logx=True,
                            logy=True,
                            legend_position='top_left',
                            fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    core_type_str = '_'.join(core_type_list)
    save_path = os.path.join(output_path, '{}_echo_vs_time_{}Core.png'.format(run_id, core_type_str))
    hvplot.save(echo_v_timing, save_path)
    return echo_v_timing


def plot_echo_vs_echo_c(dataframe1, dataframe2, run_id, core_type_list, output_path):
    """This function creates a multi-line graph for the benchmark,
    cEchoBenchmark and echoBenchmark, of 'federate_count' versus 'real_time' 
    and it is organized by a single 'run_id' and (potential) list of
    core_types.

    Args:
        dataframe1 (obj): A data frame created by make_dataframe filtered by a specific benchmark.
        dataframe2 (obj): A data frame created by make_dataframe filtered by a specific benchmark.
        run_id (str): Specific run_id used to create this plot.
        core_type_list: Specific core_types used to create this plot.
        output_path (path): Location to send the graph.
    Returns:
        echo_vs_echo_c (obj): IPython holoviews plot of the data.
    """
    core_type_list = core_type_list
    evcs = []
    for core_type in core_type_list:
            df1 = dataframe1[(dataframe1.core_type == '{}'.format(core_type)) & (
                        dataframe1.run_id == '{}'.format(run_id))]
            evc1 = df1.sort_values('federate_count').hvplot.line(
                'federate_count',
                'real_time',
                ylabel='real_time (ns)',
                #(range(0, (int(float(echo_df.federate_count.max()))+1), 1)),
                title='timing vs echoBenchmark: federate_count vs real_time',
                label='{}, run_id: {}, core_type: {}'.format(df1.benchmark.unique(), run_id, core_type),
                alpha=0.5)
            df2 = dataframe2[(dataframe2.core_type == '{}'.format(core_type)) & (
                        dataframe2.run_id == '{}'.format(run_id))]
            evc2 = df2.sort_values('federate_count').hvplot.line(
                'federate_count',
                'real_time',
                ylabel='real_time (ns)',
                #(range(0, (int(float(echo_df.federate_count.max()))+1), 1)),
                title='timing vs echo: federate_count vs real_time',
                label='{}, run_id: {}, core_type: {}'.format(df2.benchmark.unique(), run_id, core_type),
                alpha=0.5)
            evcs.append(evc1*evc2)
    echo_vs_echo_c = (reduce((lambda x, y: x*y), evcs)).opts(
                            width=600, 
                            height=360,
                            logx=True,
                            logy=True,
                            legend_position='top_left',
                            fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    core_type_str = '_'.join(core_type_list)
    save_path = os.path.join(output_path, '{}_echo_vs_echoC_{}Core.png'.format(run_id, core_type_str))
    hvplot.save(echo_vs_echo_c, save_path)
    return echo_vs_echo_c


if __name__ == '__main__':
    # file_list = bmpp.get_benchmark_files('C:\Users\barn553\Documents\GitHub\helics_benchmark_results\benchmark_results\2019-11-28')
    # json_results = bmpp.parse_files(file_list)
    # json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    json_file = 'bm_results.json'
    meta_bmk_df = md.make_dataframe(json_file)
    # print(meta_bmk_df.shape)
    meta_bmk_df.sort_values('federate_count').hvplot.line('federate_count', 'real_time')

    ### Testing
    """The main function that tests the above functions."""
    # meta_bmk_df = meta_bmk_df[meta_bmk_df.benchmark == 'echoMessageBenchmark']
    # echo_message = plot_echo_msg(meta_bmk_df, 'Zu60n', os.path.join(os.getcwd()))
    # echo_result = plot_echo_result(meta_bmk_df, 'r1Nr5')
    # message_lookup = plot_msg_lookup(meta_bmk_df, 'r1Nr5')
    # message_send_1 = plot_msg_send_1(meta_bmk_df, 'Md3vp')
    # output_path = os.path.join(os.getcwd(), 'bmk_plotting test images')
    # message_send_3 = plot_msg_send_3_cr(meta_bmk_df, ['aUZF6', 'Zu60n'], 'inproc', output_path, 'mhz_per_cpu')
    # message_send_3
    # message_send_3 = plot_msg_send_3(meta_bmk_df, 'r1Nr5')
    # phold = plot_phold(meta_bmk_df, 'r1Nr5')
    # ring = plot_ring(meta_bmk_df, 'r1Nr5')
    # filtr = plot_filter(meta_bmk_df, 'r1Nr5')
    # source = plot_src(meta_bmk_df, 'r1Nr5')
    # destination = plot_dest(meta_bmk_df, 'r1Nr5')
    # plot_list = [echo_message,
    #              echo_result,
    #              message_lookup,
    #              message_send_2,
    #              message_send_3,
    #              phold,
    #              ring,
    #              filtr,
    #              source,
    #              destination]
    #
    # save_plots(plot_list, 'r1Nr5')