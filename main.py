import numpy as np
import pandas as pd
from numpy import inf
from pycanon import anonymity


# Deletes any white spaces from column names
def clear_white_spaces(table):
    old_column_names = table.keys().values.tolist()
    new_column_names = {}

    for i in old_column_names:
        new_column_names[i] = i.strip()

    table = table.rename(columns=new_column_names)

    return table


# Adds * to all columns that are not QI or SA
def clear_data(table):
    aux = []
    for j in range(0, len(table[table.keys().values.tolist()[0]])):
        aux.append('*')

    for i in table.keys().values.tolist():
        if i not in QI and i not in SA:
            # table = table.drop(i, axis=1)
            table[i] = aux

    return table


def has_numbers(string):
    return any(i.isdigit() for i in string)


# Converts a string interval to an actual interval type, so as to facilitate the comparison of each data
def string_to_interval(column):

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
        # print(type(i[0]))
        # new_col.append(pd.Interval(i))
    column = new_col
    # print(column)
    return column


# Generalizes a column based on its data type and return a column full of strings with each new
# value for the dataset.
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
        if len(range_step[name]) > current_gen_level + 1:
            aux = range_step[name][current_gen_level + 1]
        else:
            return None

    # Generalization of numbers
    if (isinstance(column[0][0], int) or isinstance(column[0][0], float) or
            isinstance(column[0][0], complex)):
        # print("numb")

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
            if i == (step - 1):
                ranges.append(pd.Interval(left=(min_range + aux * i),
                                          right=(min_range + aux * (i + 1)),
                                          closed='both'))
            else:
                ranges.append(pd.Interval(left=(min_range + aux * i),
                                          right=(min_range + aux * (i + 1)),
                                          closed='left'))

        # print(ranges)

        new_col = []
        for i in range(0, len(column)):
            for j in ranges:
                if column[i][0] in j:
                    new_col.append(str(j))
                    break

        column = new_col
        # print(ranges)

    # Generalization of strings
    elif isinstance(column[0][0], str) and has_numbers(column[0][0]) is False:
        # print("string")
        for i in range(0, len(column)):
            column[i] = aux[column[i][0].strip()]

    # Generalization of ranges
    else:
        # print("range")
        min_range = inf
        max_range = 0

        column = string_to_interval(column)

        for i in column:
            if i.left > max_range:
                max_range = i.right
            if i.left < min_range:
                min_range = i.left

        # print("Min: ", min_range)
        # print("Max: ", max_range)

        while min_range % aux != 0 or max_range % aux != 0:
            if min_range % aux != 0:
                min_range = min_range - 1
            if max_range % aux != 0:
                max_range = max_range + 1

        # print("Min: ", min_range)
        # print("Max: ", max_range)

        step = int((max_range - min_range) / aux)
        # print(step)
        ranges = []
        for i in range(0, step):
            if i == (step - 1):
                ranges.append(pd.Interval(left=(min_range + aux * i),
                                          right=(min_range + aux * (i + 1)),
                                          closed='both'))
            else:
                ranges.append(pd.Interval(left=(min_range + aux * i),
                                          right=(min_range + aux * (i + 1)),
                                          closed='left'))
        # print(ranges)

        new_col = []
        for i in range(0, len(column)):
            for j in ranges:
                if column[i].left in j:
                    new_col.append(str(j))
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
    current_gen_level = {}
    for i in table.keys().values.tolist():
        current_gen_level[i] = 0
    # print(current_gen_level)
    freq_cs = anonymity.k_anonymity(table, qi)
    qi_aux = qi

    while freq_cs < k:

        if freq_cs <= supp_threshold:
            # Suppress tables
            cs = anonymity.utils.aux_anonymity.get_equiv_class(data, qi)

            for i in cs:
                if len(i) <= supp_threshold:
                    table = table.drop(i, axis=0)

            return table

        else:
            unique_values = []
            number_of_occurrences = 0
            name = " "

            # Calculate the attribute with more unique values
            for i in qi_aux:
                if number_of_occurrences < len(np.unique(table[i])):
                    name = i
                    unique_values = np.unique(table[i])
                    number_of_occurrences = len(unique_values)

            # print(name)

            new_ind = generalization(table[[name]].values.tolist(), range_step, hierarchies,
                                     current_gen_level[name], name)
            if new_ind is None:
                # print(name)
                qi_aux.remove(name)
                # print("################### Cannot generalize more ###################")
                # return table
            else:
                table[name] = new_ind
        # print(qi_aux)

        freq_cs = anonymity.k_anonymity(table, qi)
        current_gen_level[name] = current_gen_level[name] + 1
        # print(table)
        print(freq_cs)

    return table


