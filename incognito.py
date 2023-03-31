import typing
import copy
import numpy as np
import pandas as pd
import pycanon.anonymity
from pycanon import anonymity


def new_level(current_lv, interval, lattice, limits):
    for i, value in enumerate(interval):
        if value < limits[i]:
            new_interval = copy.deepcopy(interval)
            new_interval[i] = new_interval[i] + 1
            if new_interval not in lattice[current_lv + 1]:
                lattice[current_lv + 1].append(new_interval)
    return lattice


def generate_lattice(hierarchies):
    ranges_aux = []
    keys = hierarchies.keys()
    limits = []

    for i in keys:
        ranges_aux.append(range(len(hierarchies[i][0])))
        limits.append(len(hierarchies[i][0]))

    current_lv = 0
    lattice = {0: [[0] * len(keys)]}

    while limits not in lattice[current_lv]:
        lattice[current_lv + 1] = []
        for i in lattice[current_lv]:
            lattice = new_level(current_lv, i, lattice, limits)
        current_lv = current_lv + 1

    return lattice


def generalization(column: typing.Union[typing.List, np.ndarray],
                   range_step: dict,
                   hierarchies: dict,
                   current_gen_level: int,
                   name: str) -> typing.Union[typing.List, np.ndarray, None]:
    """Generalizes a column based on its data type.

    :param column: column from the table under study that needs to be generalized.
    :type column: list of values

    :param range_step: steps for the intervals of numeric columns.
    :type range_step: dictionary

    :param hierarchies: hierarchies for generalization of string columns.
    :type hierarchies: dictionary

    :param current_gen_level: Current level of generalization of each of the columns of the table.
    :type current_gen_level: int

    :param name: Name of the column that needs to be generalized.
    :type name: string

    :return: List of generalized values.
    :rtype: list of values
    """

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
    if isinstance(column[0][0], (int, float, complex)):

        min_range = np.inf
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
            ranges.append(pd.Interval(left=(min_range + aux * i),
                                      right=(min_range + aux * (i + 1)),
                                      closed='left'))

        new_col = []

        for i in range(len(column)):
            for j in ranges:
                if column[i][0] in j:
                    new_col.append(str(j))
                    break

        column = new_col

    # Generalization of strings
    elif isinstance(column[0][0], str) and '[' not in column[0][0]:
        for i in range(0, len(column)):
            column[i] = aux[column[i][0].strip()]

    # Generalization of ranges
    else:
        min_range = np.inf
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


def generalize(table, node, hierarchies):
    for i in range(len(node)):
        table[hierarchies.keys()[i]] = generalization(table[hierarchies.keys()[i]], node[i])

    return table


def incognito(table, hierarchies, k, qi, supp_threshold):
    lattice = generate_lattice(hierarchies)
    current_lv = 0  # To check if we have traversed all the lvs
    iter_in_lv = 0  # To check if we have traversed the current lv fully
    max_lv = len(lattice.keys())
    max_iter_lv = len(lattice[current_lv])

    possible_nodes = []

    while current_lv < max_lv:
        current_node = lattice[current_lv][iter_in_lv]
        print(current_node)
        if current_node not in possible_nodes:
            # TODO Implementar la función generalize
            new_table = generalize(table, current_node, hierarchies)

            if k == pycanon.anonymity.k_anonymity(new_table, qi):
                # TODO Temporalmente devuelve el primer nodo que encuentra, pero en verdad debe guardar el nodo y todos
                #  los que se han formado a partir de él en la lista de candidatos a solución. Debere introducir un if
                #  que compruebe si el nodo que vamos a mirar a continuación ya estas en la lista de soluciones que lo
                #  pase.
                return new_table
            elif pycanon.anonymity.k_anonymity(new_table, qi) <= supp_threshold:
                equiv_class = anonymity.utils.aux_anonymity.get_equiv_class(table, qi)
                len_ec = [len(ec) for ec in equiv_class]
                if k > max(len_ec):
                    print(f'The anonymization cannot be carried out for the given value k={k} only by suppression')
                else:
                    data_ec = pd.DataFrame({'equiv_class': equiv_class, 'k': len_ec})
                    data_ec_k = data_ec[data_ec.k < k]
                    ec_elim = np.concatenate([anonymity.utils.aux_functions.convert(ec)
                                              for ec in data_ec_k.equiv_class.values])
                    new_table = table.drop(ec_elim).reset_index()
                    assert (anonymity.k_anonymity(new_table, qi) >= k)
                    # TODO Temporalmente devuelve el primer nodo que encuentra, pero en verdad debe guardar el nodo y
                    #  todos los que se han formado a partir de él en la lista de candidatos a solución. Debere
                    #  introducir un if que compruebe si el nodo que vamos a mirar a continuación ya estas en la lista
                    #  de soluciones que lo pase.
                    return new_table

        # Reset trackers for the new level
        iter_in_lv = iter_in_lv + 1
        if iter_in_lv >= max_iter_lv:
            iter_in_lv = 0
            current_lv = current_lv + 1
            if current_lv < max_lv:
                max_iter_lv = len(lattice[current_lv])

    return max_lv


