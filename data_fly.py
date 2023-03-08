import numpy as np
import pandas as pd
from numpy import inf
from pycanon import anonymity
import copy


# Deletes any white spaces from column names
def clear_white_spaces(table):
    old_column_names = table.keys().values.tolist()
    new_column_names = {}

    for i in old_column_names:
        new_column_names[i] = i.strip()

    table = table.rename(columns=new_column_names)

    return table


# Adds * to all columns that are not QI or SA
def clear_data(table, qi, sa):
    aux = []
    for j in range(0, len(table[table.keys().values.tolist()[0]])):
        aux.append('*')

    for i in table.keys().values.tolist():
        if i not in qi and i not in sa:
            table[i] = aux

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
def data_fly(table, qi, sa, k, supp_threshold, range_step={}, hierarchies={}):
    table = clear_white_spaces(table)
    table = clear_data(table, qi, sa)

    current_gen_level = {}
    for i in table.keys().values.tolist():
        current_gen_level[i] = 0

    freq_cs = anonymity.k_anonymity(table, qi)
    qi_aux = copy.copy(qi)
    qi_aux = np.concatenate((qi_aux, sa))

    while freq_cs < k:

        if freq_cs <= supp_threshold:
            # Suppress tables
            cs = anonymity.utils.aux_anonymity.get_equiv_class(table, qi)

            for i in cs:
                if len(i) <= supp_threshold:
                    table = table.drop(i, axis=0)

            return table

        else:
            number_of_occurrences = 0
            name = " "

            # Calculate the attribute with more unique values
            for i in qi_aux:
                if number_of_occurrences < len(np.unique(table[i])):
                    name = i
                    number_of_occurrences = len(np.unique(table[i]))

            new_ind = generalization(table[[name]].values.tolist(), range_step, hierarchies,
                                     current_gen_level[name], name)
            print(name)
            if new_ind is None:
                qi_aux = qi_aux[qi_aux != name]
            else:
                table[name] = new_ind

        freq_cs = anonymity.k_anonymity(table, qi)
        current_gen_level[name] = current_gen_level[name] + 1

    return table
