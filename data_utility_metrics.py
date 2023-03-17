from pycanon import anonymity
import pandas as pd

# Global variables for metrics
LEVEL_GEN = {}


def start_level():
    global LEVEL_GEN
    LEVEL_GEN = {}


def get_level_generalization(name, level):
    global LEVEL_GEN
    LEVEL_GEN[name] = level


def string_to_interval(column):
    new_col = []

    if isinstance(column, str):
        aux = column.replace("[", "")
        aux = aux.replace(" ", "")

        aux = aux.replace(")", "")
        aux_2 = aux.split(",")
        new_col.append(pd.Interval(left=float(aux_2[0]),
                                   right=float(aux_2[1]),
                                   closed='left'))

        return new_col[0]

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


def create_vgh(hierarchy, og_table, new_table, numeric_hie):
    vgh = {}
    numb_vgh = {}

    for i in hierarchy.keys():
        vgh_aux = {}

        for j in hierarchy[i]:
            numb_vgh[j[LEVEL_GEN[i]]] = 0

        for j in hierarchy[i]:
            numb_vgh[j[LEVEL_GEN[i]]] = numb_vgh[j[LEVEL_GEN[i]]] + 1
            numb_vgh[j[0]] = 1
            vgh_aux[j[0]] = j[LEVEL_GEN[i]]

        vgh[i] = vgh_aux

    for i in numeric_hie.keys():
        vgh_aux = {}
        ranges = string_to_interval(new_table[i].unique())

        for r in ranges:
            numb_vgh[r] = 0

        for j in og_table[i].unique():
            numb_vgh[j] = 1
            for k in ranges:
                if j in k:
                    numb_vgh[k] = numb_vgh[k] + 1
                    vgh_aux[j] = k
                    break

        vgh[i] = vgh_aux
    return [vgh, numb_vgh]


# Captures the penalty incurred when generalizing a specific attribute, by quantifying the fraction of the domain values
# that have been generalized
def generalized_information_loss(hierarchy, og_table, new_table, numeric_hie, qi):
    vgh_aux = create_vgh(hierarchy, og_table, new_table, numeric_hie)
    vgh = vgh_aux[0]
    numb_vgh = vgh_aux[1]

    n = len(qi)
    t = len(og_table)

    b = 0
    c = 0
    d = 0

    for i in qi:
        for j in range(0, t):
            # One or both parameters are strings
            if isinstance(og_table[i][j], str) and '[' not in new_table[i][j]:
                b = numb_vgh[vgh[i][og_table[i][j]]] - numb_vgh[og_table[i][j]]
                c = len(vgh[i]) - 1

                # print("Row : ", i, " number ", j, " - ", d, " + (", b, " / ", c, " )")
                d = d + (b/c)

            # One or both parameters are interval
            else:
                b = (string_to_interval(new_table[i][j]).right - 1) - string_to_interval(new_table[i][j]).left
                c = max(og_table[i]) - min(og_table[i])

                # print("Row : ", i, " number ", j, " - ", d, " + (", b, " / ", c, " )")
                d = d + (b / c)

    return (1/(t*n)) * d


# Measures how indistinguishable a record is from others, by assigning a penalty to each record, equal to the
# size of the EQ to which it belongs
def discernibility(og_table, new_table, qi):
    t = len(og_table)
    k = anonymity.k_anonymity(new_table, qi)
    eq = anonymity.utils.aux_anonymity.get_equiv_class(new_table, qi)
    a = 0

    for i in eq:
        print(i)
        if len(i) >= k:
            a = a + pow(len(i), 2)
        else:
            a = a + t * len(i)

    return a


# Measures how well the creation of the EQs approaches the best case, where each record is generalized in an EQ of k
# records
def avr_equiv_class_size(og_table, new_table, qi):
    t = len(og_table)
    k = anonymity.k_anonymity(new_table, qi)
    eq = anonymity.utils.aux_anonymity.get_equiv_class(new_table, qi)
    return t/(len(eq) * k)
