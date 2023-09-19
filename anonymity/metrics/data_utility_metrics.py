import typing
import numpy as np
import pandas as pd
from pycanon import anonymity

# Global variables for metrics
LEVEL_GEN = {}


def start_level():
    """Resets the global variable which contains the generalization
    levels of each parameter of the table of the function which is
    being monitored."""

    global LEVEL_GEN
    LEVEL_GEN = {}


def get_level_generalization(name: str, level: int):
    """Updates the global variable which contains the generalization
    levels of each parameter of the table of the function which is being monitored.

    :param name: Name of the column which level we want to save
    :type name: string

    :param level: Level of generalization of a given column.
    :type level: int
    """

    global LEVEL_GEN
    LEVEL_GEN[name] = level


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

    if isinstance(column, str):
        aux = column.replace("[", "")
        aux = aux.replace(" ", "")

        aux = aux.replace(")", "")
        aux_2 = aux.split(",")
        new_col.append(
            pd.Interval(left=float(aux_2[0]), right=float(aux_2[1]), closed="left")
        )

        return new_col[0]

    for i in column:
        aux = i.replace("[", "")
        aux = aux.replace(" ", "")

        aux = aux.replace(")", "")
        aux_2 = aux.split(",")
        new_col.append(
            pd.Interval(left=float(aux_2[0]), right=float(aux_2[1]), closed="left")
        )

    column = new_col
    return column


def create_vgh(hierarchy: dict) -> typing.Union[typing.List, np.ndarray]:
    """Creates the auxiliary hierarchies to facilitate the measuring of the
    information loss function.

    :param hierarchy: hierarchies for generalization of string columns.
    :type hierarchy: dictionary

    :param og_table: dataframe with the original data under study.
    :type og_table: pandas dataframe

    :param new_table: dataframe with the anonymized data under study.
    :type new_table: pandas dataframe

    :param numeric_hie: steps for the intervals of numeric columns.
    :type numeric_hie: dictionary

    :return: an array with both the auxiliar hierarchies and the number of
    occurancies of each element on both the original table and the anonymized table.
    :rtype: array of dictionaries
    """

    vgh = {}
    numb_vgh = {}

    for i in hierarchy.keys():
        vgh_aux = {}

        for j in hierarchy[i]:
            numb_vgh[j[LEVEL_GEN[i]]] = 0

        for j in hierarchy[i]:
            numb_vgh[j[LEVEL_GEN[i]]] += 1
            numb_vgh[j[0]] = 1
            vgh_aux[j[0]] = j[LEVEL_GEN[i]]

        vgh[i] = vgh_aux

    return [vgh, numb_vgh]


def generalized_information_loss(
    hierarchy: dict,
    og_table: pd.DataFrame,
    new_table: pd.DataFrame,
    qi: typing.Union[typing.List, np.ndarray],
) -> float:
    """Captures the penalty incurred when generalizing a table, by quantifying the
    fraction of the domain values that have been generalized for each specific attribute.

    :param hierarchy: hierarchies for generalization of string columns.
    :type hierarchy: dictionary

    :param og_table: dataframe with the original data under study.
    :type og_table: pandas dataframe

    :param new_table: dataframe with the anonymized data under study.
    :type new_table: pandas dataframe

    :param numeric_hie: steps for the intervals of numeric columns.
    :type numeric_hie: dictionary

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :return: The penalty incurred when generalizing a table.
    :rtype: float
    """

    vgh_aux = create_vgh(hierarchy)
    vgh = vgh_aux[0]
    numb_vgh = vgh_aux[1]

    n = len(qi)
    t = len(og_table)

    d = 0

    for i in qi:
        for j in range(0, t):
            # One or both parameters are strings
            b = numb_vgh[vgh[i][og_table[i][j]]] - numb_vgh[og_table[i][j]]
            c = len(vgh[i]) - 1

            d = d + (b / c)

    return (1 / (t * n)) * d


def discernibility(
    og_table: pd.DataFrame,
    new_table: pd.DataFrame,
    qi: typing.Union[typing.List, np.ndarray],
) -> float:
    """Measures how indistinguishable a record is from others, by assigning a
    penalty to each record, equal to the size of the EQ to which it belongs.

    :param og_table: dataframe with the original data under study.
    :type og_table: pandas dataframe

    :param new_table: dataframe with the anonymized data under study.
    :type new_table: pandas dataframe

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :return: Measure of how indistinguishable the table is.
    :rtype: float
    """

    t = len(og_table)
    k = anonymity.k_anonymity(new_table, qi)
    eq = anonymity.utils.aux_anonymity.get_equiv_class(new_table, qi)
    a = 0

    for i in eq:
        if len(i) >= k:
            a = a + pow(len(i), 2)
    return a


def avr_equiv_class_size(
    og_table: pd.DataFrame,
    new_table: pd.DataFrame,
    qi: typing.Union[typing.List, np.ndarray],
) -> float:
    """Measures how well the creation of the EQs approaches the best case, where each record
    is generalized in an EQ of k records.

    :param og_table: dataframe with the original data under study.
    :type og_table: pandas dataframe

    :param new_table: dataframe with the anonymized data under study.
    :type new_table: pandas dataframe

    :param qi: list with the name of the columns of the dataframe.
        that are quasi-identifiers.
    :type qi: list of strings

    :return: Measure of how well the creation of the EQs approaches the best case.
    :rtype: float
    """

    t = len(og_table)
    k = anonymity.k_anonymity(new_table, qi)
    eq = anonymity.utils.aux_anonymity.get_equiv_class(new_table, qi)
    return t / (len(eq) * k)
