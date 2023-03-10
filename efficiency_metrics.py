import time

import numpy as np
import pandas as pd
from numpy import inf
from pycanon import anonymity
import copy

# Global variables for metrics
START_TIME = None
END_TIME = None


# Metrics to monitor the execution time of the functions
def monitor_time():
    if START_TIME is not None and END_TIME is not None:
        print("\nTotal execution time: ", END_TIME - START_TIME)
    else:
        print("\nTimes have not been collected")


def start_monitor_time(metrics_on):
    if metrics_on is True:
        global START_TIME
        START_TIME = time.time()


def end_monitor_time(metrics_on):
    if metrics_on is True:
        global END_TIME
        END_TIME = time.time()
        monitor_time()


# Metrics to monitor the execution time of the functions
def monitor_cost(num_op, type):

    return None


def monitor_memory_consumption():

    return None
