from pycanon import anonymity

import data_fly as df
import pandas as pd

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

data = pd.read_csv(file_name)

# TODO Check if it's correct for the data_fly algorithm to end when it can
# TODO suppress tables, even though we do not check if it has the correct k.
new_data = df.data_fly(data, ID, QI, 7, 6, age_hierarchy, city_hierarchy)
print("\n", new_data)
print("\n", "K-anonymity: ", anonymity.k_anonymity(new_data, QI))