def string_to_interval(
        column: typing.Union[typing.List, np.ndarray]
) -> typing.Union[typing.List, np.ndarray]:
    """Converts a string interval to an actual interval type,
    to facilitate the comparison of each data.

    :param column: List of intervals as strings.
    :type column: list of strings

    :return: List containing the intervals converted to the proper data type.
    :rtype: list of intervals
    """

    new_col = []
    for i in column:
        aux = i.replace("[", "")
        aux = aux.replace(" ", "")

        if ')' in i:
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


def create_ranges(table, range_step):
    new_hie = {}
    for i in range_step.keys():
        new_hie[i] = []
        for j in range(1, len(range_step[i])):
            aux = range_step[i][j]
            # Generalization of numbers
            if isinstance(table[i][0], (int, np.int64, float, complex)):

                min_range = np.inf
                max_range = 0

                for k in set(table[i]):
                    new_hie[i].append([k])

                for k in table[i]:
                    if k > max_range:
                        max_range = k

                    if k < min_range:
                        min_range = k

                while min_range % aux != 0 or max_range % aux != 0:
                    if min_range % aux != 0:
                        min_range = min_range - 1

                    if max_range % aux != 0:
                        max_range = max_range + 1

                step = int((max_range - min_range) / aux)
                ranges = []

                for k in range(0, step):
                    ranges.append(pd.Interval(left=(min_range + aux * k),
                                              right=(min_range + aux * (k + 1)),
                                              closed='left'))

                new_col = []

                # TODO Arreglar aqui lo de añadir a los subarrays de la lista el anterior
                for m in range(len(new_hie[i])):
                    for n in ranges:
                        if new_hie[i][m][0] in n:
                            new_hie[i][m].append(str(n))
                            break

                for m in range(len(table[i])):
                    for n in ranges:
                        if table[i][m] in n:
                            new_col.append(str(n))
                            break

                table[i] = new_col

            # Generalization of ranges
            else:
                min_range = np.inf
                max_range = 0
                column = string_to_interval(table[i])

                for m in column:
                    if m.left > max_range:
                        max_range = m.right

                    if m.left < min_range:
                        min_range = m.left

                while min_range % aux != 0 or max_range % aux != 0:
                    if min_range % aux != 0:
                        min_range = min_range - 1
                    if max_range % aux != 0:
                        max_range = max_range + 1

                step = int((max_range - min_range) / aux)
                ranges = []
                for m in range(0, step):
                    ranges.append(pd.Interval(left=(min_range + aux * m),
                                              right=(min_range + aux * (m + 1)),
                                              closed='left'))

                for m in range(0, len(new_hie[i])):
                    for n in ranges:
                        if new_hie[i][m][0] in n:
                            new_hie[i][m].append(str(n))
                            break

                new_col = []
                for m in range(len(column)):
                    for n in ranges:
                        if column[m].left in n:
                            new_col.append(str(n))
                            break

                table[i] = new_col

        return new_hie
