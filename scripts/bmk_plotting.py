# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 19:03:59 2019

This script provides general plotting functions
for analysis reports.  These functions take a set of specified
arguments and create a Holoviews plot object of that set.  These
functions also save each plot as a .png, which eases the
ability to incorporate plots into the analysis reports.

Further descriptions of the functions are contained in the
documentation string of each function.

@author: barn553
"""

import logging
from functools import reduce
import os
import hvplot.pandas
import numpy as np

# Setting up logging
logger = logging.getLogger(__name__)


def sa_plot(
        dataframe, x_axis, y_axis, bm_name,
        by_bool, by_name, run_id, output_path):
    """This function creates a plot of the specified data and sends it
    to the output_path.

    The target use of this function is for the standard analysis
    and benchmark tracking reports.

    Args:
        dataframe (pandas dataframe) - Contains all benchmark results
        and associated metadata.

        x_axis (str) - x-axis data from the dataframe object that should be
        given to the hvplot.line() function.

        y_axis (str) - y-axis data from the dataframe object that should be
        given to the hvplot.line() function.

        bm_name (str) - Specific benchmark's name; added to the
        title of the graph and name of the saved image.

        bm_type (str) - Benchmark_type = 'full' or 'key'.

        by_bool (bool) - If True, the keyword argument 'by' will be added
        to the hvplot.line() function, along with the by_name parameter;
        otherwise, 'by' will not be added.

        by_name (str) - Parameter for the 'by' keyword argument in the
        hvplot.line() function; only added if by_bool equals True.
        run_id (str) - 5 character unique identifier for the run-ID.

        output_path (str) - Path where graphs should be saved.

    Returns:
        (null)
    """
    if dataframe.benchmark_type.unique() == 'full':
        TITLE = 'run_id {} {}: {} vs {}'.format(
            run_id, bm_name, x_axis, y_axis)
    else:
        TITLE = '{} {}: {} vs {}'.format(
            run_id, bm_name, x_axis, y_axis)
    benchmark = dataframe.benchmark.unique()[0]
    if by_bool is True:
        if 'pholdBenchmark' == benchmark:
            p_title = 'run_id {} {}: {} vs {}'.format(
                run_id, bm_name, x_axis, 'EvCount_per_second')
            dataframe = dataframe.groupby(
                ['{}'.format(by_name),
                 'EvCount',
                 '{}'.format(x_axis)])['{}'.format(y_axis)].min().reset_index()
            dataframe['EvCount_per_second'] = dataframe['EvCount']\
                / dataframe['real_time']
            min_y = dataframe['{}'.format(y_axis)].min()
            plot = dataframe.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                'EvCount_per_second',
                ylabel='EvCount_per_second',
                line_width=3,
                by='{}'.format(by_name),
                rot=90,
                alpha=0.75).opts(
                    width=625, height=380, logx=True,
                    logy=True, legend_position='bottom_right', legend_cols=2,
                    ylim=(10.0**(2), None), fontsize={
                        'title': 8.5, 'labels': 10, 'legend': 8,
                        'legend_title': 8, 'xticks': 8, 'yticks': 10},
                    title=p_title)
            save_path = os.path.join(
                output_path, '{}_{}.png'.format(run_id, bm_name))
        elif 'messageSendBenchmark' == benchmark:
            dataframe = dataframe.groupby(
                ['{}'.format(x_axis),
                 '{}'.format(by_name)])[
                     '{}'.format(y_axis)].min().reset_index()
            min_y = dataframe['{}'.format(y_axis)].min()
            plot = (dataframe.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                line_width=3,
                by='{}'.format(by_name),
                rot=90,
                alpha=0.75) * dataframe.sort_values(
                    '{}'.format(x_axis)).hvplot.scatter(
                        '{}'.format(x_axis),
                        '{}'.format(y_axis),
                        ylabel='{} (s)'.format(y_axis),
                        by='{}'.format(by_name),
                        alpha=0.75)).opts(
                            width=625, height=380,
                            logx=True, logy=True,
                            legend_position='bottom_right', legend_cols=2,
                            yformatter='%.4f', ylim=(min_y*10.0**(-1), None),
                            title=TITLE, fontsize={
                                'title': 8.5, 'labels': 10,
                                'legend': 8, 'legend_title': 8,
                                'xticks': 8, 'yticks': 10})
            save_path = os.path.join(
                output_path, '{}_{}.png'.format(run_id, bm_name))
        else:
            # Filtering the dataframe so that there are not
            # any duplicate 'y-values' to plot; otherwise, there
            # will be spikes in the graph.
            dataframe = dataframe.groupby(
                ['{}'.format(by_name),
                 '{}'.format(x_axis)])['{}'.format(y_axis)].min().reset_index()
            min_y = dataframe['{}'.format(y_axis)].min()
            plot = dataframe.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                line_width=3,
                by='{}'.format(by_name),
                rot=90,
                alpha=0.75).opts(
                    width=625, height=380,
                    logx=True, logy=True,
                    legend_position='bottom_right', legend_cols=2,
                    yformatter='%.3f', ylim=(min_y*10.0**(-2), None),
                    title=TITLE, fontsize={
                        'title': 8.5, 'labels': 10, 'legend': 8,
                        'legend_title': 8, 'xticks': 8, 'yticks': 10})
            save_path = os.path.join(
                output_path, '{}_{}.png'.format(run_id, bm_name))
    else:
        if 'messageSendBenchmark' == benchmark:
            dataframe = dataframe.groupby(
                '{}'.format(x_axis))['{}'.format(y_axis)].min().reset_index()
            min_y = dataframe['{}'.format(y_axis)].min()
            plot = (dataframe.sort_values('{}'.format(x_axis)).hvplot.scatter(
                '{}'.format(x_axis),
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                rot=90,
                alpha=0.75) * dataframe.sort_values(
                    '{}'.format(x_axis)).hvplot.line(
                        '{}'.format(x_axis),
                        '{}'.format(y_axis),
                        ylabel='{} (s)'.format(y_axis),
                        line_width=3,
                        rot=90,
                        alpha=0.75)).opts(
                            width=625, height=380,
                            logx=True, logy=True,
                            yformatter='%.3f', ylim=(min_y*10.0**(-1), None),
                            title=TITLE, fontsize={
                                'title': 8.5, 'labels': 10,
                                'legend': 8, 'legend_title': 8,
                                'xticks': 8, 'yticks': 10})
            save_path = os.path.join(
                output_path, '{}_{}.png'.format(run_id, bm_name))
        elif 'messageLookupBenchmark' == benchmark:
            dataframe = dataframe.groupby(
                '{}'.format(x_axis))['{}'.format(y_axis)].min().reset_index()
            min_y = dataframe['{}'.format(y_axis)].min()
            plot = dataframe.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                line_width=3,
                rot=90,
                alpha=0.75).opts(
                    width=625, height=380, logx=True,
                    logy=True, title=TITLE, fontsize={
                        'title': 8.5, 'labels': 10, 'legend': 8,
                        'xticks': 8, 'yticks': 10})
            save_path = os.path.join(
                output_path, '{}_{}.png'.format(run_id, bm_name))
        else:
            dataframe = dataframe.groupby(
                '{}'.format(x_axis))['{}'.format(y_axis)].min().reset_index()
            min_y = dataframe['{}'.format(y_axis)].min()
            plot = dataframe.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                line_width=3,
                rot=90,
                alpha=0.75).opts(
                    width=625, height=380,
                    logx=True, logy=True,
                    legend_position='bottom_right', legend_cols=2,
                    yformatter='%.2f', ylim=(min_y*10.0**(-1), None),
                    title=TITLE, fontsize={
                        'title': 8.5, 'labels': 10, 'legend': 8,
                        'legend_title': 8, 'xticks': 8, 'yticks': 10})
            save_path = os.path.join(
                output_path, '{}_{}.png'.format(run_id, bm_name))
    hvplot.save(plot, save_path)
    logging.info('Created graph file {}'.format(output_path))
    # return plot


def cr_plot(
        dataframe, x_axis, y_axis, bm_name,
        run_id_list, core_type, comparison_parameter, output_path):
    """This function creates a plot for 2 or more run_ids to compare their
    benchmark(s) and the differences in their comparison_parameters.

    The use for this function is to compare the results of different
    comparison parameters for a given set of run_ids.  The comparison
    parameter that is specified will be different for each run_id, but
    other run_ids' data will be identical; hence why we want to compare
    it across the run_ids in the run_id_list

    Args:
        dataframe (pandas dataframe) - Contains all benchmark results
        and associated metadata.

        x_axis (str) - x-axis data from the dataframe object that should be
        given to the hvplot.line() function.

        y_axis (str) - y-axis data from the dataframe object that should be
        given to the hvplot.line() function.

        bm_name (str) - Specific benchmark's name; added to the
        title of the graph and name of the saved image.

        run_id_list (list) - List of run_ids for making comparison plots.

        core_type (str) - Specific core_type to filter the data
        and to plot the filtered result.

        comparison_parameter (str) - Specific paramter to compare between
        run_ids.

        output_path (str) - Path to send the graphs.

    Returns:
        (null)
    """
    benchmark = dataframe.benchmark.unique()[0]
    my_plots = []
    min_ys = []
    max_ys = []
    for run_id in run_id_list:
        if benchmark == 'messageSendBenchmark':
            # Filtering the dataframe by the core_type given and
            # each run_id in the list of run_is
            plots = dataframe[(dataframe.run_id == '{}'.format(run_id)) &
                              (dataframe.core_type == '{}'.format(core_type))]
            plots = plots.set_index('run_id')
            param_string = str(plots.at[
                run_id, '{}'.format(comparison_parameter)][0])
            plots = plots.reset_index()
            # Filtering the dataframe further so that there are not
            # duplicate 'y-values' to plot; otherwise, there will be
            # spikes in the graphs.
            x_y_map = plots.groupby(
                '{}'.format(x_axis))['{}'.format(y_axis)].min().reset_index()
            min_y = x_y_map['{}'.format(y_axis)].min()
            max_y = x_y_map['{}'.format(y_axis)].max()
            if comparison_parameter == 'build_flags_string':
                plots = (x_y_map.sort_values(
                    '{}'.format(x_axis)).hvplot.scatter(
                        '{}'.format(x_axis),
                        '{}'.format(y_axis),
                        label='run_id: {}, core_type: {}'.format(
                            run_id, core_type),
                        alpha=0.75) * x_y_map.sort_values(
                            '{}'.format(x_axis)).hvplot.line(
                                '{}'.format(x_axis),
                                '{}'.format(y_axis),
                                label='run_id: {}, core_type: {}'.format(
                                    run_id, core_type),
                                line_width=3,
                                alpha=0.75))
            else:
                label = 'run_id: {}, core_type: {}, {}: {}'.format(
                    run_id, core_type, comparison_parameter, param_string)
                plots = (x_y_map.sort_values(
                    '{}'.format(x_axis)).hvplot.scatter(
                        '{}'.format(x_axis),
                        '{}'.format(y_axis),
                        label='run_id: {}, core_type: {}, {}: {}'.format(
                            run_id, core_type,
                            comparison_parameter, param_string),
                        alpha=0.75) * x_y_map.sort_values(
                            '{}'.format(x_axis)).hvplot.line(
                                '{}'.format(x_axis),
                                '{}'.format(y_axis),
                                label=label,
                                line_width=3,
                                alpha=0.75))
            # Appending the plot for each run_id into a list of plots.
            min_ys.append(min_y)
            max_ys.append(max_y)
            my_plots.append(plots)
        else:
            # Filtering the dataframe by the core_type given and
            # each run_id in the list of run_is
            plots = dataframe[(dataframe.run_id == '{}'.format(run_id)) &
                              (dataframe.core_type == '{}'.format(core_type))]
            plots = plots.set_index('run_id')
            param_string = str(plots.at[
                run_id, '{}'.format(comparison_parameter)][0])
            plots = plots.reset_index()
            # Filtering the dataframe further so that there are not
            # duplicate 'y-values' to plot; otherwise, there will be
            # spikes in the graphs.
            x_y_map = plots.groupby(
                '{}'.format(x_axis))['{}'.format(y_axis)].min().reset_index()
            min_y = x_y_map['{}'.format(y_axis)].min()
            max_y = x_y_map['{}'.format(y_axis)].max()
            if comparison_parameter == 'build_flags_string':
                plots = x_y_map.sort_values('{}'.format(x_axis)).hvplot.line(
                    '{}'.format(x_axis),
                    '{}'.format(y_axis),
                    label='run_id: {}, core_type: {}'.format(
                        run_id, core_type),
                    line_width=3,
                    alpha=0.75)
            else:
                plots = x_y_map.sort_values('{}'.format(x_axis)).hvplot.line(
                    '{}'.format(x_axis),
                    '{}'.format(y_axis),
                    label='run_id: {}, core_type: {}, {}: {}'.format(
                        run_id, core_type, comparison_parameter, param_string),
                    line_width=3,
                    alpha=0.75)
            # Appending the plot for each run_id into a list of plots.
            min_ys.append(min_y)
            max_ys.append(max_y)
            my_plots.append(plots)
    y_min = np.min(min_ys)
    # y_max = max_ys[0]
    if benchmark == 'messageSendBenchmark':
        plot = (reduce((lambda x, y: x*y), my_plots)).opts(
            width=625, height=380,
            logx=True, logy=True,
            legend_position='bottom_right', yformatter='%.4f',
            ylim=(y_min*10.0**(-2), None), fontsize={
                'title': 8.5, 'labels': 10, 'legend': 7.5,
                'legend_title': 7.5, 'xticks': 8, 'yticks': 10},
            title='{}: {} vs {}'.format(bm_name, x_axis, y_axis))
    elif benchmark == 'messageLookupBenchmark':
        if list(dataframe.federate_count.unique())[0] == 8.0 or\
            list(dataframe.federate_count.unique())[0] == 64.0:
            plot = (reduce((lambda x, y: x*y), my_plots)).opts(
                width=625, height=380, logx=True,
                logy=True, legend_position='bottom_right',
                ylim=(10**(-6), None), fontsize={
                    'title': 8.5, 'labels': 10, 'legend': 7.5,
                    'legend_title': 7.5, 'xticks': 8, 'yticks': 10},
                title='{}: {} vs {}'.format(bm_name, x_axis, y_axis))
        else:
            plot = (reduce((lambda x, y: x*y), my_plots)).opts(
                width=625, height=380, logx=True,
                logy=True, legend_position='bottom_right',
                ylim=(0.001, None), fontsize={
                    'title': 8.5, 'labels': 10, 'legend': 7.5,
                    'legend_title': 7.5, 'xticks': 8, 'yticks': 10},
                title='{}: {} vs {}'.format(bm_name, x_axis, y_axis))
    else:
        plot = (reduce((lambda x, y: x*y), my_plots)).opts(
            width=625, height=380,
            logx=True, logy=True,
            legend_position='bottom_right', yformatter='%.3f',
            ylim=(0.001, None), fontsize={
                'title': 8.5, 'labels': 10, 'legend': 7.5,
                'legend_title': 7.5, 'xticks': 8, 'yticks': 10},
            title='{}: {} vs {}'.format(bm_name, x_axis, y_axis))
    # The beginning part of the image's name.
    # It includes all the run_ids.
    run_id_str = '_'.join(run_id_list)
    save_path = os.path.join(
        output_path, '{}_{}_{}Core.png'.format(
            run_id_str, bm_name, core_type))
    hvplot.save(plot, save_path)
    logging.info('Created graph file {}'.format(output_path))


def ir_plot(
        dataframe1, dataframe2, x_axis, y_axis,
        bm_name1, bm_name2, metric_bool, metric_type,
        title_part, run_id, core_type, output_path):
    """This function creates a graph that compares different benchmark
    results data for a single run_id and core_type.

    The use of this function is for comparing a single run_id and
    core_type's different benchmark data.  In other words, for a given
    run_id and core_type, this function compares the results from
    two benchmarks, such as 'echoBenchmark' and 'cEchoBenchmark'.

    Args:
        dataframe1 (pandas dataframe) - First dataframe filtered to a
        specific benchmark.

        dataframe2 (pandas dataframe) - Second dataframe filtered to
        another benchmark; the graph will compare both dataframes' data.

        x_axis (str) - x-axis data from the dataframe object that should be
        given to the hvplot.line() function.

        y_axis (str) - y-axis data from the dataframe object that should be
        given to the hvplot.line() function.

        bm_name1 (str) - Specific benchmark's name to be added to the
        title of the graph and name of the saved image.

        bm_name2 (str) - Specific benchmark's name to be added to the
        title of the graph and name of the saved image.

        metric_bool (bool) - If a metric plot is needed (such as counts per
        second), then this is 'True', and it will have a corresponding
        metric_type; otherwise, it will be 'False'.

        metric_type (str) - A type of metric (if it exists) for making
        a metric plot.

        title_part (str) - Part of the title that has specified information
        in it and will be added to the 'title' keyword argument.

        run_id (str) - 5 character unique identifier for the run-ID.

        core_type (str) - Specific core_type to plot.

        output_path (str) - Path to send the graphs.

    Returns:
        (null)
    """
    # Checking to see if a metric is desired.
    if metric_bool is True:
        # Checking what type of metric, if it exists, needs to be
        # created.
        if metric_type == 'seconds_per_count' or metric_type == 'spc':
            # Filtering the dataframes down to the specific run_id and
            # core_type's data
            df1 = dataframe1[(dataframe1.run_id == '{}'.format(run_id)) &
                             (dataframe1.core_type == '{}'.format(core_type))]
            df2 = dataframe2[(dataframe2.run_id == '{}'.format(run_id)) &
                             (dataframe2.core_type == '{}'.format(core_type))]
            # Calculating the metric.
            gpd1 = df1.groupby('{}'.format(x_axis))['{}'.format(y_axis)].sum()\
                / df1.groupby('{}'.format(x_axis))['{}'.format(x_axis)].sum()
            gpd1.name = 'seconds_per_count'
            gpd2 = df2.groupby('{}'.format(x_axis))['{}'.format(y_axis)].sum()\
                / df2.groupby('{}'.format(x_axis))['{}'.format(x_axis)].sum()
            gpd2.name = 'seconds_per_count'
            # Plotting the results from the calculated metric.
            plot1 = gpd1.reset_index().sort_values(
                '{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                'seconds_per_count',
                ylabel='seconds_per_federate_count',
                label='{}, run_id: {}, core_type: {}'.format(
                    bm_name1, run_id, core_type),
                line_width=3,
                alpha=0.75)
            plot2 = gpd2.reset_index().sort_values(
                '{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                'seconds_per_count',
                ylabel='seconds_per_federate_count',
                label='{}, run_id: {}, core_type: {}'.format(
                    bm_name2, run_id, core_type),
                line_width=3,
                alpha=0.75)
            core_type_str = ''.join(core_type)
            save_path = os.path.join(
                output_path, '{}_{}_vs_{}_{}_{}Core.png'.format(
                    run_id, bm_name1, bm_name2, core_type_str, title_part))
        else:
            logging.error('Invalid metric option')
    else:
        # Filtering the dataframes down to the specific run_id and
        # core_type's data.
        df1 = dataframe1[(dataframe1.run_id == '{}'.format(run_id)) &
                         (dataframe1.core_type == '{}'.format(core_type))]
        df2 = dataframe2[(dataframe2.run_id == '{}'.format(run_id)) &
                         (dataframe2.core_type == '{}'.format(core_type))]
        plot1 = df1.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                label='{}, run_id: {}, core_type: {}'.format(
                    bm_name1, run_id, core_type),
                line_width=3,
                alpha=0.75)
        plot2 = df2.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                label='{}, run_id: {}, core_type: {}'.format(
                    bm_name2, run_id, core_type),
                line_width=3,
                alpha=0.75)
        core_type_str = ''.join(core_type)
        save_path = os.path.join(
            output_path, '{}_{}_vs_{}_{}Core.png'.format(
                run_id, bm_name1, bm_name2, core_type_str))
    plots = [plot1, plot2]
    # min_y = plot1['{}'.format(y_axis)].min()
    plot = (reduce((lambda x, y: x*y), plots)).opts(
        width=625, height=380,
        logx=True, logy=True,
        legend_position='bottom_right', yformatter='%.3f',
        ylim=(10.0**(-3), None), fontsize={
            'title': 9, 'labels': 10, 'legend': 9,
            'xticks': 8, 'yticks': 10},
        title='{} v {}: {}'.format(bm_name1, bm_name2, title_part))
    hvplot.save(plot, save_path)
    logging.info('Created graph file {}'.format(output_path))


def mm_plot(
        dataframe, x_axis, y_axis, param1,
        param2, metric_bool, metric_type, bm_name,
        title_part, output_path):
    """This function creates a multi-line graph for multinode benchmark
    results.

    The use of this function is to compare the results of the
    multinode benchmarks.

    Args:
        dataframe (pandas dataframe) - Contains all benchmark results
        and associated metadata.

        x_axis (str) - x-axis data from the dataframe object that should be
        given to the hvplot.line() function.

        y_axis (str) - y-axis data from the dataframe object that should be
        given to the hvplot.line() function.

        param1 (str) - Used to filter dataframe within the .groupby() function.

        param2 (str) - Used to filter dataframe within the .groupby() function.

        metric_bool (bool) - If a metric plot is needed (such as counts per
        second), then this is 'True', and it will have a corresponding
        metric_type; otherwise, it will be 'False'.

        metric_type (str) - A type of metric (if it exists) for making
        a metric plot.

        bm_name (str) - Specific benchmark's name to be added to the
        title of the graph and name of the saved image.

        title_part (str) - Part of the title that has specified information
        in it and will be added to the 'title' keyword argument.

        output_path (str) - Path to send the graphs.

    Returns:
        (null)
    """
    # Checking to see if a metric is desired.
    if metric_bool is True:
        # Chekcing what type of metric, if it exists, needs to be
        # created.
        if metric_type == 'counts_per_second' or metric_type == 'cps':
            # Calculating the metric.
            dataframe['counts_per_second'] = dataframe['EvCount']\
                / dataframe['{}'.format(y_axis)]
            gpd = dataframe.groupby([
                '{}'.format(x_axis),
                '{}'.format(param1)])['counts_per_second'].min()
            gpd = gpd.reset_index()
            # Creating the plot.
            min_y = gpd['counts_per_second'].min()
            plot = gpd.sort_values(
                '{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                'counts_per_second',
                ylabel='EvCounts per second',
                line_width=3,
                by='{}'.format(param1),
                alpha=0.75).opts(
                    width=625, height=450,
                    logx=True, logy=True,
                    legend_position='top', legend_cols=2,
                    yformatter='%.2f',
                    title='{} {}: EvCounts/s vs {}'.format(
                        title_part, bm_name, x_axis),
                    fontsize={'title': 9, 'labels': 10,
                              'legend': 8, 'legend_title': 8,
                              'xticks': 8, 'yticks': 7.5})
            save_path = os.path.join(
                output_path, '{}_{}.png'.format(bm_name, metric_type))
    elif metric_bool is False:
        gpd = dataframe.groupby(
            ['{}'.format(x_axis),
             '{}'.format(param1)])['{}'.format(y_axis)].min()
        gpd = gpd.reset_index()
        # Creating the plot.
        min_y = gpd['{}'.format(y_axis)].min()
        plot = gpd.sort_values('{}'.format(x_axis)).hvplot.line(
                '{}'.format(x_axis),
                '{}'.format(y_axis),
                ylabel='{} (s)'.format(y_axis),
                line_width=3,
                by='{}'.format(param1),
                alpha=0.75).opts(
                    width=625, height=450,
                    logx=True, logy=True,
                    legend_position='top', legend_cols=2,
                    yformatter='%.3f',
                    title='{} {}: {} vs {}'.format(
                        title_part, bm_name, x_axis, y_axis),
                    fontsize={'title': 9, 'labels': 10, 'legend': 8,
                              'legend_title': 8, 'xticks': 8, 'yticks': 7.5})
        save_path = os.path.join(
            output_path, '{}_{}.png'.format(title_part, bm_name))
    else:
        logging.error('Invalid value; should be True or False')
    hvplot.save(plot, save_path)
    logging.info('Created graph file {}'.format(output_path))


# Testing:
# if __name__ == '__main__':
#     import make_dataframe as md
#     json_file = 'bm_results.json'
#     meta_bmk_df = md.make_dataframe1(json_file)
#     timing = meta_bmk_df[(meta_bmk_df.benchmark == 'timingBenchmark') &
#                          (meta_bmk_df.run_id == '7vGM3')]
#     phold = meta_bmk_df[(meta_bmk_df.benchmark == 'pholdBenchmark') &
#                         (meta_bmk_df.run_id == '7vGM3')]
#     msg_1 = meta_bmk_df[(meta_bmk_df.benchmark == 'messageSendBenchmark') &
#                         (meta_bmk_df.message_count == 1) &
#                         (meta_bmk_df.run_id == '7vGM3')]
#     msg_2 = meta_bmk_df[(meta_bmk_df.benchmark == 'messageLookupBenchmark') &
#                         (meta_bmk_df.federate_count == 2) &
#                         (meta_bmk_df.run_id == '7vGM3')]
#     plot1 = sa_plot(
#         phold, 'federate_count', 'real_time', 'pholdBenchmark',
#         True, 'core_type', '7vGM3', os.path.join(os.getcwd()))
#     plot2 = sa_plot(
#         msg_2, 'interface_count', 'real_time', 'messageLookupBenchmark',
#         False, '', '7vGM3', os.path.join(os.getcwd()))
#     plot3 = sa_plot(
#         msg_1, 'message_size', 'real_time', 'messageSendBenchmark',
#         True, 'core_type', '7vGM3', os.path.join(os.getcwd()))
