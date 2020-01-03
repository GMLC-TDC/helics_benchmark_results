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
    Returns:
        echo_msg (obj): IPython holoviews plot of the data.
    """

    echo_df = dataframe[dataframe.benchmark == 'echoMessageBenchmark']
    echo_df = echo_df[echo_msg.run_id == '{}'.format(run_id)]
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
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
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
    Returns:
        echo_res (obj): IPython holoviews plot of the data.
    """
    echo_df = dataframe[dataframe.benchmark == 'echoBenchmark']
    echo_df = echo_df[echo_df.run_id == '{}'.format(run_id)]
    echo_res = echo_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} echoBenchmark: federate_count vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
    save_path = os.path.join(output_path, '{}_echoResult.png'.format(run_id))
    hvplot.save(echo_res, save_path)
    return echo_res


def plot_msg_lookup(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    messageLookupBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'inproc'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        msg_lookup (obj): IPython holoviews plot of the data.
    """
    msg_lkp_df = dataframe[dataframe.benchmark == 'messageLookupBenchmark']
    inproc_df = msg_lkp_df[msg_lkp_df.core_type == 'inproc']
    inproc_df = inproc_df[inproc_df.run_id == '{}'.format(run_id)]
    msg_lookup = inproc_df.sort_values('federate_count').hvplot.bar(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} messageLookupBenchmark: federate_count vs real_time'.format(run_id),
        alpha=0.5).opts(
        width=590,
        height=360,
        logx=True,
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
    save_path = os.path.join(output_path, '{}_messageLookup.png'.format(run_id))
    hvplot.save(msg_lookup, save_path)
    return msg_lookup


def plot_msg_send_1(dataframe, run_id, output_path):
    """This function creates a multi-line graph for the benchmark,
    messageSendBenchmark, of 'message_size' versus 'real_time' and
    it is organized by a single 'core_type': 'singleFed'.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id (str): Specific run_id used to create this plot.
    Returns:
        msg_send (obj): IPython holoviews plot of the data.
    """
    msg_snd_df = dataframe[dataframe.benchmark == 'messageSendBenchmark']
    msg_snd_df = msg_snd_df[msg_snd_df.core_type == 'singleCore']
    msg_snd_df = msg_snd_df[msg_snd_df.run_id == '{}'.format(run_id)]
    msg_send = msg_snd_df.sort_values('message_size').hvplot.line(
        'message_size',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} messageSendBenchmark, core_type {}: message_size vs real_time'.format(run_id, 'singleCore'),
        alpha=0.5).opts(
        width=580,
        height=360,
        logx=True,
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
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
    Returns:
        msg_count (obj): IPython holoviews plot of the data.
    """
    msg_snd_df = dataframe[dataframe.benchmark == 'messageSendBenchmark']
    msg_ct_df = msg_snd_df[msg_snd_df.run_id == '{}'.format(run_id)]
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
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
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
    Returns:
        msg_size (obj): IPython holoviews plot of the data.
    """
    msg_snd_df = dataframe[dataframe.benchmark == 'messageSendBenchmark']
    msg_sz_df = msg_snd_df[msg_snd_df.message_size == 1]
    msg_sz_df = msg_sz_df[msg_sz_df.run_id == '{}'.format(run_id)]
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
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
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
    Returns:
        phold (obj): IPython holoviews plot of the data.
    """
    phold_df = dataframe[dataframe.benchmark == 'pholdBenchmark']
    phold_df = phold_df[phold_df.run_id == '{}'.format(run_id)]
    phold = phold_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} pholdBenchmark: federate_count vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
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
    Returns:
        ring (obj): IPython holoviews plot of the data.
    """
    ring_df = dataframe[dataframe.benchmark == 'ringBenchmark']
    ring_df = ring_df[ring_df.run_id == '{}'.format(run_id)]
    ring = ring_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} ringBenchmark: federate_count vs real_time'.format(run_id),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
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
    Returns:
        filtr (obj): IPython holoviews plot of the data.
    """
    filter_df = dataframe[dataframe.benchmark == 'filterBenchmark']
    filter_df = filter_df[filter_df.core_type == 'singleCore']
    filter_df = filter_df[filter_df.run_id == '{}'.format(run_id)]
    filtr = filter_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} filterBenchmark, core_type {}: federate_count vs real_time'.format(run_id, 'singleCore'),
        by='filter_location',
        alpha=0.5).opts(
        width=600,
        height=360,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
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
    Returns:
        source (obj): IPython holoviews plot of the data.
    """
    filter_df = dataframe[dataframe.benchmark == 'filterBenchmark']
    filter_df = filter_df[filter_df.filter_location == 'source']
    filter_df = filter_df[filter_df.run_id == '{}'.format(run_id)]
    source = filter_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} filterBenchmark, filter_location {}: federate_count vs real_time'.format(run_id, 'source'),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
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
    Returns:
        dest (obj): IPython holoviews plot of the data.
    """
    filter_df = dataframe[dataframe.benchmark == 'filterBenchmark']
    filter_df = filter_df[filter_df.filter_location == 'destination']
    filter_df = filter_df[filter_df.run_id == '{}'.format(run_id)]
    dest = filter_df.sort_values('federate_count').hvplot.line(
        'federate_count',
        'real_time',
        ylabel='real_time (ns)',
        title='run_id {} filterBenchmark, filter_location {}: federate_count vs real_time'.format(run_id,
                                                                                                  'destination'),
        by='core_type',
        alpha=0.5).opts(
        width=600,
        height=360,
        logx=True,
        logy=True,
        fontsize={'title': 9, 'labels': 10, 'xticks': 10, 'yticks': 10}
    )
    save_path = os.path.join(output_path, '{}_destination.png'.format(run_id))
    hvplot.save(dest, save_path)
    return dest


### Creating cross-run_idd comparison plots
def plot_echo_msg_cr(dataframe, run_id_list, core_type):
    """This function creates a multi-line graph for the benchmark,
    echoMessageBenchmark, of 'federate_count' versus 'real_time', and
    it is organized by a single 'core_type' and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
    Returns:
        echo_msg_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    echo_msgs = []
    for run_id in run_id_list:
        echo_df = dataframe[
            (dataframe.benchmark == 'echoMessageBenchmark') & (dataframe.core_type == '{}'.format(core_type)) & (
                        dataframe.run_id == '{}'.format(run_id))]
        echo_msg = echo_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {}, core_type: {} echoMessageBenchmark: federate_count vs real_time'.format(run_id_list,
                                                                                                       core_type),
            alpha=0.5).opts(
            width=1000,
            height=600,
            logx=True,
            logy=True)
        echo_msgs.append(echo_msg)
    if len(run_id_list) == 2:
        echo_msg_plot = echo_msgs[0] * echo_msgs[1]
    return echo_msg_plot


def plot_echo_result_cr(dataframe, run_id_list, core_type):
    """This function creates a multi-line graph for the benchmark,
    echoBenchmark, of 'federate_count' versus 'real_time' and
    it is organized a single 'core_type' and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
    Returns:
        echo_res_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    echo_ress = []
    for run_id in run_id_list:
        echo_df = dataframe[
            (dataframe.benchmark == 'echoBenchmark') & (dataframe.core_type == '{}'.format(core_type)) & (
                    dataframe.run_id == '{}'.format(run_id))]
        echo_res = echo_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {}, core_type: {} echoBenchmark: federate_count vs real_time'.format(run_id_list, core_type),
            alpha=0.5).opts(
            width=1000,
            height=600,
            logx=True,
            logy=True)
        echo_ress.append(echo_res)
    if len(run_id_list) == 2:
        echo_res_plot = echo_ress[0] * echo_ress[1]
    return echo_res_plot


