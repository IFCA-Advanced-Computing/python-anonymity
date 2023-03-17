from pycanon import anonymity

import data_fly as df
import pandas as pd
import data_utility_metrics as dum

file_name = "hospital_extended.csv"
ID = ["name"]
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

data = pd.read_csv(file_name)

new_data = df.data_fly(data, ID, QI, 7, 6, age_hierarchy, city_hierarchy)
print("\n", new_data)
print("\n", "K-anonymity: ", anonymity.k_anonymity(new_data, QI))

#  ----------------------------TEST FOR DATA UTILITY METRICS -------------------------------------

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
age_hierarchy = {"age": [0, 5, 10]}
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

new_data = df.data_fly(data, ID, QI, 3, 0, age_hierarchy, hierarchy)
print("\n", new_data)
print("Generalized Information Loss: ", dum.generalized_information_loss(hierarchy, data, new_data, age_hierarchy, QI))
print("Discernibility Metric: ", dum.discernibility(data, new_data, QI))
print("Average Equivalence Class Size Metric: ", dum.avr_equiv_class_size(data, new_data, QI))
