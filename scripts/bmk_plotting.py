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

def sa_plot(dataframe, x_axis, y_axis, bm_name, by_bool, by_name, run_id, output_path):
    """This function creates a plot of the specified data and sends it
    to the output_path.
    
    Args:
        dataframe (obj): Pandas dataframe object of specified data to be
        plotted.
        x_axis (str): x-axis data from the dataframe object that should be 
        given to the hvplot.line() function.
        y_axis (str): y-axis data from the dataframe object that should be
        given to the hvplot.line() function.
        bm_name (str): Specific benchmark's name to be added to the 
        title of the graph.
        by_bool (bool): If True, the keyword argument 'by' will be added
        to the hvplot.line() function along with the by_name parameter; 
        otherwise, 'by' will not be added.
        by_name (str): Parameter for the 'by' keyword argument in the
        hvplot.line() function; only add if by_bool equals True.
        run_id (str): 5 character unique identifier for the run-ID.
        output_path (path): Path where graphs should be saved.
    
    Returns:
        plot (obj): Holoviews object of the graphed data
        
    """
    if by_bool == True:
        dataframe = dataframe.groupby(
                ['{}'.format(by_name), 
                 '{}'.format(x_axis)])['{}'.format(y_axis)].min().reset_index()
        plot = dataframe.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis), 
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                title='run_id {} {}: {} vs {}'.format(
                        run_id,
                        bm_name, 
                        x_axis, 
                        y_axis),
                by='{}'.format(by_name),
                alpha=0.5).opts(
                        width=590,
                        height=360,
                        logx=True,
                        logy=True,
                        fontsize={'title': 9.5, 
                                  'labels': 10, 
                                  'legend': 9, 
                                  'xticks': 10, 
                                  'yticks': 10})
    else:
        dataframe = dataframe.groupby(
                '{}'.format(x_axis))['{}'.format(y_axis)].min().reset_index()
        plot = dataframe.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis), 
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                title='run_id {} {}: {} vs {}'.format(
                        run_id,
                        bm_name, 
                        x_axis, 
                        y_axis),
                alpha=0.5).opts(
                        width=590,
                        height=360,
                        logx=True,
                        logy=True,
                        fontsize={'title': 9.5, 
                                  'labels': 10, 
                                  'legend': 9, 
                                  'xticks': 10, 
                                  'yticks': 10})
    save_path = os.path.join(output_path, '{}_{}.png'.format(run_id, bm_name))
    hvplot.save(plot, save_path)
    return plot