def plot_msg_lookup_cr(dataframe, run_id_list):
    """This function creates a multi-line graph for the benchmark,
    messageLookupBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'inproc' and compares
    run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
    Returns:
        msg_lookup_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    msg_lookups = []
    for run_id in run_id_list:
        msg_lkp_df = dataframe[(dataframe.benchmark == 'messageLookupBenchmark') & (dataframe.core_type == 'inproc') & (
                    dataframe.run_id == '{}'.format(run_id))]
        msg_lookup = msg_lkp_df.sort_values('federate_count').hvplot.bar(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {} core_type: inproc messageLookupBenchmark: federate_count vs real_time'.format(
                run_id_list),
            alpha=0.5).opts(
            width=1000,
            height=600,
            logx=True,
            logy=True)
        msg_lookups.append(msg_lookup)
    if len(run_id_list) == 2:
        msg_lookup_plot = msg_lookups[0] * msg_lookups[1]
    return msg_lookup_plot


def plot_msg_send_1_cr(dataframe, run_id_list):
    """This function creates a multi-line graph for the benchmark,
    messageSendBenchmark, of 'message_size' versus 'real_time' and
    it is organized by a single 'core_type': 'singleFed' and compares
    run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
    Returns:
        msg_send_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    msg_sends = []
    for run_id in run_id_list:
        msg_snd_df = dataframe[
            (dataframe.benchmark == 'messageSendBenchmark') & (dataframe.core_type == 'singleFed') & (
                        dataframe.run_id == '{}'.format(run_id))]
        msg_send = msg_snd_df.sort_values('message_size').hvplot.line(
            'message_size',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {} core_type: {} messageSendBenchmark: message_size vs real_time'.format(run_id_list,
                                                                                                    'singleFed'),
            alpha=0.5).opts(
            width=1000,
            height=600,
            logx=True,
            logy=True)
        msg_sends.append(msg_send)
    if len(run_id_list) == 2:
        msg_send_plot = msg_sends[0] * msg_sends[1]
    return msg_send_plot