# Function to test if the generalization function is capable of generalizing numbers, strings
# and ranges
def generalization_test_1():
    file = "adult.csv"
    # QI = ["age", "education", "occupation", "relationship", "sex", "native-country", "workclass"]
    # SA = ["salary-class"]
    age_hie = {"age": [0, 5, 10, 20]}
    workclass_hierarchy = {"workclass": [["Private", "Non-Government", "*"],
                                         ["Self-emp-not-inc", "Non-Government", "*"],
                                         ["Self-emp-inc", "Non-Government", "*"],
                                         ["Federal-gov", "Government", "*"],
                                         ["Local-gov", "Government", "*"],
                                         ["State-gov", "Government", "*"],
                                         ["Without-pay", "Unemployed", "*"],
                                         ["Never-worked", "Unemployed", "*"],
                                         ["?", "Unknown", "*"]]}

    table = pd.read_csv(file)

    # print(type(type(DATA[["age"]].values.tolist()[0][0])))
    # print(DATA.keys().values.tolist()[0])

    table = clear_white_spaces(table)

    generalization(table[["workclass"]].values.tolist(), age_hie, workclass_hierarchy,
                   0, "workclass")

    new_column = generalization(table[["age"]].values.tolist(), age_hie,
                                workclass_hierarchy, 0, "age")

    table["age"] = new_column

    table["age"] = generalization(table[["age"]].values.tolist(), age_hie, workclass_hierarchy,
                                  1, "age")

    print(table)


######################################################################################################
#######################################  TESTING AREA  ###############################################
######################################################################################################


file_name = "hospital.csv"
QI = ["age", "gender", "city"]
SA = ["disease"]
age_hierarchy = {"age": [0, 2, 4, 8, 10]}
city_hierarchy = {"city": [["Tamil Nadu", "India north", "*"],
                                     ["Kerala", "India south", "*"],
                                     ["Karnataka", "India north", "*"],
                                     ["?", "Unknown", "*"]],
                  "gender": [["Female", "*"],
                           ["Male", "*"]],

                  }

data = pd.read_csv(file_name)
data = clear_white_spaces(data)
data = clear_data(data)

data["age"] = generalization(data[["age"]].values.tolist(), age_hierarchy,
                             city_hierarchy, 1, "age")

data["city"] = generalization(data[["city"]].values.tolist(), age_hierarchy,
                              city_hierarchy, 0, "city")

data["age"] = generalization(data[["age"]].values.tolist(), age_hierarchy,
                             city_hierarchy, 1, "age")

# data.to_csv("data_intervals.csv", index=1)
# print(np.unique(data["age"]))
# print(type(data["age"][0]))

# generalization_test_1()  # Check generalization with a different dataset

data = pd.read_csv(file_name)
data = clear_white_spaces(data)
data = clear_data(data)

print(data)

# data_supp = data_fly(data, QI, SA, 2, 1, age_hierarchy, city_hierarchy)
# print(data_supp)  # Check if it can suppress
# print(anonymity.k_anonymity(data_supp, QI)) # Check k-anonymity of the suppressed data

# Try and fix the interval data so that k-anonymity accepts it
# print(anonymity.k_anonymity(data_fly(data, QI, SA, 2, 0, age_hierarchy, city_hierarchy), QI))  # Check new k-anonymity
print(data_fly(data, QI, SA, 3, 0, age_hierarchy, city_hierarchy))
