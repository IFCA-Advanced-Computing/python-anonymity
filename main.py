import pandas as pd
from numpy import inf
from pycanon import anonymity


def clear_white_spaces(table):
    old_column_names = table.keys().values.tolist()
    new_column_names = {}

    for i in old_column_names:
        new_column_names[i] = i.strip()

    table = table.rename(columns=new_column_names)

    return table


def generalization(column, range_step, hierarchies, current_gen_level, name):
    if name in hierarchies is False and name in range_step is False:
        return column
    elif name in hierarchies:
        aux = hierarchies.get(name)
        new_hierarchy = {}
        for i in range(0, len(aux)):
            if len(aux[i]) > (current_gen_level + 1):
                new_hierarchy[aux[i][current_gen_level]] = aux[i][current_gen_level + 1]
            else:
                new_hierarchy[aux[i][current_gen_level]] = '*'
        # print(newHie)
        aux = new_hierarchy
    else:
        aux = range_step.get(name)[current_gen_level + 1]

    # Generalization of numbers
    if (isinstance(column[0][0], int) or isinstance(column[0][0], float) or
            isinstance(column[0][0], complex)):
        print("numb")

        min_range = inf
        max_range = 0

        for i in column:
            if i[0] > max_range:
                max_range = i[0]
            if i[0] < min_range:
                min_range = i[0]

        # print("Min: ", min)
        # print("Max: ", max)

        while min_range % aux != 0 or max_range % aux != 0:
            if min_range % aux != 0:
                min_range = min_range - 1
            if max_range % aux != 0:
                max_range = max_range + 1

        # print("Min: ", min)
        # print("Max: ", max)

        step = int((max_range - min_range) / aux)
        # print(step)
        ranges = []
        for i in range(0, step):
            # ranges.append([min + aux*i, min + aux*(i+1)])
            if i == (step - 1):
                ranges.append([min_range + aux * i, (min_range + aux * (i + 1))])
            else:
                ranges.append([min_range + aux * i, (min_range + aux * (i + 1)) - 1])
        # print(ranges)

        new_col = []
        for i in range(0, len(column)):
            for j, (start, end) in enumerate(ranges, start=1):
                if column[i][0] in range(start, end + 1):
                    new_col.append(ranges[j - 1])
                    break

        column = new_col
        # print(ranges)
        # print(column)

    # Generalization of strings
    elif isinstance(column[0][0], str):
        print("string")
        for i in range(0, len(column)):
            column[i][0] = aux[column[i][0].strip()]

        # print(column)

    # Generalization of ranges
    else:
        print("range")
        min_range = inf
        max_range = 0

        for i in column:
            if i[0][0] > max_range:
                max_range = i[0][0]
            if i[0][0] < min_range:
                min_range = i[0][0]

        # print("Min: ", min)
        # print("Max: ", max)

        while min_range % aux != 0 or max_range % aux != 0:
            if min_range % aux != 0:
                min_range = min_range - 1
            if max_range % aux != 0:
                max_range = max_range + 1

        # print("Min: ", min)
        # print("Max: ", max)

        step = int((max_range - min_range) / aux)
        # print(step)
        ranges = []
        for i in range(0, step):
            if i == (step - 1):
                ranges.append([min_range + aux * i, (min_range + aux * (i + 1))])
            else:
                ranges.append([min_range + aux * i, (min_range + aux * (i + 1)) - 1])
        # print(ranges)

        new_col = []
        for i in range(0, len(column)):
            for j, (start, end) in enumerate(ranges, start=1):
                if column[i][0][0] in range(start, end + 1):
                    new_col.append(ranges[j - 1])
                    break

        column = new_col
        # print(ranges)
        # print(column)

    return column


# RangeStep should be a dictionary which key is the name of the quasi-identifier and the
#       value is a list of different steps for each of the ranges per level of the identifier.
# Hierarchies should be a dictionary which key is the name of the quasi-identifier and the
#       value is a list of list, which index identifies each level generalizations for said
#       quasi-identifier.
def data_fly(table, qi, sa, k, supp_threshold, range_step={}, hierarchies={}):
    current_supp = 0
    len_table = len(table)
    current_gen_level = 0

    freq_cs = anonymity.k_anonymity(table, qi)
    if freq_cs >= k:
        return table

    if freq_cs <= supp_threshold:
        # Suppress tables
        return table

    else:
        unique_values = []
        number_of_occurrences = 0
        index = ''

        # Calculate the attribute with more unique values
        for i in qi:
            if number_of_occurrences < len(unique_values):
                index = i
                unique_values = table[i].keys()  # equals to list(set(words))
                number_of_occurrences = len(unique_values)
                # table[i].values()  # counts the elements' frequency

        new_ind = generalization(table[index], range_step, hierarchies,
                                 current_gen_level, DATA.keys().values.tolist()[index])
        new_ind = pd.DataFrame({'index': new_ind})
        table[index] = new_ind

    return table


FILE_NAME = "adult.csv"
QI = ["age", "education", "occupation", "relationship", "sex", "native-country", "workclass"]
SA = ["salary-class"]
age_hierarchy = {"age": [0, 5, 10, 20]}
workclass_hierarchy = {"workclass": [["Private", "Non-Government", "*"],
                                     ["Self-emp-not-inc", "Non-Government", "*"],
                                     ["Self-emp-inc", "Non-Government", "*"],
                                     ["Federal-gov", "Government", "*"],
                                     ["Local-gov", "Government", "*"],
                                     ["State-gov", "Government", "*"],
                                     ["Without-pay", "Unemployed", "*"],
                                     ["Never-worked", "Unemployed", "*"],
                                     ["?", "Unknown", "*"]]}

DATA = pd.read_csv(FILE_NAME)

# print(type(type(DATA[["age"]].values.tolist()[0][0])))
# print(DATA.keys().values.tolist()[0])

DATA = clear_white_spaces(DATA)

generalization(DATA[["workclass"]].values.tolist(), age_hierarchy, workclass_hierarchy,
               0, "workclass")

new_column = generalization(DATA[["age"]].values.tolist(), age_hierarchy, workclass_hierarchy,
               0, "age")

DATA["age"] = new_column

generalization(DATA[["age"]].values.tolist(), age_hierarchy, workclass_hierarchy,
               1, "age")