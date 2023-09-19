import pandas as pd
import pycanon.anonymity
from anonymity import tools
from anonymity.tools.utils_k_anon import utils_k_anonymity as utils


class TestAdult:
    qi = ["age", "education", "occupation", "marital-status", "race", "sex"]
    sa = ["salary-class"]
    ident = [
        "workclass",
        "fnlwgt",
        "education-num",
        "relationship",
        "capital-gain",
        "capital-loss",
        "hours-per-week",
        "native-country",
    ]
    supp_threshold = 1
    age_hierarchy = {"age": [0, 2, 5, 10]}
    hierarchy = {
        "education": [
            ["Bachelors", "Undergraduate", "Higher education", "*"],
            ["Some-college", "Undergraduate", "Higher education", "*"],
            ["11th", "High School", "Secondary education", "*"],
            ["HS-grad", "High School", "Secondary education", "*"],
            ["Prof-school", "Professional Education", "Higher education", "*"],
            ["Assoc-acdm", "Professional Education", "Higher education", "*"],
            ["Assoc-voc", "Professional Education", "Higher education", "*"],
            ["9th", "High School", "Secondary education", "*"],
            ["7th-8th", "High School", "Secondary education", "*"],
            ["12th", "High School", "Secondary education", "*"],
            ["Masters", "Graduate", "Higher education", "*"],
            ["1st-4th", "Primary School", "Primary education", "*"],
            ["10th", "High School", "Secondary education", "*"],
            ["Doctorate", "Graduate", "Higher education", "*"],
            ["5th-6th", "Primary School", "Primary education", "*"],
            ["Preschool", "Primary School", "Primary education", "*"],
        ],
        "marital-status": [
            ["Married-civ-spouse", "spouse present", "*"],
            ["Divorced", "spouse not present", "*"],
            ["Never-married", "spouse not present", "*"],
            ["Separated", "spouse not present", "*"],
            ["Widowed", "spouse not present", "*"],
            ["Married-spouse-absent", "spouse not present", "*"],
            ["Married-AF-spouse", "spouse present", "*"],
        ],
        "occupation": [
            ["Tech-support", "Technical", "*"],
            ["Craft-repair", "Technical", "*"],
            ["Other-service", "Other", "*"],
            ["Sales", "Nontechnical", "*"],
            ["Exec-managerial", "Nontechnical", "*"],
            ["Prof-specialty", "Technical", "*"],
            ["Handlers-cleaners", "Nontechnical", "*"],
            ["Machine-op-inspct", "Technical", "*"],
            ["Adm-clerical", "Other", "*"],
            ["Farming-fishing", "Other", "*"],
            ["Transport-moving", "Other", "*"],
            ["Priv-house-serv", "Other", "*"],
            ["Protective-serv", "Other", "*"],
            ["Armed-Forces", "Other", "*"],
        ],
        "marital-status": [
            ["White", "*"],
            ["Asian-Pac-Islander", "*"],
            ["Amer-Indian-Eskimo", "*"],
            ["Other", "*"],
            ["Black", "*"],
        ],
        "sex": [
            ["Male", "*"],
            ["Female", "*"],
        ],
        "salary-class": [
            [">50K", "*"],
            ["<=50K", "*"],
        ],
    }

    file_name = "./data/adult.csv"
    data = pd.read_csv(file_name)

    hierarchies = dict(hierarchy, **utils.create_ranges(data, age_hierarchy))
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
    hierarchies = dict(city_hierarchy, **utils.create_ranges(data, age_hierarchy))
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
