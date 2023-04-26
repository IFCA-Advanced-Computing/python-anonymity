import copy
import typing
import utils as ut
import numpy as np
import pandas as pd
from pycanon import anonymity
import efficiency_metrics as em
import data_utility_metrics as dum


def data_fly(table: pd.DataFrame,
             ident: typing.Union[typing.List, np.ndarray],
             qi: typing.Union[typing.List, np.ndarray],
             k: int,
             supp_threshold: int,
             hierarchies: dict = {}) -> pd.DataFrame:
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

    # TODO Metrics
    em.start_monitor_time()
    em.monitor_cost_init("data_fly")
    em.monitor_memory_consumption_start()
    dum.start_level()

    table = ut.clear_white_spaces(table)
    table = ut.suppress_identifiers(table, ident)

    current_gen_level = {}
    for i in qi:
        current_gen_level[i] = 0
        dum.get_level_generalization(i, current_gen_level[i])

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
                print(f'The anonymization cannot be carried out for '
                      f'the given value k={k} only by suppression')
            else:
                data_ec = pd.DataFrame({'equiv_class': equiv_class, 'k': len_ec})
                data_ec_k = data_ec[data_ec.k < k]
                ec_elim = np.concatenate([anonymity.utils.aux_functions.convert(ec)
                                          for ec in data_ec_k.equiv_class.values])
                table_new = table.drop(ec_elim).reset_index()
                assert anonymity.k_anonymity(table_new, qi) >= k

                # TODO Metrics
                em.end_monitor_time()
                em.monitor_cost("data_fly")
                em.monitor_memory_consumption_stop()

                return table_new

        # Calculate the attribute with more unique values
        occurrences_qi = [len(np.unique(table[i])) for i in qi_aux]
        name = qi_aux[np.argmax(occurrences_qi)]

        # TODO Metrics
        em.monitor_cost_add("datafly")
        new_ind = ut.generalization(table[name].values.tolist(), hierarchies,
                                    current_gen_level[name] + 1, name)

        if new_ind is None:
            if name in qi:
                qi.remove(name)
                qi_aux = copy.copy(qi)
        else:
            table[name] = new_ind
            current_gen_level[name] = current_gen_level[name] + 1

        k_real = anonymity.k_anonymity(table, qi)
        dum.get_level_generalization(name, current_gen_level[name])

    # TODO Metrics
    em.end_monitor_time()
    em.monitor_cost("datafly")
    em.monitor_memory_consumption_stop()

    return table
