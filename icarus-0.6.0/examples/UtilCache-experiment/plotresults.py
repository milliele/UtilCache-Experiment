#!/usr/bin/env python
"""Plot results read from a result set
"""
from __future__ import division
import os
import argparse
import collections
import logging
import copy
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from icarus.util import Settings, Tree, config_logging, step_cdf
from icarus.tools import means_confidence_interval
from icarus.results import plot_axis_lines, plot_axis_bar_chart
from icarus.registry import RESULTS_READER


# Logger object
logger = logging.getLogger('plot')

# These lines prevent insertion of Type 3 fonts in figures
# Publishers don't want them
plt.rcParams['ps.useafm'] = True
plt.rcParams['pdf.use14corefonts'] = True

# If True text is interpreted as LaTeX, e.g. underscore are interpreted as
# subscript. If False, text is interpreted literally
plt.rcParams['text.usetex'] = False

# Aspect ratio of the output figures
plt.rcParams['figure.figsize'] = 8, 5

# Size of font in legends
LEGEND_SIZE = 14

# Line width in pixels
LINE_WIDTH = 1.5

# Plot
PLOT_EMPTY_GRAPHS = True

# This dict maps strategy names to the style of the line to be used in the plots
# Regional strategies: solid lines
# On-path strategies: dashed lines
# individual-cache: dotted line
STRATEGY_STYLE = {
         'HR_SYMM':         'b-o',
         'LCE':             'b:p',
         'PROB_CACHE':      'g--D',
         'POP_CACHE':       'c--s',
         'MUS':             'r--^'
}

# This dict maps name of strategies to names to be displayed in the legend
STRATEGY_LEGEND = {
         'LCE':             'LCE',
         'HR_SYMM':         'HR Symm',
         'PROB_CACHE':      'ProbCache',
         'POP_CACHE':        'PopCache',
         'MUS':         'UtilCache'
                    }

# Color and hatch styles for bar charts of cache hit ratio and link load vs topology
TOPOLOGY_BAR_COLOR = {
    'GEANT':          'k',
    'WIDE':          '0.4',
    'GARR':          '0.5',
    'TISCALI':       '0.6'
    }

TOPOLOGY_BAR_HATCH = {
    'GEANT':          None,
    'WIDE':          '//',
    'GARR':     'x',
    'TISCALI':     '+'
    }

TOPOLOGY_LEGEND = {
         'GEANT':          'GEANT',
    'WIDE':          'WIDE',
    'GARR':          'GARR',
    'TISCALI':       'TISCALI'
                    }

def draw_groups_of_interval(resultset, topologies, alpha, cache_size, strategy, interval_range, plotdir):
    plt.rcParams['figure.figsize'] = 8, 2.5
    # Size of font in legends
    LEGEND_SIZE = 10

    # Line width in pixels
    LINE_WIDTH = 1
    myfig = plt.figure()
    plt.subplot(121)
    desc = {}
    desc['title'] = '(a) Cache hit ratio'
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'Update interval'
    desc['xparam'] = ('workload', 'update_internal')
    desc['xvals'] = interval_range
    desc['filter'] = {'workload': {'alpha': alpha},
                      'cache_placement': {'network_cache': cache_size},
                      'strategy': {'name': strategy}}
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN')] * len(topologies)
    desc['ycondnames'] = [('topology', 'name')] * len(topologies)
    desc['ycondvals'] = topologies
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper left'
    desc['bar_color'] = TOPOLOGY_BAR_COLOR
    desc['bar_hatch'] = TOPOLOGY_BAR_HATCH
    desc['legend'] = TOPOLOGY_LEGEND
    desc['legend_args'] = {'mode': 'expand',
                           'ncol': len(topologies),
                           'bbox_to_anchor': (0., 1.02, 2.2, .3)}
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    plot_axis_bar_chart(resultset, desc)
    if 'legend' in desc:
        legend = [desc['legend'][l] for l in topologies]
        legend_args = desc['legend_args'] if 'legend_args' in desc else {}
        if 'legend_loc' in desc:
            legend_args['loc'] = desc['legend_loc']
        plt.legend(legend, prop={'size': LEGEND_SIZE}, **legend_args)
    plt.subplot(122)
    desc['title'] = '(b) Latency'
    desc['ylabel'] = 'Latency'
    desc['ymetrics'] = [('LATENCY', 'MEAN')] * len(topologies)
    plot_axis_bar_chart(resultset, desc)
    myfig.savefig(os.path.join(plotdir, 'VS_INTERVAL_A=%s@C=%s.png' % (alpha, cache_size)), bbox_inches='tight')
    plt.close(myfig)

