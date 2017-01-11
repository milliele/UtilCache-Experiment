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
from icarus.registry import RESULTS_READER, RESULTS_WRITER


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

def run(config, results):
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
    desc = {'strategy':{'name':'MUS'}}
    RESULTS_WRITER['PICKLE'](resultset.refilter(desc), 'new.txt')

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("-r", "--results", dest="results",
                        help='the results file',
                        required=True)
    parser.add_argument("-o", "--output", dest="output",
                        help='the output will be saved',
                        required=True)
    parser.add_argument("config",
                        help="the configuration file")
    args = parser.parse_args()
    run(args.config, args.results)


if __name__ == '__main__':
    main()

