import copy
import typing
import numpy as np
import utils as ut
import pandas as pd
import pycanon.anonymity
from pycanon import anonymity
from pycanon.anonymity import utils


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
                   hierarchies: dict,
                   gen_level: int, name: str
                   ) -> typing.Union[typing.List, np.ndarray, None]:
    """Generalizes a column based on its data type.

    :param column: column from the table under study that needs to be generalized.
    :type column: list of values

    :param hierarchies: hierarchies for generalization of string columns.
    :type hierarchies: dictionary

    :param gen_level: Current level of generalization of each of the columns of the table.
    :type gen_level: int

    :param name: Name of the column that needs to be generalized.
    :type name: string

    :return: List of generalized values.
    :rtype: list of values
    """

    if name in hierarchies is False:
        return column

    else:
        aux = hierarchies[name]

    # Generalization of numbers
    if isinstance(column[0][0], (int, float, complex, np.int64)):

        aux_col = []
        for i in range(0, len(aux)):
            aux_col.append(aux[i][gen_level])

        ranges = ut.string_to_interval(aux_col)
        new_col = []

        for i in range(len(column)):
            for j in ranges:
                if column[i] in j:
                    new_col.append(str(j))
                    break

        column = new_col

    # Generalization of strings
    elif isinstance(column[0], str) and '[' not in column[0]:
        for i in range(len(column)):
            # TODO Aux esta mal, deberia ser la lista con todas las jerarquias de los "marital status"
            for j in range(len(aux)):
                if aux[j][0] == column[i]:
                    column[i] = aux[j][gen_level]
                    break

    # Generalization of ranges
    else:
        column = ut.string_to_interval(column)
        aux_col = []
        for i in range(len(aux)):
            aux_col.append(aux[i][gen_level])

        ranges = ut.string_to_interval(aux_col)

        new_col = []
        for i in range(len(column)):
            for j in ranges:
                if column[i].left in j:
                    new_col.append(str(j))
                    break

        column = new_col

    return column


def generalize(table, node, hierarchies):
    for i in range(len(node)):
        if node[i] != 0:
            name = list(hierarchies.keys())[i]
            table[name] = generalization(table[name], hierarchies, node[i], name)

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
