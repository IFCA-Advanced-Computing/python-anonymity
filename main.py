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


def clear_data(table):

    for i in table.keys().values.tolist():
        if i not in QI and i not in SA:
            table = table.drop(i, axis=1)

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
                    new_col.append(j)
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
            if i[0].left > max_range:
                max_range = i[0].right
            if i[0].left < min_range:
                min_range = i[0].left

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
                if column[i][0] in j:
                    new_col.append(j)
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
    print(freq_cs)
    if freq_cs >= k:
        return table

    if freq_cs <= supp_threshold:
        # Suppress tables
        return table

    else:
        unique_values = []
        number_of_occurrences = 0
        index = 0

        # Calculate the attribute with more unique values
        for i in range(0, len(qi)):
            if number_of_occurrences < len(unique_values):
                index = i
                unique_values = table[i].keys()  # equals to list(set(words))
                number_of_occurrences = len(unique_values)
                # table[i].values()  # counts the elements' frequency

        name = table.keys().values.tolist()[index]
        new_ind = generalization(table[name], range_step, hierarchies,
                                 current_gen_level, name)
        table[name] = new_ind

        print(table[name])

    return table


# Function to test if the generalization function is capable of generalizing numbers, strings
# and ranges
def generalization_test_1():
    file_name = "adult.csv"
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

    data = pd.read_csv(file_name)

    # print(type(type(DATA[["age"]].values.tolist()[0][0])))
    # print(DATA.keys().values.tolist()[0])

    data = clear_white_spaces(data)

    generalization(data[["workclass"]].values.tolist(), age_hierarchy, workclass_hierarchy,
                   0, "workclass")

    new_column = generalization(data[["age"]].values.tolist(), age_hierarchy,
                                workclass_hierarchy, 0, "age")

    data["age"] = new_column

    generalization(data[["age"]].values.tolist(), age_hierarchy, workclass_hierarchy,
                   1, "age")


file_name = "hospital_extended.csv"
QI = ["age", "gender", "city"]
SA = ["disease"]
age_hierarchy = {"age": [0, 2, 4]}
city_hierarchy = {"city": [["Tamil Nadu", "India north", "*"],
                                     ["Kerala", "India south", "*"],
                                     ["Karnataka", "India north", "*"],
                                     ["?", "Unknown", "*"]]}

data = pd.read_csv(file_name)
data = clear_white_spaces(data)
copy_data = data

data = clear_data(data)
# print(data)

data["age"] = generalization(data[["age"]].values.tolist(), age_hierarchy,
                            city_hierarchy, 1, "age")

data["city"] = generalization(data[["city"]].values.tolist(), age_hierarchy,
                              city_hierarchy, 0, "city")

data["age"] = generalization(data[["age"]].values.tolist(), age_hierarchy,
                            city_hierarchy, 1, "age")

# print(data)

print(anonymity.k_anonymity(data_fly(data, QI, SA, 2, 0, age_hierarchy, city_hierarchy), QI))