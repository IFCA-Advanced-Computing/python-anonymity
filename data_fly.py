import numpy as np
import pandas as pd
from numpy import inf
from pycanon import anonymity
import copy
import efficiency_metrics as em
import data_utility_metrics as dum
import typing


def clear_white_spaces(table: pd.DataFrame) -> pd.DataFrame:
    """Deletes any white spaces from column names.

    :param table:  dataframe with the data under study.
    :type table: pandas dataframe

    :return: table which columns don't contain whitespaces.
    :rtype: pandas dataframe
    """

    old_column_names = table.keys().values.tolist()
    new_column_names = {}

    for i in old_column_names:
        new_column_names[i] = i.strip()

    table = table.rename(columns=new_column_names)
    return table


def suppress_identifiers(table: pd.DataFrame, ident: typing.Union[typing.List, np.ndarray]) -> pd.DataFrame:
    """Removes all the identifiers in the database.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param ident: list with the name of the columns of the dataframe
        that are identifiers.
    :type ident: list of strings

    :return: table with the identifiers fully anonymized.
    :rtype: pandas dataframe
    """

    for i in ident:
        table[i] = '*'
    return table


def has_numbers(string: str) -> bool:
    """Checks if a string contains numbers

    :param string: string under study
    :type string: python string

    :return: boolean that indicates wether a string contains numbers or not.
    :rtype: boolean
    """

    return any(i.isdigit() for i in string)


def string_to_interval(column: typing.Union[typing.List, np.ndarray]) -> typing.Union[typing.List, np.ndarray]:
    """Converts a string interval to an actual interval type,
    to facilitate the comparison of each data.

    :param column: List of intervals as strings.
    :type column: list of strings

    :return: List containing the intervals converted to the proper data type.
    :rtype: list of intervals
    """

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


def generalization(column: typing.Union[typing.List, np.ndarray], range_step: dict, hierarchies: dict,
                   current_gen_level: int, name: str) -> typing.Union[typing.List, np.ndarray]:
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
    elif isinstance(column[0][0], str) and '[' not in column[0][0]:
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


def data_fly(table: pd.DataFrame, ident: typing.Union[typing.List, np.ndarray],
             qi: typing.Union[typing.List, np.ndarray], k: int,
             supp_threshold: int, range_step: dict = {}, hierarchies: dict = {}) -> pd.DataFrame:
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

    :param range_step: steps for the intervals of numeric columns.
    :type range_step: dictionary

    :param hierarchies: hierarchies for generalization of string columns.
    :type hierarchies: dictionary

    :return: anonymized table.
    :rtype: pandas dataframe
    """

    # TODO Metrics
    em.start_monitor_time()
    em.monitor_cost_init("data_fly")
    em.monitor_memory_consumption_start()
    dum.start_level()

    table = clear_white_spaces(table)
    table = suppress_identifiers(table, ident)

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
                print(f'The anonymization cannot be carried out for the given value k={k} only by suppression')
            else:
                data_ec = pd.DataFrame({'equiv_class': equiv_class, 'k': len_ec})
                data_ec_k = data_ec[data_ec.k < k]
                ec_elim = np.concatenate([anonymity.utils.aux_functions.convert(ec)
                                          for ec in data_ec_k.equiv_class.values])
                table_new = table.drop(ec_elim).reset_index()
                assert (anonymity.k_anonymity(table_new, qi) >= k)

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
        new_ind = generalization(table[[name]].values.tolist(), range_step, hierarchies,
                                 current_gen_level[name], name)

        if new_ind is None:
            qi_aux = copy.copy(qi)
            qi_aux.remove(name)
        else:
            table[name] = new_ind

        k_real = anonymity.k_anonymity(table, qi)
        current_gen_level[name] = current_gen_level[name] + 1
        dum.get_level_generalization(name, current_gen_level[name])

    # TODO Metrics
    em.end_monitor_time()
    em.monitor_cost("datafly")
    em.monitor_memory_consumption_stop()

    return table
