import copy
import re
import typing
import numpy as np
import pandas as pd
import pycanon.anonymity as pc
from pycanon.anonymity.utils import aux_functions
from pycanon.anonymity.utils.aux_anonymity import get_equiv_class
from anonymity.tools._k_anonymity import data_fly
from anonymity.tools._k_anonymity import incognito


def aux_t_closeness_num(
    data: pd.DataFrame, quasi_ident: typing.Union[list, np.ndarray], sens_att_value: str
) -> float:
    """Obtain t for t-closeness.
    Function used for numerical attributes: the definition of the EMD is used.
    :param data: dataframe with the data under study.
    :type data: pandas dataframe
    :param quasi_ident: list with the name of the columns of the dataframe
        that are quasi-identifiers.
    :type quasi_ident: list of strings
    :param sens_att_value: sensitive attribute under study.
    :type sens_att_value: string
    :return: t for the introduced SA (numerical).
    :rtype: float.
    """
    equiv_class = get_equiv_class(data, quasi_ident)
    values = np.unique(data[sens_att_value].values)
    m = len(values)
    p = np.array([len(data[data[sens_att_value] == s]) / len(data) for s in values])
    emd = []
    for ec in equiv_class:
        data_temp = data.iloc[aux_functions.convert(ec)]
        qi = np.array(
            [len(data_temp[data_temp[sens_att_value] == s]) / len(ec) for s in values]
        )
        r = qi - p
        abs_r, emd_ec = 0.0, 0.0
        for i in range(m):
            abs_r += r[i]
            emd_ec += np.abs(abs_r)
        emd_ec = 1 / (m - 1) * emd_ec
        emd.append(emd_ec)
    return max(emd)


def aux_t_closeness_str(
    data: pd.DataFrame,
    quasi_ident: typing.Union[list, np.ndarray],
    sens_att_value: list,
) -> float:
    """Obtain t for t-closeness.
    Function used for categorical attributes: the metric "Equal Distance" is
    used.
    :param data: dataframe with the data under study.
    :type data: pandas dataframe
    :param quasi_ident: list with the name of the columns of the dataframe
        that are quasi-identifiers.
    :type quasi_ident: list of strings
    :param sens_att_value: sensitive attribute under study.
    :type sens_att_value: string
    :return: t for the introduced SA (categorical).
    :rtype: float.
    """
    equiv_class = get_equiv_class(data, quasi_ident)
    values = np.unique(data[sens_att_value].values)
    m = len(values)
    p = np.array([len(data[data[sens_att_value] == s]) / len(data) for s in values])
    emd = []
    for ec in equiv_class:
        data_temp = data.iloc[aux_functions.convert(ec)]
        qi = np.array(
            [len(data_temp[data_temp[sens_att_value] == s]) / len(ec) for s in values]
        )
        r = qi - p
        emd_ec = 0.0
        for i in range(m):
            emd_ec += np.abs(r[i])
        emd_ec = 0.5 * emd_ec
        emd.append(emd_ec)
    return max(emd)


# TODO Añadir el if para elegir entre una de las 2 funciones de arriba segun el type_t
def get_t(
    table: pd.DataFrame,
    sa: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
    type_t: str,
) -> typing.Union[typing.List, np.ndarray]:
    equiv_class = pc.utils.aux_anonymity.get_equiv_class(table, qi)

    global_freqs = {}
    total_count = float(len(table))
    group_counts = table.groupby(sa)[sa].agg("count")

    for value, count in group_counts.to_dict().items():
        for i in count.keys():
            p = count[i] / total_count
            global_freqs[i] = p

    equiv_sa = {}
    equiv_sa_tables = {}
    i = 0
    for ec in equiv_class:
        name = "eq" + str(i)
        tmp = table.iloc[ec]
        equiv_sa_tables[name] = tmp
        equiv_sa[name] = tmp[sa].values
        i += 1

    result = {}
    class_count = {}
    for value in equiv_sa.keys():
        total_count = float(len(equiv_sa[value]))
        class_count = equiv_sa_tables[value]["crime"].value_counts()
        d = 0
        for j in equiv_sa[value]:
            p = float(re.findall(r"\d+", str(class_count[j]))[0]) / total_count
            d += abs(p - global_freqs[j[0]])

            p = float(re.findall(r"\d+", str(class_count[j]))[0]) / total_count

            d += abs(p - global_freqs[j[0]])
        result[value] = d

    return result


