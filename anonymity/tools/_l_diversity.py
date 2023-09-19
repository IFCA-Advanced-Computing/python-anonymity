import copy
import typing
import numpy as np
import pandas as pd
from pycanon import anonymity
from anonymity.tools._k_anonymity import data_fly
from anonymity.tools._k_anonymity import incognito


def get_diversities(
    table: pd.DataFrame,
    sa: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
) -> typing.Union[typing.List, np.ndarray]:
    """Return the l-diversity value as an integer. Calls the get_diversities and extract the
    minimum l-diversity level.

    :param table: dataframe with the data under study.
    :type table: pandas dataframe

    :param sa: list with the name of the columns of the dataframe.
        that are sensitive attributes.
    :type sa: list of strings

    :param qi: list which contains a list of arrays which represent each equivalence
    class and a list with the l-diversity value for each of those classes.
    :type qi: list of arrays
    """
    equiv_class = anonymity.utils.aux_anonymity.get_equiv_class(table, qi)

    equiv_sa = []
    for ec in equiv_class:
        tmp = table.iloc[ec]
        equiv_sa.append(tmp[sa].values)

    result = [len(np.unique(ec_sa)) for ec_sa in equiv_sa]
    return [equiv_sa, result]


def get_l(
    table: pd.DataFrame,
    sa: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
) -> int:
    """Return the l-diversity value as an integer.
    Calls the get_diversities and extract the minimum l-diversity level.

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


def apply_l_diversity_supp(
    table: pd.DataFrame,
    sa: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
    l: int,
    supp_lim: float = 1,
) -> pd.DataFrame:
    total_percent = len(table)
    supp_records = round(total_percent * (supp_lim / 100))
    l_real = anonymity.l_diversity(table, qi, sa)
    """Apply l-diversity to an anonymized dataset using suppression.

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

        :param k_method: desired algorithm for anonymization.
        :type k_method: string

        :param l: desired level of l-diversity.
        :type l: int

        :param supp_threshold: level of suppression allowed.
        :type supp_threshold: int

        :param hierarchies: hierarchies for generalization of columns.
        :type hierarchies: dictionary

        :return: anonymized table that satisfies l-diversity.
        :rtype: pandas dataframe
        """

    if len(table[sa].value_counts()) < l:
        print(
            "l-diversity cannot be satisfied only with row suppression, "
            "due to l being bigger than the unique values of the SA column"
        )
        return table

    if l_real >= l:
        print(f"l-diversity is satisfied with l={l_real}")
        return table

    equiv_class = anonymity.utils.aux_anonymity.get_equiv_class(table, qi)
    l_eq_c = get_diversities(table, sa, qi)[1]

    if l > max(l_eq_c):
        print("l-diversity cannot be satisfied only with row suppression")
        return table

    else:
        supp_rate = 0
        print("supp_records ", supp_records)
        while supp_rate <= supp_records:
            data_ec = pd.DataFrame({"equiv_class": equiv_class, "l": l_eq_c})
            data_ec_l = data_ec[data_ec.l > l]

            ec_elim = np.concatenate(
                [
                    anonymity.utils.aux_functions.convert(ec)
                    for ec in data_ec_l.equiv_class.values
                ]
            )
            # print(ec_elim)
            table_new = table.drop(ec_elim[0]).reset_index()
            # print(table_new)
            supp_rate = (len(table) - len(table_new)) / len(table)
            if supp_rate > supp_records:
                print(
                    f"l-diversity cannot be satisfied by deleting less than "
                    f"{supp_records}% of the records."
                )
                return table

        assert anonymity.l_diversity(table_new, qi, sa) >= l
        return table_new


# La idea es que usando las funciones auxiliares de arriba esto devolviera una nueva tabla anonimizada
# con una k superior.
def apply_l_diversity(
    table: pd.DataFrame,
    sa: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
    k_method: str,
    l: int,
    ident: typing.Union[typing.List, np.ndarray],
    supp_threshold: int,
    hierarchies: dict,
    k: int,
) -> pd.DataFrame:
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

    :param k_method: desired algorithm for anonymization.
    :type k_method: string

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
    # print(l)
    # print(get_l(table, qi, sa))
    while get_l(table, qi, sa) < l and count < 50:
        if k_method == "data_fly":
            k = k + 1
            table = data_fly(table, ident, qi, k, supp_threshold, hierarchies)

        else:
            k = k + 1
            table = incognito(table, ident, qi, k, supp_threshold, hierarchies)
        count += 1

    if count >= 50:
        print("l-diversity not satisfied")
        return [get_l(table, qi, sa), table, False]

    else:
        print("l-diversity satisfied")
        return [get_l(table, qi, sa), table, True]


def apply_l_diversity_multiple_sa(
    table: pd.DataFrame,
    sa: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
    k_method: str,
    l: int,
    ident: typing.Union[typing.List, np.ndarray],
    supp_threshold: int,
    hierarchies: dict,
    k: int,
) -> pd.DataFrame:
    """Apply l-diversity to an anonymized dataset with multiple SA.

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

    :param k_method: desired algorithm for anonymization.
    :type k_method: string

    :param l: desired level of l-diversity.
    :type l: int

    :param supp_threshold: level of suppression allowed.
    :type supp_threshold: int

    :param hierarchies: hierarchies for generalization of columns.
    :type hierarchies: dictionary

    :return: returns a list containing the value of l-diversity of the new table and the
    anonymized table that satisfies l-diversity.
    :rtype: list
    """
    limit = len(sa)
    count = 0
    new_table = copy.deepcopy(table)
    l_div = []
    new_hierarchies = copy.deepcopy(hierarchies)
    while count < limit:
        new_qi = qi + sa[:count] + sa[count + 1 :]
        # print(new_qi)
        new_sa = sa[count]

        result = apply_l_diversity(
            new_table,
            new_sa,
            new_qi,
            k_method,
            l,
            ident,
            supp_threshold,
            new_hierarchies,
            k,
        )

        if not result[2]:
            print("l-diversity not satisfied for ", sa[count:])
            return [l_div, new_table]

        l_div.append(result[0])
        new_table = result[1]
        count += 1

    return [l_div, new_table]


def l_diversity(
    table: pd.DataFrame,
    sa: typing.Union[typing.List, np.ndarray],
    qi: typing.Union[typing.List, np.ndarray],
    k_method: str,
    l: int,
    ident: typing.Union[typing.List, np.ndarray],
    supp_threshold: int,
    hierarchies: dict,
    k: int,
) -> pd.DataFrame:
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

        :param k_method: desired algorithm for anonymization.
        :type k_method: string

        :param l: desired level of l-diversity.
        :type l: int

        :param supp_threshold: level of suppression allowed.
        :type supp_threshold: int

        :param hierarchies: hierarchies for generalization of columns.
        :type hierarchies: dictionary

        :return: anonymized table that satisfies l-diversity.
        :rtype: pandas dataframe
    """
    if len(sa) > 1:
        return apply_l_diversity_multiple_sa(
            table, sa, qi, k_method, l, ident, supp_threshold, hierarchies, k
        )
    else:
        return apply_l_diversity(
            table, sa, qi, k_method, l, ident, supp_threshold, hierarchies, k
        )
