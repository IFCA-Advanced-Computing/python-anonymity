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
    for i in column:
        aux = i.replace("[", "")
        aux = aux.replace(" ", "")

        if ')' in i:
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

    column = new_col
    return column


def create_vgh(hierarchy, og_table, new_table, numeric_hie):
    vgh = {}
    numb_vgh = {}

    for i in hierarchy.keys():
        vgh_aux = {}
        abstract = {}

        # TODO Mirar si esto sirve o no, porque igual la abstracción no hace falta
        for k in range(0, len(hierarchy[i])):
            abstract[hierarchy[i][k][0]] = k

        # print(abstract)
        for j in hierarchy[i]:
            numb_vgh[j[LEVEL_GEN[i]]] = 0

        for j in hierarchy[i]:
            numb_vgh[j[0]] = 0

        for j in hierarchy[i]:
            numb_vgh[j[LEVEL_GEN[i]]] = numb_vgh[j[LEVEL_GEN[i]]] + 1
            numb_vgh[j[0]] = numb_vgh[j[0]] + 1
            vgh_aux[j[0]] = j[LEVEL_GEN[i]]

        vgh[i] = vgh_aux

    for i in numeric_hie.keys():
        vgh_aux = {}
        ranges = string_to_interval(new_table[i].unique())

        # TODO Añadir los rangos y las edades con su numero de apariciones al diccionario vgh_aux

        for j in og_table[i].unique():
            for k in ranges:
                if j in k:
                    vgh_aux[j] = k

        vgh[i] = vgh_aux
    return [vgh, numb_vgh]


# TODO NOT WORKING AT ALL, PLS DO NOT TRY TO USE IT YET
def generalized_information_loss(hierarchy, og_table, new_table, numeric_hie, QI):
    vgh_aux = create_vgh(hierarchy, og_table, new_table, numeric_hie)
    vgh = vgh_aux[0]
    numb_vgh = vgh_aux[1]

    # print(numb_vgh)
    # print(vgh)

    n = len(QI)
    t = len(og_table)

    for i in QI:
        for j in range(0, t - 1):
            # numb_vgh[vgh[i][og_table[i][j]]] - numb_vgh[new_table[i][j]]
            print(numb_vgh[vgh[i][og_table[i][j]]] - numb_vgh[new_table[i][j]])
    return 1/(t*n)


# TODO NOT WORKING AT ALL, PLS DO NOT TRY TO USE IT YET
def number_of_missing_values(original_table, modifed_table, QI):
    n = QI
    t = len(original_table[0])

    a = 1 / (t * n)
    b = 0
    c = 0
    d = 0

    for i in n:
        for j in range(1, t):
            # b = b + Valor más alto de ese intervalo en la jerarquia + valor más bajo de ese intervalo en la jerarquia
            b = b
            # c = # Valor mas alto de la tabla inicial para esa col - Valor más bajo de la tabla incial para esa col
            c = c
            d = b / c

    return a * d


# TODO Fix this function, as 't' is the number of recods but I don't get what
#  that refers to exactly.
def discernibility(new_table, qi, t):
    k = anonymity.k_anonymity(new_table, qi)
    eq = anonymity.utils.aux_anonymity.get_equiv_class(new_table, qi)

    a = 0
    for i in eq:
        if i >= k:
            a = a + i ^ 2
        else:
            a = a + t * i

    return a


# TODO Fix this function, as 't' is the number of recods but I don't get what
#  that refers to exactly.
def avr_equiv_class_size(new_table, qi, t):
    k = anonymity.k_anonymity(new_table, qi)
    eq = anonymity.utils.aux_anonymity.get_equiv_class(new_table, qi)
    return t/(len(eq) * k)