#-----------------------------------------------------------------------#
#------------------  Cross-run_id comparison plots ---------------------#
def cr_plot(dataframe, x_axis, y_axis, bm_name, run_id_list, core_type, comparison_parameter, output_path):
    """This function creates a plot for 2 or more run_ids to compare their
    benchmark and the differences in their comparison_parameters.
    
    Args:
        dataframe (obj): Pandas dataframe object of specified data to be
        plotted.
        x_axis (str): x-axis data from the dataframe object that should be 
        given to the hvplot.line() function.
        y_axis (str): y-axis data from the dataframe object that should be
        given to the hvplot.line() function.
        bm_name (str): Specific benchmark's name to be added to the 
        title of the graph.
        title_part (str): Part of the title that has specified information
        in it and will be added to the 'title' keyword argument.
        run_id_list (list): List of run_ids for which to make the plots.
        core_type (str): Specific core_type to plot.
        comparison_parameter (str): Specific paramter to compare between
        run_ids.
        output_path (path): Path to send the graphs.
    
    Returns:
        plot (obj): Holoviews object of the graphed data.
        
    """
    my_plots = []
    for run_id in run_id_list:
        plots = dataframe[(dataframe.run_id == '{}'.format(run_id)) & 
                          (dataframe.core_type == '{}'.format(core_type))]
        x_y_map = plots.groupby(
                '{}'.format(x_axis))['{}'.format(y_axis)].min().reset_index()
        plots = x_y_map.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis), 
                '{}'.format(y_axis), 
                title='{}: {} vs {}'.format(
                        bm_name, 
                        x_axis,
                        y_axis),
                label='run_id: {}, core_type: {}, {}: {}'.format(
                        run_id,
                        core_type,
                        comparison_parameter,
                        plots['{}'.format(comparison_parameter)].unique()), 
                alpha=0.5)
        my_plots.append(plots)
    plot = (reduce((lambda x, y: x*y), my_plots)).opts(
                            width=590, 
                            height=360,
                            logx=True,
                            logy=True,
                            legend_position='top_left',
                            fontsize={'title': 9.5, 
                                      'labels': 10, 
                                      'legend': 9, 
                                      'xticks': 10, 
                                      'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_{}_{}Core.png'.format(
            run_id_str, 
            bm_name,
            core_type))
    hvplot.save(plot, save_path)
    return plot


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
        echo_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & 
                        (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
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
                        width=590, 
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
        echo_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & 
                    (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
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
                        width=590, 
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
        echo_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & 
                    (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
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
                        width=590, 
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
        msg_lkp_df = dataframe[(dataframe.core_type == 'inproc') & 
                    (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full') & (dataframe.federate_count == 2)]
        msg_lookup = msg_lkp_df.sort_values('interface_count').hvplot.line(
            'interface_count',
            'real_time',
            ylabel='real_time (ns)',
            title='fed_ct = 2, messageLookup: interface_count vs real_time',
            label='run_id: {}, core_type: inproc, {}: {}'.format(run_id, comparison_parameter, msg_lkp_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_lookups.append(msg_lookup)
    msg_lookup_plot = reduce((lambda x, y: x*y), msg_lookups).opts(
                        width=590, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_messageLookup1.png'.format(run_id_str))
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
        msg_lkp_df = dataframe[(dataframe.core_type == 'inproc') & 
                    (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full') & (dataframe.federate_count == 8)]
        msg_lookup = msg_lkp_df.sort_values('interface_count').hvplot.line(
            'interface_count',
            'real_time',
            ylabel='real_time (ns)',
            title='fed_ct = 8, messageLookup: interface_count vs real_time',
            label='run_id: {}, core_type: inproc, {}: {}'.format(run_id, comparison_parameter, msg_lkp_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_lookups.append(msg_lookup)
    msg_lookup_plot = reduce((lambda x, y: x*y), msg_lookups).opts(
                        width=590, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='top_left',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}_messageLookup2.png'.format(run_id_str))
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
        msg_lkp_df = dataframe[(dataframe.core_type == 'inproc') & 
                    (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full') & (dataframe.federate_count == 64)]
        msg_lookup = msg_lkp_df.sort_values('interface_count').hvplot.line(
            'interface_count',
            'real_time',
            ylabel='real_time (ns)',
            title='fed_ct = 64, messageLookup: interface_count vs real_time',
            label='run_id: {}, core_type: inproc, {}: {}'.format(run_id, comparison_parameter, msg_lkp_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_lookups.append(msg_lookup)
    msg_lookup_plot = reduce((lambda x, y: x*y), msg_lookups).opts(
                        width=590, 
                        height=360, 
                        logx=True, 
                        logy=True, 
                        legend_position='bottom_right',
                        fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(output_path, '{}__messageLookup3.png'.format(run_id_str))
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
        msg_snd_df = dataframe[(dataframe.core_type == 'singleCore') & 
                        (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
        msg_send = msg_snd_df.sort_values('message_size').hvplot.line(
            'message_size',
            'real_time',
            ylabel='real_time (ns)',
            title='messageSendBenchmark: message_size vs real_time',
            label='run_id: {}, core_type: singleCore, {}: {}'.format(run_id, comparison_parameter, msg_snd_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_sends.append(msg_send)
    msg_send_plot = (reduce((lambda x, y: x*y), msg_sends)).opts(
                        width=590, 
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
        msg_ct_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & 
                (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full') & (dataframe.message_count == 1)]
        x_y_map = msg_ct_df.groupby('message_size')['real_time'].min().reset_index()
        msg_count = x_y_map.sort_values('message_size').hvplot.line(
            'message_size',
            'real_time',
            ylabel='real_time (ns)',
            title='msg_ct = 1, messageSendBenchmark: message_size vs real_time', 
            label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, msg_ct_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_cts.append(msg_count)
    msg_count_plot = (reduce((lambda x, y: x*y), msg_cts)).opts(
                        width=590, 
                        height=360, 
                        logx=True, 
                        logy=True, 
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
        msg_sz_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & 
                (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full') & (dataframe.message_size == 1)]
        msg_size = msg_sz_df.sort_values('message_count').hvplot.line(
            'message_count',
            'real_time',
            ylabel='real_time (ns)',
            title='msg_sz = 1, messageSendBenchmark: message_count vs real_time',
            label='run_id: {}, core_type: {}, {}: {}'.format(run_id, core_type, comparison_parameter, msg_sz_df['{}'.format(comparison_parameter)].unique()),
            alpha=0.5)
        msg_sizes.append(msg_size)
    msg_size_plot = (reduce((lambda x, y: x*y), msg_sizes)).opts(
                        width=590, 
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
        phold_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & 
                    (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
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
                        width=590, 
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
            ring_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & 
                        (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
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
                            width=590, 
                            height=360, 
                            legend_position='top_left',
                            fontsize={'title': 9.5, 'labels': 10, 'legend': 9, 'xticks': 10, 'yticks': 10})
    else:
        for run_id in run_id_list:
            ring_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & (
                        (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full'))]
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
                            width=590, 
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
        filter_df = dataframe[(dataframe.core_type == 'singleCore') & 
                (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full')]
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
                        width=590, 
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
        filter_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & 
                    (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full') & (dataframe.filter_location == 'source')]
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
                        width=590, 
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
        filter_df = dataframe[(dataframe.core_type == '{}'.format(core_type)) & 
                    (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full') & (dataframe.filter_location == 'destination')]
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
                        width=590, 
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
                        (dataframe.run_id == '{}'.format(run_id)) & (dataframe.benchmark_type == 'full'))]
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
                        width=590, 
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
def ir_plot(dataframe1, dataframe2, x_axis, y_axis, bm_name1, bm_name2, metric_bool, metric_type, title_part, run_id, core_type, output_path):
    """This function creates a graph that compares different benchmark results
    data for a single run_id and core_type.
    
    Args:
        dataframe1 (obj): First dataframe filtered to a specific benchmark.
        dataframe2 (obj): Second dataframe filtered to another benchmark; the 
        graph will compare both dataframes' data.
        x_axis (str): x-axis data from the dataframe object that should be 
        given to the hvplot.line() function.
        y_axis (str): y-axis data from the dataframe object that should be
        given to the hvplot.line() function.
        bm_name1 (str): Specific benchmark's name to be added to the 
        title of the graph.
        bm_name2 (str): Specific benchmark's name to be added to the 
        title of the graph.
        metric_bool (bool):  If a metric plot is needed (such as counts per
        second), then this is True, and it will have a corresponding
        metric_type; otherwise, it will be False.
        metric_type (str): A type of metric (if it exists) to make a plot for
        bm_name (str): Specific benchmark's name to be added to the 
        title of the graph.
        title_part (str): Part of the title that has specified information
        in it and will be added to the 'title' keyword argument. 
        run_id (str): 5 character unique identifier for the run-ID.
        core_type (str): Specific core_type to plot.
        output_path (path): Path to send the graphs.
    """
    if metric_bool == True:
        if metric_type == 'seconds_per_count' or metric_type == 'spc':
            df1 = dataframe1[(dataframe1.run_id == '{}'.format(run_id)) &
                             (dataframe1.core_type == '{}'.format(core_type))]
            df2 = dataframe2[(dataframe2.run_id == '{}'.format(run_id)) &
                             (dataframe2.core_type == '{}'.format(core_type))]
            
            gpd1 = df1.groupby('{}'.format(x_axis))['{}'.format(y_axis)].sum()\
                / df1.groupby('{}'.format(x_axis))['{}'.format(x_axis)].sum()
            gpd1.name = 'seconds_per_count'
            gpd2 = df2.groupby('{}'.format(x_axis))['{}'.format(y_axis)].sum()\
                / df2.groupby('{}'.format(x_axis))['{}'.format(x_axis)].sum()
            gpd2.name = 'seconds_per_count'
            
            plot1 = gpd1.reset_index().sort_values('{}'.format(x_axis)).hvplot.line(
                    '{}'.format(x_axis), 
                    'seconds_per_count', 
                    title='{} v {} {}: {} vs {}'.format(
                            bm_name1,
                            bm_name2,
                            title_part,
                            x_axis,
                            'seconds_per_count'),
                    label='{}, run_id: {}, core_type: {}'.format(
                            df1.benchmark.unique(),
                            run_id,
                            core_type),
                    alpha=0.5)
            plot2 = gpd2.reset_index().sort_values('{}'.format(x_axis)).hvplot.line(
                    '{}'.format(x_axis), 
                    'seconds_per_count', 
                    title='{} v {} {}: {} vs {}'.format(
                            bm_name1,
                            bm_name2,
                            title_part,
                            x_axis,
                            'seconds_per_count'),
                    label='{}, run_id: {}, core_type: {}'.format(
                            df2.benchmark.unique(),
                            run_id,
                            core_type),
                    alpha=0.5)
            core_type_str = ''.join(core_type)
            save_path = os.path.join(output_path, '{}_{}_vs_{}_{}Core{}.png'.format(
                    run_id, 
                    bm_name1, 
                    bm_name2, 
                    core_type_str,
                    metric_type))
                    
        elif metric_type == 'average':
            pass
        elif metric_type == 'total':
            pass
        elif metric_type == 'max':
            pass
        elif metric_type == 'min':
            pass
        else:
            pass
    else:
        df1 = dataframe1[(dataframe1.run_id == '{}'.format(run_id)) &
                         (dataframe1.core_type == '{}'.format(core_type))]
        df2 = dataframe2[(dataframe2.run_id == '{}'.format(run_id)) &
                         (dataframe2.core_type == '{}'.format(core_type))]
        plot1 = df1.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis), 
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                title='{} v {} {}: {} vs {}'.format(
                        bm_name1,
                        bm_name2,
                        title_part,
                        x_axis,
                        y_axis),
                label='{}, run_id: {}, core_type: {}'.format(
                        df1.benchmark.unique(),
                        run_id,
                        core_type),
                alpha=0.5)
        plot2 = df2.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis), 
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                title='{} v {} {}: {} vs {}'.format(
                        bm_name1,
                        bm_name2,
                        title_part,
                        x_axis,
                        y_axis),
                label='{}, run_id: {}, core_type: {}'.format(
                        df2.benchmark.unique(),
                        run_id,
                        core_type),
                alpha=0.5)
        core_type_str = ''.join(core_type)
        save_path = os.path.join(output_path, '{}_{}_vs_{}_{}Core.png'.format(
                run_id, 
                bm_name1, 
                bm_name2, 
                core_type_str))
    plots = [plot1, plot2]
    plot = (reduce((lambda x, y: x*y), plots)).opts(
                            width=590, 
                            height=360,
                            logx=True,
                            logy=True,
                            legend_position='top_left',
                            fontsize={'title': 9.5, 
                                      'labels': 10, 
                                      'legend': 9, 
                                      'xticks': 10, 
                                      'yticks': 10})
    
    hvplot.save(plot, save_path)
    return plot


#-----------------------------------------------------------------------#
#------------------  Multinode benchmark result plots ------------------#
def mm_plot(dataframe, x_axis, y_axis, param1, param2, metric_bool, metric_type, bm_name, title_part, output_path):
    """This function creates a multi-line graph for multinode benchmark 
    results. For example, it compares N1-N8 versus total elapsed time.
    
    Args:
        dataframe (obj): Pandas dataframe object that contains all the
        multinode benchmark results data.
        x_axis (str): x-axis data from the dataframe object that should be 
        given to the hvplot.line() function.
        y_axis (str): y-axis data from the dataframe object that should be
        given to the hvplot.line() function.
        param1 (str): Used to filter dataframe within the .groupby() function.
        param2 (str): Used to filter dataframe within the .groupby() function.
        metric_bool (bool):  If a metric plot is needed (such as counts per
        second), then this is True, and it will have a corresponding
        metric_type; otherwise, it will be False.
        metric_type (str): A type of metric (if it exists) to make a plot for
        bm_name (str): Specific benchmark's name to be added to the 
        title of the graph.
        title_part (str): Part of the title that has specified information
        in it and will be added to the 'title' keyword argument. 
        image_name (str): Name to call the graph.
        output_path (path): Path to send the graphs.
    """
    if metric_bool == True:
        if metric_type == 'counts_per_second' or metric_type == 'cps':
            gpd = dataframe.groupby(['{}'.format(x_axis), 
                                     '{}'.format(param1)])['{}'.format(param2)].sum()\
                    /dataframe.groupby(['{}'.format(x_axis), 
                                       '{}'.format(param1)])['{}'.format(y_axis)].mean()
            gpd.name = 'counts_per_second'
            plot = gpd.reset_index().sort_values('{}'.format(x_axis)).hvplot.line(
                    '{}'.format(x_axis), 
                    'counts_per_second', 
                    title='{} {}: counts/s vs {}'.format(
                            title_part,
                            bm_name,
                            x_axis),
                    by='{}'.format(param1),
                    alpha=0.5).opts(
                            width=590,
                            height=360,
                            logy=True,
                            fontsize={'title': 9.5, 
                                      'labels': 10, 
                                      'legend': 9, 
                                      'xticks': 10, 
                                      'yticks': 10})
            save_path = os.path.join(output_path, 
                                     '{}_{}.png'.format(bm_name, 
                                                        metric_type))
        if metric_type == 'sum':
            gpd = dataframe.groupby(['{}'.format(x_axis), 
                                     '{}'.format(param1)])['{}'.format(y_axis)].sum()
            plot = gpd.reset_index().sort_values('{}'.format(x_axis)).hvplot.line(
                    '{}'.format(x_axis), 
                    '{}'.format(y_axis), 
                    title='{} {}: {} {} vs {}'.format(
                            title_part,
                            bm_name,
                            y_axis,
                            metric_type,
                            x_axis),
                    by='{}'.format(param1),
                    alpha=0.5).opts(
                            width=590,
                            height=360,
                            logy=True,
                            fontsize={'title': 9.5, 
                                      'labels': 10, 
                                      'legend': 9, 
                                      'xticks': 10, 
                                      'yticks': 10})
            save_path = os.path.join(output_path, 
                                     '{}_{}_{}.png'.format(bm_name,
                                                           y_axis,
                                                           metric_type))
        if metric_type == 'average' or metric_type == 'mean':
            gpd = dataframe.groupby(['{}'.format(x_axis), 
                                     '{}'.format(param1)])['{}'.format(y_axis)].mean()
            plot = gpd.reset_index().sort_values('{}'.format(x_axis)).hvplot.line(
                    '{}'.format(x_axis), 
                    '{}'.format(y_axis), 
                    title='{} {}: {} {} vs {}'.format(
                            title_part,
                            bm_name,
                            y_axis,
                            metric_type,
                            x_axis),
                    by='{}'.format(param1),
                    alpha=0.5).opts(
                            width=590,
                            height=360,
                            logy=True,
                            fontsize={'title': 9.5, 
                                      'labels': 10, 
                                      'legend': 9, 
                                      'xticks': 10, 
                                      'yticks': 10})
            save_path = os.path.join(output_path, 
                                     '{}_{}_{}.png'.format(bm_name,
                                                           y_axis,
                                                           metric_type))
        if metric_type == 'max':
            gpd = dataframe.groupby(['{}'.format(x_axis), 
                                     '{}'.format(param1)])['{}'.format(y_axis)].max()
            plot = gpd.reset_index().sort_values('{}'.format(x_axis)).hvplot.line(
                    '{}'.format(x_axis), 
                    '{}'.format(y_axis), 
                    title='{} {}: {} {} vs {}'.format(
                            title_part,
                            bm_name,
                            y_axis,
                            metric_type,
                            x_axis),
                    by='{}'.format(param1),
                    alpha=0.5).opts(
                            width=590,
                            height=360,
                            logy=True,
                            fontsize={'title': 9.5, 
                                      'labels': 10, 
                                      'legend': 9, 
                                      'xticks': 10, 
                                      'yticks': 10})
            save_path = os.path.join(output_path, 
                                     '{}_{}_{}.png'.format(bm_name,
                                                           y_axis,
                                                           metric_type))
        if metric_type == 'min':
            gpd = dataframe.groupby(['{}'.format(x_axis), 
                                     '{}'.format(param1)])['{}'.format(y_axis)].min()
            plot = gpd.reset_index().sort_values('{}'.format(x_axis)).hvplot.line(
                    '{}'.format(x_axis), 
                    '{}'.format(y_axis), 
                    title='{} {}: {} {} vs {}'.format(
                            title_part,
                            bm_name,
                            y_axis,
                            metric_type,
                            x_axis),
                    by='{}'.format(param1),
                    alpha=0.5).opts(
                            width=590,
                            height=360,
                            logy=True,
                            fontsize={'title': 9.5, 
                                      'labels': 10, 
                                      'legend': 9, 
                                      'xticks': 10, 
                                      'yticks': 10})
            save_path = os.path.join(output_path, 
                                     '{}_{}_{}.png'.format(bm_name,
                                                           y_axis,
                                                           metric_type))
    else:
        pass
    
    hvplot.save(plot, save_path)
    return plot
 

if __name__ == '__main__':
    # file_list = bmpp.get_benchmark_files('C:\Users\barn553\Documents\GitHub\helics_benchmark_results\benchmark_results\2019-11-28')
    # json_results = bmpp.parse_files(file_list)
    # json_results = bmpp.parse_and_add_benchmark_metadata(json_results)
    json_file = 'bm_results.json'
    meta_bmk_df = md.make_dataframe1(json_file)
    # print(meta_bmk_df.shape)
    meta_bmk_df.sort_values('federate_count').hvplot.line('federate_count', 'real_time')

    ### Testing
    """The main function that tests the above functions."""
    # echo_message = plot_echo_msg_cr(meta_bmk_df, ['r1Nr5'], 'inproc', os.path.join(os.getcwd()), 'mhz_per_cpu')
    # echo_result = plot_echo_result(meta_bmk_df, 'r1Nr5')
    # message_lookup = plot_msg_lookup(meta_bmk_df, 'r1Nr5')
    # message_send_1 = plot_msg_send_1(meta_bmk_df, 'Md3vp')

    # output_path = os.path.join(os.getcwd())
    # multi_bmk_df = md.make_dataframe2('multinode_bm_results.json')
    # benchmark = 'PholdFederate'
    # plot = plot_counts_per_second(multi_bmk_df, benchmark, output_path)
    # plot
    # message_send_3 = plot_msg_send_3_cr(meta_bmk_df, ['aUZF6', 'Zu60n'], 'inproc', output_path, 'mhz_per_cpu')
    # message_send_3
    # message_send_3 = plot_msg_send_3(meta_bmk_df, 'r1Nr5')
    # phold = plot_phold(meta_bmk_df, 'r1Nr5')
    # df1 = meta_bmk_df[meta_bmk_df.benchmark == 'echoBenchmark']
    # df2 = meta_bmk_df[meta_bmk_df.benchmark == 'timingBenchmark']
    # plot = plot_echo_vs_timing(df1, df2, 'YidUg', 'singleCore', output_path)
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



