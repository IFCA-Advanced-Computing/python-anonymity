import pandas as pd
import pycanon.anonymity
from anonymity import tools
from anonymity.tools import utils_k_anon


class TestAdult:
    qi = ["age", "education", "occupation", "relationship", "sex", "native-country"]
    sa = ["salary-class"]
    ident = []
    supp_threshold = 1
    hierarchies = ...
    file_name = "./data/adult.csv"
    data = pd.read_csv(file_name)
    k = 5
    l = 2
    t = 0.5

    def test_k_anon_datafly(self):
        new_data = tools.data_fly(
            self.data,
            self.ident,
            self.qi,
            self.k,
            self.supp_threshold,
            self.hierarchies,
        )
        assert self.k >= pycanon.anonymity.k_anonymity(new_data, self.qi)

    def test_k_anon_incognito(self):
        new_data = tools.incognito(
            self.data,
            self.ident,
            self.qi,
            self.k,
            self.supp_threshold,
            self.hierarchies,
        )
        assert self.k >= pycanon.anonymity.k_anonymity(new_data, self.qi)

    def test_l_div_datafly(self):
        k_method = "data_fly"
        new_data = tools.l_diversity(
            self.data,
            self.sa,
            self.qi,
            k_method,
            self.l,
            self.ident,
            self.supp_threshold,
            self.hierarchies,
            self.k,
        )
        assert self.l >= pycanon.anonymity.l_diversity(new_data, self.qi, self.sa)

    def test_l_div_incognito(self):
        k_method = "incognito"
        new_data = tools.l_diversity(
            self.data,
            self.sa,
            self.qi,
            k_method,
            self.l,
            self.ident,
            self.supp_threshold,
            self.hierarchies,
            self.k,
        )
        assert self.l >= pycanon.anonymity.l_diversity(new_data, self.qi, self.sa)

    def test_t_clos_datafly(self):
        k_method = "data_fly"
        new_data = tools.t_closeness(
            self.data,
            self.sa,
            self.qi,
            self.t,
            k_method,
            self.ident,
            self.supp_threshold,
            self.hierarchies,
        )
        assert self.t >= pycanon.anonymity.t_closeness(new_data, self.qi, self.sa)

    def test_t_clos_incognito(self):
        k_method = "incognito"
        new_data = tools.t_closeness(
            self.data,
            self.sa,
            self.qi,
            self.t,
            k_method,
            self.ident,
            self.supp_threshold,
            self.hierarchies,
        )
        assert self.t >= pycanon.anonymity.t_closeness(new_data, self.qi, self.sa)


class TestHospital:
    file_name = "./data/hospital_extended.csv"
    data = pd.read_csv(file_name)
    ident = ["name", "religion"]
    qi = ["age", "gender", "city"]
    sa = ["disease"]
    age_hierarchy = {"age": [0, 2, 4, 8, 10]}
    city_hierarchy = {
        "city": [
            ["Tamil Nadu", "India north", "*"],
            ["Kerala", "India south", "*"],
            ["Karnataka", "India north", "*"],
            ["?", "Unknown", "*"],
        ],
        "gender": [["Female", "*"], ["Male", "*"]],
        "disease": [
            ["Cancer", "Cancer"],
            ["Viral infection", "Other"],
            ["TB", "Other"],
            ["No illness", "No illness"],
            ["Heart-related", "Other"],
        ],
    }
    hierarchies = dict(city_hierarchy, utils_k_anon.create_ranges(data, age_hierarchy))
    supp_threshold = 1
    k = 2
    l = 2
    t = 0.7

    def test_k_anon_datafly(self):
        new_data = tools.data_fly(
            self.data,
            self.ident,
            self.qi,
            self.k,
            self.supp_threshold,
            self.hierarchies,
        )
        assert self.k >= pycanon.anonymity.k_anonymity(new_data, self.qi)

    def test_k_anon_incognito(self):
        new_data = tools.incognito(
            self.data,
            self.ident,
            self.qi,
            self.k,
            self.supp_threshold,
            self.hierarchies,
        )
        assert self.k >= pycanon.anonymity.k_anonymity(new_data, self.qi)

    def test_l_div_datafly(self):
        k_method = "data_fly"
        new_data = tools.l_diversity(
            self.data,
            self.sa,
            self.qi,
            k_method,
            self.l,
            self.ident,
            self.supp_threshold,
            self.hierarchies,
            self.k,
        )
        assert self.l >= pycanon.anonymity.l_diversity(new_data, self.qi, self.sa)

    def test_l_div_incognito(self):
        k_method = "incognito"
        new_data = tools.l_diversity(
            self.data,
            self.sa,
            self.qi,
            k_method,
            self.l,
            self.ident,
            self.supp_threshold,
            self.hierarchies,
            self.k,
        )
        assert self.l >= pycanon.anonymity.l_diversity(new_data, self.qi, self.sa)

    def test_t_clos_datafly(self):
        k_method = "data_fly"
        new_data = tools.t_closeness(
            self.data,
            self.sa,
            self.qi,
            self.t,
            k_method,
            self.ident,
            self.supp_threshold,
            self.hierarchies,
        )
        assert self.t >= pycanon.anonymity.t_closeness(new_data, self.qi, self.sa)

    def test_t_clos_incognito(self):
        k_method = "incognito"
        new_data = tools.t_closeness(
            self.data,
            self.sa,
            self.qi,
            self.t,
            k_method,
            self.ident,
            self.supp_threshold,
            self.hierarchies,
        )
        assert self.t >= pycanon.anonymity.t_closeness(new_data, self.qi, self.sa)
