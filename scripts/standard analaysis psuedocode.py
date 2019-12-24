#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 9:15:39 2019

Psuedo-code to show how I think the code should be structured to support the 
standard analysis and report-generation

@author: hard312
"""
import stuff


def main:
    # User provides a path with one or more directories that contain one or 
    #   more results files
    user_input_path = get_user_input_defining_location_of_results_files_to_process

    # Do a tiny bit of pre-processing to figure generate a list of paths from
    #   the user-provided path 
    path_list = find_paths_for_all_individual_benchmark_runs(user_input_path)

    for results_path in path_list:
        # Run Trevor's pre-processing code that will generate a JSON string
        #   for all the benchmark results in the specified file.
        #  
        # For the standard analysis this will be data from one benchmark run.
        json_results = benchmark_postprocessing(results_path)
        
        # Generate the graphs and save them as a files in a "report" folder
        #   alongside the benchmark results. The location of the saved files will
        #   be fixed (relative to the passed-in path) so this function doesn't
        #   need to return anything.
        generate_results_graph_images(json_results)
        
        # For each run (which now has a set of graphs available), generate a
        #   report that includes metadata for the run at the top of the report
        #   as well as all the graph images. The resulting PDF is the standard
        #   analysis report.
        #
        # The results path is used to define the location of the graph images
        #   and the json_results contains the metadata needed for the header
        #   of the report
        generate_standard_analysis_PDF_report(results_path, json_results)
        
        