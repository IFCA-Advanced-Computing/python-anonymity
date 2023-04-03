import copy
import typing
import numpy as np
import pandas as pd


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


def suppress_identifiers(
        table: pd.DataFrame,
        ident: typing.Union[typing.List, np.ndarray]) -> pd.DataFrame:
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
        aux = i.replace("[", "")
        aux = aux.replace(" ", "")

        aux = aux.replace(")", "")
        aux_2 = aux.split(",")
        new_col.append(pd.Interval(left=float(aux_2[0]),
                                   right=float(aux_2[1]),
                                   closed='left'))

    column = new_col
    return column


# TODO Devuelve tanto la jerarquia nueva como los rangos creados
def create_ranges(data, range_step):
    table = copy.deepcopy(data)
    new_hie = {}
    for i in range_step.keys():
        new_hie[i] = []
        for j in range(1, len(range_step[i])):
            aux = range_step[i][j]
            # Generalization of numbers
            if (isinstance(table[i][0], int) or isinstance(table[i][0], np.int64) or isinstance(table[i][0], float) or
                    isinstance(table[i][0], complex)):

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

                for m in range(0, len(new_hie[i])):
                    for n in ranges:
                        if new_hie[i][m][0] in n:
                            new_hie[i][m].append(str(n))
                            break

                for m in range(0, len(table[i])):
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
                for m in range(0, len(column)):
                    for n in ranges:
                        if column[m].left in n:
                            new_col.append(str(n))
                            break

                table[i] = new_col

        return new_hie