def plot_msg_send_2_cr(dataframe, run_id_list, core_type):
    """This function creates a multi-line graph for the benchmark,
    messageSendBenchmark, of 'message_size' versus 'real_time' and
    it is organized by a single 'core_type', 'message_count'= 1, and
    compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
    Returns:
        msg_count_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    msg_cts = []
    for run_id in run_id_list:
        msg_ct_df = dataframe[(dataframe.benchmark == 'messageSendBenchmark') & (dataframe.core_type == 'singleFed') & (
                dataframe.run_id == '{}'.format(run_id)) & (dataframe.message_count == 1)]
        msg_count = msg_ct_df.sort_values('message_size').hvplot.line(
            'message_size',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {} core_type: {} messageSendBenchmark, message_count = 1: message_size vs real_time'.format(
                run_id_list, core_type),
            alpha=0.5).opts(
            width=1000,
            height=600,
            logx=True,
            logy=True)
        msg_cts.append(msg_count)
    if len(run_id_list) == 2:
        msg_count_plot = msg_cts[0] * msg_cts[1]
    return msg_count_plot


def plot_msg_send_3_cr(dataframe, run_id_list, core_type):
    """This function creates a multi-line graph for the benchmark,
    messageSendBenchmark, of 'message_count' versus 'real_time' and
    it is organized by a single 'core_type', 'message_size'= 1, and
    compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
    Returns:
        msg_size_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    msg_sizes = []
    for run_id in run_id_list:
        msg_sz_df = dataframe[(dataframe.benchmark == 'messageSendBenchmark') & (dataframe.core_type == 'singleFed') & (
                dataframe.run_id == '{}'.format(run_id)) & (dataframe.message_size == 1)]
        msg_size = msg_sz_df.sort_values('message_count').hvplot.line(
            'message_count',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {} core_type: {} messageSendBenchmark, message_size = 1: message_count vs real_time'.format(
                run_id_list, core_type),
            alpha=0.5).opts(
            width=1000,
            height=600,
            logx=True,
            logy=True)
        msg_sizes.append(msg_size)
    if len(run_id_list) == 2:
        msg_size_plot = msg_sizes[0] * msg_sizes[1]
    return msg_size_plot


def plot_phold_cr(dataframe, run_id_list, core_type):
    """This function creates a multi-line graph for the benchmark,
    pholdBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type' and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
    Returns:
        phold_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    pholds = []
    for run_id in run_id_list:
        phold_df = dataframe[
            (dataframe.benchmark == 'pholdBenchmark') & (dataframe.core_type == '{}'.format(core_type)) & (
                    dataframe.run_id == '{}'.format(run_id))]
        phold = phold_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {} core_type: {} pholdBenchmark: federate_count vs real_time'.format(run_id_list, core_type),
            alpha=0.5).opts(
            width=1000,
            height=600,
            logx=True,
            logy=True)
        pholds.append(phold)
    if len(run_id_list) == 2:
        phold_plot = pholds[0] * pholds[1]
    return phold_plot


def plot_ring_cr(dataframe, run_id_list, core_type):
    """This function creates a multi-line graph for the benchmark,
    ringBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type' and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
    Returns:
        ring_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    rings = []
    for run_id in run_id_list:
        ring_df = dataframe[
            (dataframe.benchmark == 'ringBenchmark') & (dataframe.core_type == '{}'.format(core_type)) & (
                    dataframe.run_id == '{}'.format(run_id))]
        ring = ring_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {} core_type: {} ringBenchmark: federate_count vs real_time'.format(run_id_list, core_type),
            alpha=0.5).opts(
            width=1000,
            height=600,
            logx=True,
            logy=True)
        rings.append(ring)
    if len(run_id_list) == 2:
        ring_plot = rings[0] * rings[1]
    return ring_plot


