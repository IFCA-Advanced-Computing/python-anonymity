import copy
import typing
import numpy as np
import pandas as pd
from pycanon import anonymity
from data_fly import data_fly
from incognito import incognito


def l_diversity(eq: typing.Union[typing.List, np.ndarray]) -> int:
    """Counts the l-diversity of a given equivalence class

    :param eq: equivalence class under study.
    :type eq: list

    :return: l-diversity of a given equivalence class.
    :rtype: pandas dataframe
    """
    un_values = np.unique(eq)
    return len(un_values)


def get_diversities(table: pd.DataFrame, sa: typing.Union[typing.List, np.ndarray],
                    qi: typing.Union[typing.List, np.ndarray]) -> typing.Union[typing.List, np.ndarray]:
    # Nos devuelve arrays con los indices de cada clase de quivalencia
    """Return the l-diversity value as an integer. Calls the get_diversities and extract the minimum l-diversity level.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param sa: list with the name of the columns of the dataframe.
        that are sensitive attributes.
    :type sa: list of strings

    :param qi: list which contains a list of arrays which represent each equivalence class and a list with
    the l-diversity value for each of those classes.
    :type qi: list of arrays
    """
    equiv_class = anonymity.utils.aux_anonymity.get_equiv_class(table, qi)

    equiv_sa = []
    count = 0
    for i in equiv_class:
        equiv_sa.append([])
        for j in i:
            equiv_sa[count].append(table[sa].values.tolist()[j][0])
        count += 1

    result = []
    for i in equiv_sa:
        # print(i)
        res = l_diversity(i)
        result.append(res)
    # print(result)
    return [equiv_sa, result]


def get_l(table: pd.DataFrame, sa: typing.Union[typing.List, np.ndarray],
          qi: typing.Union[typing.List, np.ndarray]) -> int:
    """Return the l-diversity value as an integer. Calls the get_diversities and extract the minimum l-diversity level.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param sa: list with the name of the columns of the dataframe.
        that are sensitive attributes.
    :type sa: list of strings

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :return: minimum l-diversity of a given list of l-diversity values.
    :rtype: int
    """

    return min(get_diversities(table, qi, sa)[1])


# TODO Añadir una version en la que el usuario nos meta el % de registros que permite suprimir
def apply_l_diversity_supp(table: pd.DataFrame, sa: typing.Union[typing.List, np.ndarray],
                           qi: typing.Union[typing.List, np.ndarray], l: int) -> pd.DataFrame:
    if get_l(table, qi, sa) < l:
        print("l-diversity satisfied")
        return table

    equiv_class = anonymity.utils.aux_anonymity.get_equiv_class(table, qi)
    l_eq_c = get_diversities(table, sa, qi)[1]

    if l > max(l_eq_c):
        print("l-diversity cannot be satisfied with suppression")
        return table

    else:
        data_ec = pd.DataFrame({'equiv_class': equiv_class, 'l': l_eq_c})
        data_ec_l = data_ec[data_ec.l_eq_c < l]
        ec_elim = np.concatenate([anonymity.utils.aux_functions.convert(ec)
                                  for ec in data_ec_l.equiv_class.values])
        table_new = table.drop(ec_elim).reset_index()
        assert anonymity.l_diversity(table_new, qi, sa) >= l

        return table_new


# TODO Suprimir por columnas, ordenar QI por importancia
def apply_l_diversity_qi(table: pd.DataFrame, sa: typing.Union[typing.List, np.ndarray],
                           qi: typing.Union[typing.List, np.ndarray], l: int) -> pd.DataFrame:
    if get_l(table, qi, sa) < l:
        print("l-diversity satisfied")
        return table

        for i in qi:
            new_table = table.copy()
            # TODO esto no es similar al de abajo?


# La idea es que usando las funciones auxiliares de arriba esto devolviera una nueva tabla anonimizada
# con una k superior.
def apply_l_diversity(table: pd.DataFrame, sa: typing.Union[typing.List, np.ndarray],
                      qi: typing.Union[typing.List, np.ndarray], k_anon: str, l: int,
                      ident: typing.Union[typing.List, np.ndarray], supp_threshold: int,
                      hierarchies: dict, k: int) -> pd.DataFrame:
    """Apply l-diversity to an anonymized dataset.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param sa: list with the name of the columns of the dataframe.
        that are sensitive attributes.
    :type sa: list of strings

    :param ident: list with the name of the columns of the dataframe.
        that are identifiers.
    :type ident: list of strings

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :param k: desired level of k-anonymity.
    :type k: int

    :param k_anon: desired algorithm for anonymization.
    :type k_anon: string

    :param l: desired level of l-diversity.
    :type l: int

    :param supp_threshold: level of suppression allowed.
    :type supp_threshold: int

    :param hierarchies: hierarchies for generalization of columns.
    :type hierarchies: dictionary

    :return: anonymized table that satisfies l-diversity.
    :rtype: pandas dataframe
    """
    count = 0
    while get_l(table, qi, sa) > l and count < 50:

        if k_anon == "data_fly":
            k = k + 1
            return data_fly(table, ident,
                            qi, k, supp_threshold,
                            hierarchies)

        else:
            k = k + 1
            return incognito(table, hierarchies,
                             k, qi, supp_threshold,
                             ident)
        count += 1

    else:
        print("l-diversity satisfied")
        return get_l(table, qi, sa)



# NO SIRVE
def apply_l_diversity_v2(table: pd.DataFrame, sa: typing.Union[typing.List, np.ndarray],
                         qi: typing.Union[typing.List, np.ndarray], k_anon: str,
                         l: int, ident: typing.Union[typing.List, np.ndarray],
                         sa_hierarchies: dict = {}) -> pd.DataFrame:
    """Apply l-diversity to an anonymized dataset.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param sa: list with the name of the columns of the dataframe.
        that are sensitive attributes.
    :type sa: list of strings

    :param ident: list with the name of the columns of the dataframe.
        that are identifiers.
    :type ident: list of strings

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :param l: desired level of l-diversity.
    :type l: int

    :param k_anon: desired algorithm for anonymization.
    :type k_anon: string

    :param sa_hierarchies: hierarchies for generalization of columns.
    :type sa_hierarchies: dictionary

    :return: anonymized table that satisfies l-diversity.
    :rtype: pandas dataframe
    """

    if get_l(table, qi, sa) > l:
        if k_anon == "data_fly":
            new_table = data_fly(copy.deepcopy(table), ident, sa, l, 0, sa_hierarchies)
            if get_l(table, qi, sa) <= l:
                print("l-diversity satisfied after anonymization with data-fly")
                return new_table

            print("Unable to satisfy " + l + " l-diversity")
            return table

        else:
            new_table = incognito(copy.deepcopy(table), sa_hierarchies, l, sa, 0, ident)
            if get_l(table, qi, sa) <= l:
                print("l-diversity satisfied after anonymization with incognito")
                return new_table

            print("Unable to satisfy " + l + " l-diversity")
            return table

    else:
        print("l-diversity satisfied")
        return table
