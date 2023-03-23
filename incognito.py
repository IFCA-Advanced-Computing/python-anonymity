import numpy as np
import pandas as pd
from numpy import inf
from pycanon import anonymity
import copy
import itertools


def generate_lattice_wrong(hierarchies):
    ranges = []
    for i in hierarchies.keys():
        ranges.append(range(0, len(hierarchies[i][0])))
    return list(itertools.product(*ranges))


def new_level(current_lv, interval, lattice, limits):
    for i in range(0, len(interval)):
        if interval[i] < limits[i]:
            new_interval = copy.deepcopy(interval)
            new_interval[i] = new_interval[i] + 1
            if new_interval not in  lattice[current_lv + 1]:
                lattice[current_lv + 1].append(new_interval)
    return lattice


def generate_lattice(hierarchies):
    ranges_aux = []
    keys = hierarchies.keys()
    limits = []

    for i in keys:
        ranges_aux.append(range(0, len(hierarchies[i][0])))
        limits.append(len(hierarchies[i][0]))

    current_lv = 0
    lattice = {0:[[0]*len(keys)]}

    while limits not in lattice[current_lv]:
        lattice[current_lv + 1] = []
        for i in lattice[current_lv]:
            lattice = new_level(current_lv, i, lattice, limits)
        current_lv = current_lv + 1

    return lattice

