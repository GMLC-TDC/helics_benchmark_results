# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 19:03:59 2019

@author: barn553
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import make_dataframe as md

json_file = 'bm_results.json'
meta_bmk_df = md.make_dataframe(json_file)
#print(meta_bmk_df.shape)

#meta_bmk_df = meta_bmk_df.sort_values('real_time')
#print(meta_bmk_df.head())

#plt.scatter(meta_bmk_df.federate_count, 
#            meta_bmk_df.real_time, 
#            s=100,
#            alpha=0.3)
#plt.title('federate_count vs real_time')
#plt.xlabel('federate_count')
#plt.ylabel('real_time (ns)')

#plt.show()
def plot_echoMessage():
    """This function plots the bar graph for the echoMessage
    benckmark.
    """
    echo_df = meta_bmk_df[ meta_bmk_df.benchmark == 'echoMessageBenchmark']
    echo_df.sort_values('core_type')
    x_range = range(len(echo_df.core_type.unique()))
    print(x_range)
#    labels = [echo_df.core_type.unique()]
#    print(labels)
    plt.bar(range(0, 8), 
            echo_df.real_time, 
            width=5,
            alpha=0.3)
#    plt.xticks(x_range, labels)
#    plt.xlabel('core_type')
    plt.ylabel('real_time (ns)')
    plt.title('echoMessage: core_type vs real_time')
    plt.show()

def plot_messageLookup():
    """This function plot the bar graph (??) for the messageLookup
    Benchmark.
    """
    msg_lkp_df = meta_bmk_df[ meta_bmk_df.benchmark == 'messageLookupBenchmark']
    core_df = msg_lkp_df[ msg_lkp_df.core_type == 'inproc']
    
    plt.bar(core_df.federate_count, 
            core_df.real_time, 
            width=5,
            alpha=0.3)
    plt.xlabel('federate_count')
    plt.ylabel('real_time (ns)')
    plt.title('messageLookup: federate_count vs real_time')
    plt.show()
    
def plot_messageSend():
    """This funtion plots the graph for the messageSend 
    Benchmark.
    """
    msg_lkp_df = meta_bmk_df[ meta_bmk_df.benchmark == 'messageLookupBenchmark']
    core_df = msg_lkp_df[ msg_lkp_df.core_type == 'singleFed']
    
    plt.plot(core_df.message_size, 
             core_df.real_time, 
             alpha=0.5)
    plt.xlabel('message_size')
    plt.ylabel('real_time (ns)')
    plt.title('messageLookup: federate_count vs real_time')
    plt.show()

def main():
    """The main function that runs this script."""
    
    fig, (sub1, sub2) = plt.subplots(1, 2)
    fig.suptitle('benchmark plots')
    sub1 = plot_messageLookup()
    sub2 = plot_messageSend()
main()