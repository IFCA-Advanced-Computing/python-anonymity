import pandas as pd
from numpy import inf
from numpy.core.defchararray import isdigit
from pycanon import anonymity, report
from collections import Counter

FILE_NAME = "adult.csv"
QI = ["age", "education", "occupation", "relationship", "sex", "native-country"]
SA = ["salary-class"]
DATA = pd.read_csv(FILE_NAME)

# Calculate k for k-anonymity:
#k = anonymity.k_anonymity(DATA, QI)

#report.print_report(DATA, QI, SA)

def Generalization(column):
    # Generalization of numbers
    if(isinstance(column[0][0], int) or isinstance(column[0][0], float) or
            isinstance(column[0][0], complex)):
        print("numb")

        min = inf
        max = 0

        for i in column:
            if i[0] > max:
                max = i[0]
            if i[0] < min:
                min = i[0]

        # print("Min: ", min)
        # print("Max: ", max)

        while min % 5 != 0 or max % 5 !=0:
            if min % 5 != 0:
                min = min - 1
            if max % 5 != 0:
                max = max + 1

        # print("Min: ", min)
        # print("Max: ", max)

        step = int((max-min) / 5)
        # print(step)
        ranges = []
        for i in range(0, step):
            # ranges.append([min + 5*i, min + 5*(i+1)])
            ranges.append([min + 5*i, (min + 5*(i+1)) - 1])
        # print(ranges)

        for i in range(1, len(column)):
            for j, (start, end) in enumerate(ranges, start=1):
                if column[i][0] in range(start, end + 1):
                    column[i][0] = column[i][0], ranges[j - 1]

        return column

    # Generalization of strings
    elif(isinstance(column[0][0], str)):
        print("string")

    # Generalization of ranges
    else:
        print("range")

    return column

def DataFly(table, QI, SA, k, suppThreshold):
    currentSupp = 0
    lenTable = len(table)

    freqCs = anonymity.k_anonymity(table, QI)
    if (freqCs >= k):
        return table

    if (freqCs <= suppThreshold):
        # Suppress tables
        return table

    else:
        uniqueValues = []
        numberOfOccurances = 0
        index = ''

        # Calculate the attribute with more unique values
        for i in QI:
            if(numberOfOccurances < len(uniqueValues)):
                index = i
                uniqueValues = table[i].keys()  # equals to list(set(words))
                numberOfOccurances = len(uniqueValues)
                #table[i].values()  # counts the elements' frequency

        new_ind = Generalization(table[index])
        new_ind = pd.DataFrame({'index': new_ind})
        table[index] = new_ind

    return table


print(type(type(DATA[["age"]].values.tolist()[0][0])))

Generalization(DATA[[" workclass"]].values.tolist())
Generalization(DATA[["age"]].values.tolist())

