import copy
import typing
import warnings
import numpy as np
import pandas as pd
import pycanon.anonymity
from pycanon import anonymity
from pycanon.anonymity import utils
import anonymity.metrics.efficiency_metrics as em
import anonymity.metrics.data_utility_metrics as dat_ut
from anonymity.tools.utils_k_anon import utils_k_anonymity as ut


def data_fly(
    table: pd.DataFrame,
    ident: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
    k: int,
    supp_threshold: int,
    hierarchies: dict = {},
) -> pd.DataFrame:
    """Data-fly generalization algorithm for k-anonymity.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param ident: list with the name of the columns of the dataframe.
        that are identifiers.
    :type ident: list of strings

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :param k: desired level of k-anonymity.
    :type k: int

    :param supp_threshold: level of suppression allowed.
    :type supp_threshold: int

    :param hierarchies: hierarchies for generalization of columns.
    :type hierarchies: dictionary

    :return: anonymized table.
    :rtype: pandas dataframe
    """

    em.start_monitor_time()
    em.monitor_cost_init("data_fly")
    em.monitor_memory_consumption_start()
    dat_ut.start_level()

    table = ut.clear_white_spaces(table)
    table = ut.suppress_identifiers(table, ident)

    current_gen_level = {}
    for i in qi:
        current_gen_level[i] = 0
        dat_ut.get_level_generalization(i, current_gen_level[i])

    k_real = anonymity.k_anonymity(table, qi)
    qi_aux = copy.deepcopy(qi)
    # og_table = copy.deepcopy(table)

    if k_real >= k:
        print(f"The data verifies k-anonymity with k={k_real}")
        return table

    while k_real < k:
        if k_real <= supp_threshold:
            equiv_class = anonymity.utils.aux_anonymity.get_equiv_class(table, qi)
            len_ec = [len(ec) for ec in equiv_class]
            if k > max(len_ec):
                print(
                    f"The anonymization cannot be carried out for "
                    f"the given value k={k} only by suppression"
                )
            else:
                data_ec = pd.DataFrame({"equiv_class": equiv_class, "k": len_ec})
                data_ec_k = data_ec[data_ec.k < k]
                ec_elim = np.concatenate(
                    [
                        anonymity.utils.aux_functions.convert(ec)
                        for ec in data_ec_k.equiv_class.values
                    ]
                )
                table_new = table.drop(ec_elim).reset_index()
                assert anonymity.k_anonymity(table_new, qi) >= k

                em.end_monitor_time()
                em.monitor_cost("data_fly")
                em.monitor_memory_consumption_stop()

                return table_new

        # Calculate the attribute with more unique values
        if len(qi_aux) == 0:
            print(
                f"The anonymization cannot be carried out for " f"the given value k={k}"
            )
            return table
        occurrences_qi = [len(np.unique(table[i])) for i in qi_aux]
        name = qi_aux[np.argmax(occurrences_qi)]

        em.monitor_cost_add("datafly")
        new_ind = ut.generalization(
            table[name].values.tolist(), hierarchies, current_gen_level[name] + 1, name
        )

        if new_ind is None:
            if name in qi_aux:
                qi_aux.remove(name)
        else:
            table[name] = new_ind
            current_gen_level[name] = current_gen_level[name] + 1

        k_real = anonymity.k_anonymity(table, qi)
        # print(k_real)
        dat_ut.get_level_generalization(name, current_gen_level[name])
        # print(table)

    em.end_monitor_time()
    em.monitor_cost("datafly")
    em.monitor_memory_consumption_stop()

    return table


def new_level(current_lv, interval, lattice, limits):
    """Takes care of calculating the next level of the lattice.

    :param current_lv: current level of the lattice.
    :type current_lv: int

    :param interval: corresponding to the level of the lattice
    :type ident: interval

    :param lattice: full lattice for incognito
    :type lattice: pandas dataframe

    :param limits: numerical limits for each of the parameters that conform the lattice nodes
    :type lattice: list of ints

    :return: lattice with a new level added
    :rtype: pandas dataframe
    """
    for i, value in enumerate(interval):
        if value < limits[i]:
            new_interval = copy.deepcopy(interval)
            new_interval[i] += 1
            if new_interval not in lattice[current_lv]:
                lattice[current_lv].append(new_interval)
    return lattice


def generate_lattice(hierarchies):
    """Generates a lattice for a given hierarchy to apply incognito.

    :param hierarchies: hierarchy for a given dataset
    :type hierarchies: pandas dataframe

    :return: full lattice ready to apply incognito
    :rtype: pandas dataframe
    """
    ranges_aux = []
    # print(hierarchies)
    keys = hierarchies.keys()
    limits = []

    for i in keys:
        ranges_aux.append(range(len(hierarchies[i][0])))
        limits.append(len(hierarchies[i][0]) - 1)

    current_lv = 0
    lattice = {0: [[0] * len(keys)]}

    while limits not in lattice[current_lv]:
        current_lv += 1
        lattice[current_lv] = []
        for i in lattice[current_lv - 1]:
            lattice = new_level(current_lv, i, lattice, limits)

    return lattice