def t_closeness(
    table: pd.DataFrame,
    sa: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
    t: float,
    k_method: str,
    ident: typing.Union[typing.List, np.ndarray],
    supp_threshold: int,
    hierarchies: dict,
) -> pd.DataFrame:
    """Apply t-closeness to an anonymized dataset.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param sa: list with the name of the columns of the dataframe.
        that are sensitive attributes.
    :type sa: list of strings

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :param t: threshold for t-closeness
    :type t: float

    :param k_method: string that specifies the type of k-anonymization we want to use
    :type k_method: string

    :param ident: list with the name of the columns of the dataframe.
        that are identifiers.
    :type ident: list of strings

    :param supp_threshold: level of suppression allowed.
    :type supp_threshold: int

    :param hierarchies: hierarchies for generalization of columns.
    :type hierarchies: dictionary

    :return: list which contains the value of t for the anonymized table, the current table that after applying
     t-closeness and true or false whether t-closeness is actually satisfied.
    :rtype: list
    """

    count = 0
    # print(t)
    # print(pc.t_closeness(table, qi, sa))

    k = 0
    type_t = "num"

    if isinstance(table[sa[0]][0], str):
        type_t = "cat"

    # TODO Hacer variable global
    while pc.t_closeness(table, qi, sa) > t and count < 50:
        if k_method == "data_fly":
            k = k + 1
            table = data_fly(table, ident, qi, k, supp_threshold, hierarchies)

        else:
            k = k + 1
            table = incognito(table, ident, qi, k, supp_threshold, hierarchies)
        count += 1

    if count >= 50 or pc.t_closeness(table, qi, sa, type_t) > 1:
        print("t-closeness not satisfied")
        return [pc.t_closeness(table, qi, sa), table, False]

    else:
        print("t-closeness satisfied")
        return [pc.t_closeness(table, qi, sa), table, True]


def t_closeness_supp(
    table: pd.DataFrame,
    sa: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
    t: float,
    supp_lim: float = 1,
) -> pd.DataFrame:
    """Apply t-closeness to an anonymized dataset using suppressing up to the established percentage allowed as input.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param sa: list with the name of the columns of the dataframe.
        that are sensitive attributes.
    :type sa: list of strings

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :param t: threshold for t-closeness
    :type t: float

    :param supp_lim: percentage of suppressed rows allowed
    :type supp_lim: float

    :return: table that covers t-closeness.
    :rtype: pandas dataframe
    """

    total_percent = len(table)
    # print(len(table))
    supp_records = round(total_percent * supp_lim)
    t_real = pc.t_closeness(table, qi, sa)
    if t_real < t:
        print(f"t-closeness is satisfied with t={t_real}")
        return table

    # print(supp_records)
    type_t = "num"

    if isinstance(table[sa[0]][0], str):
        type_t = "cat"

    t_eq_c = get_t(table, sa, qi, type_t)

    if t > max(t_eq_c.values()):
        print("t_closeness cannot be satisfied only with row suppression")
        return table

    else:
        supp_rate = 0
        while supp_rate <= supp_records:
            data_ec = pd.DataFrame({"equiv_class": t_eq_c.keys(), "t": t_eq_c.values()})
            data_ec_t = data_ec[data_ec.t > t]
            # print(data_ec_t)
            ec_elim = np.concatenate(
                [
                    pc.utils.aux_functions.convert(ec[2])
                    for ec in data_ec_t.equiv_class.values
                ]
            )

            # print(ec_elim)
            # print(type(ec_elim[0]))
            table_new = table.drop(int(ec_elim[0])).reset_index()
            supp_rate = (len(table) - len(table_new)) / len(table)
            if supp_rate > supp_records or pc.t_closeness(table_new, qi, sa) > t:
                print(
                    f"t-closeness cannot be satisfied by deleting less than "
                    f"{supp_records}% of the records."
                )
                return table
            else:
                assert pc.t_closeness(table_new, qi, sa) <= t
                return table_new
