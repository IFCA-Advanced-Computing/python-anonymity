# PYTHON LIBRARY FOR ANONYMIZATION

This library supports the application of three classical anonymization techniques for tabular data: k-anonymity, l-diversity and t-closeness. 


**Installation**

> We recommend to use Python3 with  virtualenv:
> 
```
> virtualenv .venv -p python3
> source .venv/bin/activate
```


Then run the following command to install the library and all its
requirements:

`pip install python-anonymity`


**Documentation**

> The python-anonymity documentation is hosted on Read the Docs.


**Getting started**
> Example using the crime synthetic dataset:
> 
```
> import pandas as pd
> import pycanon
> from anonymity import tools
> from anonymity.tools.utils_k_anon import utils_k_anonymity as utils
> 
> d = {
>         "name": ["Joe", "Jill", "Sue", "Abe", "Bob", "Amy"],
>         "marital stat": [
>             "Separated",
>             "Single",
>             "Widowed",
>             "Separated",
>             "Widowed",
>             "Single",
>         ],
>         "age": [29, 20, 24, 28, 25, 23],
>         "ZIP code": ["32042", "32021", "32024", "32046", "32045", "32027"],
>         "crime": ["Murder", "Theft", "Traffic", "Assault", "Piracy", "Indecency"],
>     }
>     data = pd.DataFrame(data=d)
> 
>     ID = ["name"]
>     QI = ["marital stat", "age", "ZIP code"]
>     SA = ["crime"]
>     age_hierarchy = {"age": [0, 2, 5, 10]}
>     hierarchy = {
>         "marital stat": [
>             ["Single", "Not married", "*"],
>             ["Separated", "Not married", "*"],
>             ["Divorce", "Not married", "*"],
>             ["Widowed", "Not married", "*"],
>             ["Married", "Married", "*"],
>             ["Re-married", "Married", "*"],
>         ],
>         "ZIP code": [
>             ["32042", "3204*", "*"],
>             ["32021", "3202*", "*"],
>             ["32024", "3202*", "*"],
>             ["32046", "3204*", "*"],
>             ["32045", "3204*", "*"],
>             ["32027", "3202*", "*"],
>         ],
>     }
> 
>     mix_hierarchy = dict(hierarchy, **utils.create_ranges(data, age_hierarchy))

>     k = 2
>     supp_threshold = 0
>     new_data = tools.data_fly(data, ID, QI, k, supp_threshold, self.mix_hierarchy)
> 
```


License: [Apache 2.0.](https://gitlab.ifca.es/privacy-security/python_library_anonymization/-/blob/main/LICENSE?ref_type=heads)

**Note: the library is under heavy production, only for testing purposes.**


