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


def sa_plot(dataframe, x_axis, y_axis, bm_name, bm_type, by_bool, by_name, run_id, output_path):
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
        bm_type (str): Benchmark_type = 'full' or 'key'.
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
    if bm_type == 'full':
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
            save_path = os.path.join(output_path, '{}_{}.png'.format(run_id, bm_name))
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
    elif bm_type == 'key':
        dataframe = dataframe.groupby(
                    ['{}'.format(by_name), 
                     '{}'.format(x_axis)])['{}'.format(y_axis)].min().reset_index()
        plot = dataframe.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis), 
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                title='{} tracking: {} vs {}'.format(
                        bm_name, 
                        x_axis, 
                        y_axis),
                by='{}'.format(by_name),
                alpha=0.5, 
                rot=90).opts(
                        width=590,
                        height=360,
                        logx=True,
                        logy=True,
                        fontsize={'title': 9.5, 
                                  'labels': 10, 
                                  'legend': 9, 
                                  'xticks': 10, 
                                  'yticks': 10})
        save_path = os.path.join(output_path, '{}_tracking.png'.format(bm_name))
    
    hvplot.save(plot, save_path)
    return plot


#-----------------------------------------------------------------------#
#------------------  Cross-run_id comparison plot ----------------------#
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



#-----------------------------------------------------------------------#
#------------------  Cross-benchmark comparison plot -------------------#
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
#------------------  Multinode benchmark result plot -------------------#
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
    json_file = 'bm_results.json'
    meta_bmk_df = md.make_dataframe1(json_file)
    # print(meta_bmk_df.shape)
    meta_bmk_df.sort_values('federate_count').hvplot.line('federate_count', 'real_time')
