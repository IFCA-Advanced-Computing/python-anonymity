import time
import tracemalloc as tr

import numpy as np
import pandas as pd
from numpy import inf
from pycanon import anonymity
import copy

# Global variables for metrics
START_TIME = None
END_TIME = None
NUM_DATAFLY = 0
NUM_INCOGNITO = 0
NUM_MONDRIAN = 0


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
def monitor_cost(type):
    if type.lower() == "data_fly" or type.lower() == "datafly":
        global NUM_DATAFLY
        print("Number of generalization operations: ", NUM_DATAFLY)
    if type.lower() == "incognito":
        global NUM_INCOGNITO
        print(NUM_INCOGNITO)
    if type.lower() == "mondrian":
        global NUM_MONDRIAN
        print(NUM_MONDRIAN)


def monitor_cost_init(type):
    if type.lower() == "data_fly" or type.lower() == "datafly":
        global NUM_DATAFLY
        NUM_DATAFLY = 0
    if type.lower() == "incognito":
        global NUM_INCOGNITO
        NUM_INCOGNITO = 0
    if type.lower() == "mondrian":
        global NUM_MONDRIAN
        NUM_MONDRIAN = 0


def monitor_cost_add(type):
    if type.lower() == "data_fly" or type.lower() == "datafly":
        global NUM_DATAFLY
        NUM_DATAFLY = NUM_DATAFLY + 1
    if type.lower() == "incognito":
        global NUM_INCOGNITO
        NUM_INCOGNITO = NUM_INCOGNITO + 1
    if type.lower() == "mondrian":
        global NUM_MONDRIAN
        NUM_MONDRIAN = NUM_MONDRIAN + 1


def monitor_memory_consumption_start():
    tr.start()


def monitor_memory_consumption_stop():
    memory = tr.get_traced_memory()
    print("Peak memory use: ", memory[1])
    tr.stop()


# TODO NOT WORKING AT ALL, PLS DO NOT TRY TO USE IT YET
def number_of_missing_values(original_table, modifed_table, U, L):
    n = len(original_table.keys().values.tolist())
    t = len(original_table[0])

    a = 1/(t*n)

    for i in range(0, n):
        for j in range(0, t):
            b = U[i, j] - L[i, j]
            c = U[i, ] - L[i, ]
            d = d + (b/c)

    return a * d