def generalize(table, node, hierarchies):
    """Generalices a table for a given node of the lattice.

    :param table: table that will be anonymized
    :type table: pandas dataframe

    :param node: singular node of the lattice that contains the level of generalization for each QI
    :type node: list of ints

    :param hierarchies: hierarchies for generalization of columns.
    :type hierarchies: dictionary

    :return: anonymized table.
    :rtype: pandas dataframe
    """
    for i in range(len(node)):
        if node[i] != 0:
            name = list(hierarchies.keys())[i]
            table[name] = ut.generalization(table[name], hierarchies, node[i], name)

    return table


def incognito(
    table: pd.DataFrame,
    ident: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
    k: int,
    supp_threshold: int,
    hierarchies: dict,
) -> pd.DataFrame:
    """Incognito generalization algorithm for k-anonymity.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param ident: list with the name of the columns of the dataframe.
        that are identifiers.
    :type ident: list of strings

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :param k: desired level of k-anonymity.
    :type k: int

    :param supp_threshold: level of suppression allowed.
    :type supp_threshold: int

    :param hierarchies: hierarchies for generalization of columns.
    :type hierarchies: dictionary

    :return: anonymized table.
    :rtype: pandas dataframe
    """
    warnings.simplefilter("ignore", pd.errors.SettingWithCopyWarning)

    lattice = generate_lattice(hierarchies)
    current_lv = 0  # To check if we have traversed all the lvs
    iter_in_lv = 0  # To check if we have traversed the current lv fully
    max_lv = len(lattice.keys())
    max_iter_lv = len(lattice[current_lv])

    table = ut.clear_white_spaces(table)
    table = ut.suppress_identifiers(table, ident)

    possible_nodes = {}
    traversed_nodes = []

    while current_lv < max_lv:
        current_node = lattice[current_lv][iter_in_lv]

        if current_node not in traversed_nodes:
            new_table = generalize(copy.deepcopy(table), current_node, hierarchies)

            if k == pycanon.anonymity.k_anonymity(new_table, qi):
                possible_nodes[dat_ut.discernibility(table, new_table, qi)] = [
                    current_node,
                    False,
                ]

            elif pycanon.anonymity.k_anonymity(new_table, qi) <= supp_threshold:
                equiv_class = anonymity.utils.aux_anonymity.get_equiv_class(table, qi)
                len_ec = [len(ec) for ec in equiv_class]
                if k > max(len_ec):
                    print(
                        f"The anonymization cannot be carried out for "
                        f"the given value k={k} only by suppression"
                    )
                else:
                    data_ec = pd.DataFrame({"equiv_class": equiv_class, "k": len_ec})
                    data_ec_k = data_ec[data_ec.k < k]
                    ec_elim = np.concatenate(
                        [
                            anonymity.utils.aux_functions.convert(ec)
                            for ec in data_ec_k.equiv_class.values
                        ]
                    )
                    new_table = table.drop(ec_elim).reset_index()
                    assert anonymity.k_anonymity(new_table, qi) >= k

                    possible_nodes[dat_ut.discernibility(table, new_table, qi)] = [
                        current_node,
                        True,
                    ]

        traversed_nodes.append(current_node)

        # Reset trackers for the new level
        iter_in_lv = iter_in_lv + 1
        if iter_in_lv >= max_iter_lv:
            iter_in_lv = 0
            current_lv = current_lv + 1
            if current_lv < max_lv:
                max_iter_lv = len(lattice[current_lv])

    metric = np.inf
    node = {}
    for i in possible_nodes.keys():
        if i < metric:
            metric = i
            node = possible_nodes[i]

    if len(node):
        if node[1] is True:
            equiv_class = anonymity.utils.aux_anonymity.get_equiv_class(
                generalize(table, node[0], hierarchies), qi
            )
            len_ec = [len(ec) for ec in equiv_class]
            data_ec = pd.DataFrame({"equiv_class": equiv_class, "k": len_ec})
            data_ec_k = data_ec[data_ec.k < k]
            ec_elim = np.concatenate(
                [
                    anonymity.utils.aux_functions.convert(ec)
                    for ec in data_ec_k.equiv_class.values
                ]
            )
            return table.drop(ec_elim).reset_index()
    else:
        print(f"Unnable to achieve k={k}")
        return table

    return generalize(table, node[0], hierarchies)


def k_anonymity(
    table: pd.DataFrame,
    ident: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
    k: int,
    supp_threshold: int,
    hierarchies: dict,
    method: str,
) -> pd.DataFrame:
    """Generalization algorithm for k-anonymity. Applies data-fly for default in case we don't specify correctly.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param ident: list with the name of the columns of the dataframe.
        that are identifiers.
    :type ident: list of strings

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :param k: desired level of k-anonymity.
    :type k: int

    :param supp_threshold: level of suppression allowed.
    :type supp_threshold: int

    :param hierarchies: hierarchies for generalization of columns.
    :type hierarchies: dictionary

    :param method: name of the anonymization method that we want to use.
    :type method: string

    :return: anonymized table.
    :rtype: pandas dataframe
    """

    if method.lower() == "incognito":
        return incognito(table, ident, qi, k, supp_threshold, hierarchies)
    elif method.lower() == "datafly" or method.lower() == "data fly":
        return data_fly(table, ident, qi, k, supp_threshold, hierarchies)
    else:
        raise ValueError("Unimplemented k-anonymity method.")