def draw_groups_of_alpha(resultset, topologies, alpha_range, cache_size, strategies, interval, plotdir):
    plt.rcParams['figure.figsize'] = 21, 10
    # Size of font in legends
    LEGEND_SIZE = 15

    # Line width in pixels
    LINE_WIDTH = 2
    myfig = plt.figure()
    count = 0
    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'Zipf Exponent: Alpha'
    desc['xparam'] = ('workload', 'alpha')
    desc['xvals'] = alpha_range
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN')] * len(strategies)
    desc['ycondnames'] = [('strategy', 'name')] * len(strategies)
    desc['ycondvals'] = strategies
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper left'
    desc['line_style'] = STRATEGY_STYLE
    desc['legend'] = STRATEGY_LEGEND
    desc['legend_args'] = {'mode': 'expand',
                           'ncol': len(strategies),
                           'bbox_to_anchor': (0., 1.02, 4.5, .2)}
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    for topology in topologies:
        desc['title'] = '(%s) Cache hit ratio: T=%s@C=%s' % (chr(ord('a')+count), topology, cache_size)
        desc['filter'] = {'topology': {'name': topology},
                          'cache_placement': {'network_cache': cache_size}}
        plt.subplot(2, len(topologies), count + 1)
        plot_axis_lines(resultset, desc)
        if count == 0:
            if 'legend' in desc:
                legend = [desc['legend'][l] for l in strategies]
                legend_args = desc['legend_args'] if 'legend_args' in desc else {}
                if 'legend_loc' in desc:
                    legend_args['loc'] = desc['legend_loc']
                plt.legend(legend, prop={'size': LEGEND_SIZE}, **legend_args)
        count += 1
    desc['ylabel'] = 'Latency'
    desc['ymetrics'] = [('LATENCY', 'MEAN')] * len(strategies)
    for topology in topologies:
        desc['title'] = '(%s) Latency: T=%s@C=%s' % (chr(ord('a')+count), topology, cache_size)
        desc['filter'] = {'topology': {'name': topology},
                          'cache_placement': {'network_cache': cache_size}}
        plt.subplot(2, len(topologies), count + 1)
        plot_axis_lines(resultset, desc)
        if count == 0:
            if 'legend' in desc:
                legend = [desc['legend'][l] for l in strategies]
                legend_args = desc['legend_args'] if 'legend_args' in desc else {}
                if 'legend_loc' in desc:
                    legend_args['loc'] = desc['legend_loc']
                plt.legend(legend, prop={'size': LEGEND_SIZE}, **legend_args)
        count += 1
    myfig.savefig(os.path.join(plotdir, 'VS_ALPHA_C=%s.png' % (cache_size)), bbox_inches='tight')
    plt.close(myfig)

