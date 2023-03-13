import numpy as np
import pandas as pd
from numpy import inf
from pycanon import anonymity
import time
import copy
import efficiency_metrics as em


# GLOBAL VARIABLES
METRICS_TIME = True  # Activate or deactivate the time metrics
METRICS_COST = False  # Activate or deactivate the metrics for characteristics cost
METRICS_MEMORY = False  # Activate or deactivate the memory consumption cost


# Deletes any white spaces from column names
def clear_white_spaces(table):
    old_column_names = table.keys().values.tolist()
    new_column_names = {}

    for i in old_column_names:
        new_column_names[i] = i.strip()

    table = table.rename(columns=new_column_names)
    return table


# Removes all the identifiers in the database
def suppress_identifiers(table, ident):
    for i in ident:
        table[i] = '*'
    return table


# Checks if a string contains numbers
def has_numbers(string):
    return any(i.isdigit() for i in string)


# Converts a string interval to an actual interval type,
# to facilitate the comparison of each data
def string_to_interval(column):
    new_col = []
    for i in column:
        aux = i[0].replace("[", "")
        aux = aux.replace(" ", "")

        if ')' in i[0]:
            aux = aux.replace(")", "")
            aux_2 = aux.split(",")
            new_col.append(pd.Interval(left=float(aux_2[0]),
                                       right=float(aux_2[1]),
                                       closed='left'))
        else:
            aux = aux.replace("]", "")
            aux_2 = aux.split(",")
            new_col.append(pd.Interval(left=float(aux_2[0]),
                                       right=float(aux_2[1]),
                                       closed='both'))

    column = new_col
    return column


# Generalizes a column based on its data type and return a column full of strings with each new
# value for the dataset.
def generalization(column, range_step, hierarchies, current_gen_level, name):
    if name in hierarchies is False and name in range_step is False:
        return column

    elif name in hierarchies:
        aux = hierarchies.get(name)
        new_hierarchy = {}

        for i in range(0, len(aux)):
            if len(aux[i]) > (current_gen_level + 1):
                new_hierarchy[aux[i][current_gen_level]] = aux[i][current_gen_level + 1]

            else:
                return None

        aux = new_hierarchy

    else:
        if len(range_step[name]) > current_gen_level + 1:
            aux = range_step[name][current_gen_level + 1]

        else:
            return None

    # Generalization of numbers
    if (isinstance(column[0][0], int) or isinstance(column[0][0], float) or
            isinstance(column[0][0], complex)):

        min_range = inf
        max_range = 0

        for i in column:
            if i[0] > max_range:
                max_range = i[0]

            if i[0] < min_range:
                min_range = i[0]

        while min_range % aux != 0 or max_range % aux != 0:
            if min_range % aux != 0:
                min_range = min_range - 1

            if max_range % aux != 0:
                max_range = max_range + 1

        step = int((max_range - min_range) / aux)
        ranges = []

        for i in range(0, step):
            if i == (step - 1):
                ranges.append(pd.Interval(left=(min_range + aux * i),
                                          right=(min_range + aux * (i + 1)),
                                          closed='both'))
            else:
                ranges.append(pd.Interval(left=(min_range + aux * i),
                                          right=(min_range + aux * (i + 1)),
                                          closed='left'))

        new_col = []

        for i in range(0, len(column)):
            for j in ranges:
                if column[i][0] in j:
                    new_col.append(str(j))
                    break

        column = new_col

    # Generalization of strings
    elif isinstance(column[0][0], str) and has_numbers(column[0][0]) is False:
        for i in range(0, len(column)):
            column[i] = aux[column[i][0].strip()]

    # Generalization of ranges
    else:
        min_range = inf
        max_range = 0

        column = string_to_interval(column)

        for i in column:
            if i.left > max_range:
                max_range = i.right

            if i.left < min_range:
                min_range = i.left

        while min_range % aux != 0 or max_range % aux != 0:
            if min_range % aux != 0:
                min_range = min_range - 1
            if max_range % aux != 0:
                max_range = max_range + 1

        step = int((max_range - min_range) / aux)
        ranges = []
        for i in range(0, step):
            if i == (step - 1):
                ranges.append(pd.Interval(left=(min_range + aux * i),
                                          right=(min_range + aux * (i + 1)),
                                          closed='both'))
            else:
                ranges.append(pd.Interval(left=(min_range + aux * i),
                                          right=(min_range + aux * (i + 1)),
                                          closed='left'))

        new_col = []
        for i in range(0, len(column)):
            for j in ranges:
                if column[i].left in j:
                    new_col.append(str(j))
                    break

        column = new_col

    return column


# RangeStep should be a dictionary which key is the name of the quasi-identifier and the
#       value is a list of different steps for each of the ranges per level of the identifier.
# Hierarchies should be a dictionary which key is the name of the quasi-identifier and the
#       value is a list of list, which index identifies each level generalizations for said
#       quasi-identifier.
def data_fly(table, ident, qi, k, supp_threshold, range_step={}, hierarchies={}):

    # TODO Metrics
    em.start_monitor_time(METRICS_TIME)
    em.monitor_cost_init("data_fly")
    em.monitor_memory_consumption_start()

    if METRICS_COST:
        num_op = 0
        type = "data_fly"

    table = clear_white_spaces(table)
    table = suppress_identifiers(table, ident)

    current_gen_level = {}
    for i in qi:
        current_gen_level[i] = 0

    k_real = anonymity.k_anonymity(table, qi)
    qi_aux = copy.copy(qi)

    if k_real >= k:
        print(f'The data verifies k-anonymity with k={k_real}')
        return table

    while k_real < k:
        if k_real <= supp_threshold:
            equiv_class = anonymity.utils.aux_anonymity.get_equiv_class(table, qi)
            len_ec = [len(ec) for ec in equiv_class]
            if k > max(len_ec):
                print(f'The anonymization cannot be carried out for the given value k={k} only by suppression')
            else:
                data_ec = pd.DataFrame({'equiv_class': equiv_class, 'k': len_ec})
                data_ec_k = data_ec[data_ec.k < k]
                ec_elim = np.concatenate([anonymity.utils.aux_functions.convert(ec)
                                          for ec in data_ec_k.equiv_class.values])
                table_new = table.drop(ec_elim).reset_index()
                assert (anonymity.k_anonymity(table_new, qi) >= k)

                # TODO Metrics
                em.end_monitor_time(METRICS_TIME)
                em.monitor_cost("data_fly")
                em.monitor_memory_consumption_stop()

                if METRICS_COST:
                    num_op = 0
                    em.monitor_cost(num_op, type)

                return table_new

        # Calculate the attribute with more unique values
        occurrences_qi = [len(np.unique(table[i])) for i in qi_aux]
        name = qi_aux[np.argmax(occurrences_qi)]

        # TODO Metrics
        em.monitor_cost_add("datafly")

        new_ind = generalization(table[[name]].values.tolist(), range_step, hierarchies,
                                 current_gen_level[name], name)

        if new_ind is None:
            qi_aux = copy.copy(qi)
            qi_aux.remove(name)
        else:
            table[name] = new_ind

        k_real = anonymity.k_anonymity(table, qi)
        current_gen_level[name] = current_gen_level[name] + 1

    # TODO Metrics
    em.end_monitor_time(METRICS_TIME)
    em.monitor_cost("datafly")
    em.monitor_memory_consumption_stop()

    return table