def plot_filter_cr(dataframe, run_id_list):
    """This function creates a multi-line graph for the benchmark,
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type': 'singleCore' and compares
    run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
    Returns:
        filter_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    filters = []
    for run_id in run_id_list:
        filter_df = dataframe[(dataframe.benchmark == 'filterBenchmark') & (dataframe.core_type == 'singleCore') & (
                dataframe.run_id == '{}'.format(run_id))]
        filtr = filter_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {}, core_type: {} filterBenchmark: federate_count vs real_time'.format(run_id_list,
                                                                                                  'singleCore'),
            by='filter_location',
            alpha=0.5).opts(
            width=1000,
            height=600)
        filters.append(filtr)
    if len(run_id_list) == 2:
        filter_plot = filters[0] * filters[1]
    return filter_plot


def plot_src_cr(dataframe, run_id_list, core_type):
    """This function creates a multi-line graph for the benchmark,
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type', 'filter_location' = 'source',
    and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
    Returns:
        source_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    sources = []
    for run_id in run_id_list:
        filter_df = dataframe[
            (dataframe.benchmark == 'filterBenchmark') & (dataframe.core_type == '{}'.format(core_type)) & (
                    dataframe.run_id == '{}'.format(run_id)) & (dataframe.filter_location == 'source')]
        source = filter_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {} core_type: {}, filterBenchmark, filter_location {}: federate_count vs real_time'.format(
                run_id_list, core_type, 'source'),
            alpha=0.5).opts(
            width=1000,
            height=600,
            logx=True,
            logy=True)
        sources.append(source)
    if len(run_id_list) == 2:
        source_plot = sources[0] * sources[1]
    return source_plot


def plot_dest_cr(dataframe, run_id_list, core_type):
    """This function creates a multi-line graph for the benchmark,
    filterBenchmark, of 'federate_count' versus 'real_time' and
    it is organized by a single 'core_type', 'filter_location' = 'destination',
    and compares run_ids' data.

    Args:
        dataframe (obj): A data frame created by make_dataframe.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
    Returns:
        dest_plot (obj): IPython holoviews plot of the data.
    """
    run_id_list = run_id_list
    dests = []
    for run_id in run_id_list:
        filter_df = dataframe[
            (dataframe.benchmark == 'filterBenchmark') & (dataframe.core_type == '{}'.format(core_type)) & (
                    dataframe.run_id == '{}'.format(run_id)) & (dataframe.filter_location == 'destination')]
        filter_df = filter_df[filter_df.run_id == '{}'.format(run_id)]
        dest = filter_df.sort_values('federate_count').hvplot.line(
            'federate_count',
            'real_time',
            ylabel='real_time (ns)',
            title='run_ids {} core_type: {}, filterBenchmark, filter_location {}: federate_count vs real_time'.format(
                run_id_list, core_type, 'destination'),
            alpha=0.5).opts(
            width=1000,
            height=600,
            logx=True,
            logy=True)
        dests.append(dest)
    if len(run_id_list) == 2:
        dest_plot = dests[0] * dests[1]
    return dest_plot


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


def save_plots_cr(plot_list, run_id_list, core_type):
    """This function saves the desired plots as .png files.

    Args:
        plot_list (list): List of plots desired to save.
        run_id_list (list): Specific run_ids used to create this plot.
        core_type (str): Specific core_type for cross-run_id comparison plots.
    """

    i = 1
    plot_list = plot_list
    for p in plot_list:
        hvplot.save(p, 'run_ids {} plot_{}.png'.format(run_id_list, i))
        i += 1


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
    # echo_message = plot_echo_msg(meta_bmk_df, 'r1Nr5')
    # echo_result = plot_echo_result(meta_bmk_df, 'r1Nr5')
    # message_lookup = plot_msg_lookup(meta_bmk_df, 'r1Nr5')
    # #    message_send_1 = plot_msg_send_1(meta_bmk_df, 'Md3vp')
    # message_send_2 = plot_msg_send_2(meta_bmk_df, 'r1Nr5')
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