def draw_groups_of_cache_size(resultset, topologies, alpha, cache_size_range, strategies, interval, plotdir):
    plt.rcParams['figure.figsize'] = 21, 10
    # Size of font in legends
    LEGEND_SIZE = 15

    # Line width in pixels
    LINE_WIDTH = 2
    myfig = plt.figure()
    count = 0
    desc = {}
    desc['ylabel'] = 'Cache hit ratio'
    desc['xlabel'] = 'Cache to population ratio'
    desc['xparam'] = ('cache_placement', 'network_cache')
    desc['xvals'] = cache_size_range
    desc['ymetrics'] = [('CACHE_HIT_RATIO', 'MEAN')] * len(strategies)
    desc['ycondnames'] = [('strategy', 'name')] * len(strategies)
    desc['ycondvals'] = strategies
    desc['errorbar'] = True
    desc['legend_loc'] = 'upper left'
    desc['line_style'] = STRATEGY_STYLE
    desc['legend'] = STRATEGY_LEGEND
    desc['legend_args'] = {'mode': 'expand',
                           'ncol': len(strategies),
                           'bbox_to_anchor': (0., 1.02, 4.5, .2)}
    desc['plotempty'] = PLOT_EMPTY_GRAPHS
    for topology in topologies:
        desc['title'] = '(%s) Cache hit ratio: T=%s@A=%s' % (chr(ord('a')+count), topology, alpha)
        desc['filter'] = {'topology': {'name': topology},
                          'workload': {'alpha': alpha}}
        plt.subplot(2, len(topologies), count + 1)
        plot_axis_lines(resultset, desc)
        if count == 0:
            if 'legend' in desc:
                legend = [desc['legend'][l] for l in strategies]
                legend_args = desc['legend_args'] if 'legend_args' in desc else {}
                if 'legend_loc' in desc:
                    legend_args['loc'] = desc['legend_loc']
                plt.legend(legend, prop={'size': LEGEND_SIZE}, **legend_args)
        count += 1
    desc['ylabel'] = 'Latency'
    desc['ymetrics'] = [('LATENCY', 'MEAN')] * len(strategies)
    for topology in topologies:
        desc['title'] = '(%s) Latency: T=%s@A=%s' % (chr(ord('a')+count), topology, alpha)
        desc['filter'] = {'topology': {'name': topology},
                          'workload': {'alpha': alpha}}
        plt.subplot(2, len(topologies), count + 1)
        plot_axis_lines(resultset, desc)
        if count == 0:
            if 'legend' in desc:
                legend = [desc['legend'][l] for l in strategies]
                legend_args = desc['legend_args'] if 'legend_args' in desc else {}
                if 'legend_loc' in desc:
                    legend_args['loc'] = desc['legend_loc']
                plt.legend(legend, prop={'size': LEGEND_SIZE}, **legend_args)
        count += 1
    myfig.savefig(os.path.join(plotdir, 'VS_CACHE_SIZE_A=%s.png' % (alpha)), bbox_inches='tight')
    plt.close(myfig)

def run(config, results, plotdir):
    """Run the plot script

    Parameters
    ----------
    config : str
        The path of the configuration file
    results : str
        The file storing the experiment results
    plotdir : str
        The directory into which graphs will be saved
    """
    settings = Settings()
    settings.read_from(config)
    config_logging(settings.LOG_LEVEL)
    resultset = RESULTS_READER[settings.RESULTS_FORMAT](results)
    # Create dir if not existsing
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
    # Parse params from settings
    topologies = settings.TOPOLOGIES
    cache_sizes = settings.NETWORK_CACHE
    alphas = settings.ALPHA
    intervals = settings.UPDATE_INTERNAL
    strategies = settings.STRATEGIES

    logger.info(
        'Plotting cache hit ratio for cache size: %s, alpha:%s vs internal' % (str(cache_sizes[2]), str(alphas[2])))
    draw_groups_of_interval(resultset, topologies, alphas[2], cache_sizes[2], 'MUS', intervals, plotdir)
    logger.info(
        'Plotting performance for cache size: %s vs alpha' % (str(cache_sizes[2])))
    draw_groups_of_alpha(resultset, topologies, alphas, cache_sizes[2], strategies, intervals[2], plotdir)
    logger.info(
        'Plotting performance for alpha: %s vs cache size' % (str(alphas[2])))
    draw_groups_of_cache_size(resultset, topologies, alphas[2], cache_sizes, strategies, intervals[2], plotdir)
    logger.info('Exit. Plots were saved in directory %s' % os.path.abspath(plotdir))

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("-r", "--results", dest="results",
                        help='the results file',
                        required=True)
    parser.add_argument("-o", "--output", dest="output",
                        help='the output directory where plots will be saved',
                        required=True)
    parser.add_argument("config",
                        help="the configuration file")
    args = parser.parse_args()
    run(args.config, args.results, args.output)


if __name__ == '__main__':
    main()

