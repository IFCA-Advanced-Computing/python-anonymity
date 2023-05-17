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
        if isinstance(i, list):
            return column

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
        if len(hierarchies[name][0]) > gen_level:
            aux = hierarchies[name]
        else:
            return None

    # Generalization of numbers
    if isinstance(column[0], (int, float, complex, np.int64)):

        aux_col = []
        for i in range(0, len(aux)):
            aux_col.append(aux[i][gen_level])

        ranges = string_to_interval(aux_col)
        new_col = []

        for i in range(len(column)):
            for j in ranges:
                if column[i] in j:
                    new_col.append(str(j))
                    break

        column = new_col

    # Generalization of strings

    elif isinstance(column[0], str) and '[' not in column[0]:
        if isinstance(column, list):
            pass
        else:
            column = column.values
        for i in range(len(column)):
            # TODO Aux esta mal, deberia ser la lista con todas las jerarquias de los "marital status"
            for j in range(len(aux)):
                if aux[j][0] == column[i]:
                    column[i] = aux[j][gen_level]
                    break

    # Generalization of ranges
    else:
        column = string_to_interval(column)
        aux_col = []
        for i in range(len(aux)):
            aux_col.append(aux[i][gen_level])

        ranges = string_to_interval(aux_col)

        new_col = []
        for i in range(len(column)):
            for j in ranges:
                if column[i].left in j:
                    new_col.append(str(j))
                    break

        column = new_col

    return column

