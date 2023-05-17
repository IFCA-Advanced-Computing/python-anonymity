import copy
import utils
import incognito
import pandas as pd
import data_fly as df
from pycanon import anonymity
import data_utility_metrics as dum
from l_diversity import apply_l_diversity, apply_l_diversity_v2

file_name = "hospital_extended.csv"
ID = ["name", "religion"]
QI = ["age", "gender", "city"]
SA = ["disease"]
age_hierarchy = {"age": [0, 2, 4, 8, 10]}
city_hierarchy = {"city": [["Tamil Nadu", "India north", "*"],
                           ["Kerala", "India south", "*"],
                           ["Karnataka", "India north", "*"],
                           ["?", "Unknown", "*"]],
                  "gender": [["Female", "*"],
                             ["Male", "*"]],
                  "disease": [["Cancer", "Cancer"],
                              ["Viral infection", "Other"],
                              ["TB", "Other"],
                              ["No illness", "No illness"],
                              ["Heart-related", "Other"]]
                  }

#  ----------------------------------------------TEST FOR DATA_FLY-------------------------------------------------

# data = pd.read_csv(file_name)
# mix_hierarchy = dict(city_hierarchy, **utils.create_ranges(data, age_hierarchy))
# new_data = df.data_fly(data, ID, QI, 7, 6, mix_hierarchy)
# print("\n", new_data)
# print("\n", "K-anonymity: ", anonymity.k_anonymity(new_data, QI))

#  -------------------------------------TEST FOR DATA UTILITY METRICS ----------------------------------------------

d = {'name': ["Joe", "Jill", "Sue", "Abe", "Bob", "Amy"],
     'marital stat': ["Separated", "Single", "Widowed", "Separated", "Widowed", "Single"],
     'age': [29, 20, 24, 28, 25, 23],
     'ZIP code': ["32042", "32021", "32024", "32046", "32045", "32027"],
     'crime': ["Murder", "Theft", "Traffic", "Assault", "Piracy", "Indecency"]
     }
data = pd.DataFrame(data=d)

ID = ["name"]
QI = ["marital stat", "age", "ZIP code"]
SA = ["crime"]
age_hierarchy = {"age": [0, 2, 5, 10]}
hierarchy = {"marital stat": [["Single", "Not married", "*"],
                              ["Separated", "Not married", "*"],
                              ["Divorce", "Not married", "*"],
                              ["Widowed", "Not married", "*"],
                              ["Married", "Married", "*"],
                              ["Re-married", "Married", "*"]],
             "ZIP code": [["32042", "3204*", "*"],
                          ["32021", "3202*", "*"],
                          ["32024", "3202*", "*"],
                          ["32046", "3204*", "*"],
                          ["32045", "3204*", "*"],
                          ["32027", "3202*", "*"]]
             }

print('RAW DATA')
print(data)
print(f"QI: {QI}")
mix_hierarchy = dict(hierarchy, **utils.create_ranges(copy.deepcopy(data), age_hierarchy))
print('DATA-FLY')
new_data = df.data_fly(data, ID, copy.copy(QI), 5, 0, mix_hierarchy)
print("\n", new_data)
print(f"QI: {QI}")
print("\n", "K-anonymity: ", anonymity.k_anonymity(new_data, QI))
print("Generalized Information Loss: ",
      dum.generalized_information_loss(mix_hierarchy, data,
                                       new_data, QI))
print("Discernibility Metric: ",
      dum.discernibility(data, new_data, QI))
print("Average Equivalence Class Size Metric: ",
      dum.avr_equiv_class_size(data, new_data, QI))

# TODO La metrica de GIL no va bien, ya que sale el mismo resultado en ambos casos
new_data = incognito.incognito(data, mix_hierarchy, 3, copy.copy(QI), 0, ID)
print("RAW DATA")
print("\n", data)
print('INCOGNITO')
print(f"QI: {QI}")
print("\n", new_data)
print("\n", "K-anonymity: ",
      anonymity.k_anonymity(new_data, QI))
print("Generalized Information Loss: ",
      dum.generalized_information_loss(mix_hierarchy, data, new_data, QI))
print("Discernibility Metric: ",
      dum.discernibility(data, new_data, QI))
print("Average Equivalence Class Size Metric: ",
      dum.avr_equiv_class_size(data, new_data, QI))

sa_hierarchy = {"crime": [["Murder", "Violent crime", "*"],
                          ["Theft", "Non violent crime", "*"],
                          ["Traffic", "Non violent crime", "*"],
                          ["Assault", "Violent crime", "*"],
                          ["Piracy", "Non violent crime", "*"],
                          ["Indecency", "Non violent crime", "*"]]
                }
print(apply_l_diversity_v2(new_data, SA, QI, "data_fly", 2, ID, sa_hierarchy))
