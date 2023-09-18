import unittest
import pandas as pd
import pycanon
from anonymity import tools
from anonymity.metrics.data_utility_metrics import generalized_information_loss, discernibility, avr_equiv_class_size
from anonymity.tools.utils_k_anon import utils_k_anonymity as utils


class UnitTest(unittest.TestCase):

    d = {
        "name": ["Joe", "Jill", "Sue", "Abe", "Bob", "Amy"],
        "marital stat": [
            "Separated",
            "Single",
            "Widowed",
            "Separated",
            "Widowed",
            "Single",
        ],
        "age": [29, 20, 24, 28, 25, 23],
        "ZIP code": ["32042", "32021", "32024", "32046", "32045", "32027"],
        "crime": ["Murder", "Theft", "Traffic", "Assault", "Piracy", "Indecency"],
    }
    data = pd.DataFrame(data=d)

    ID = ["name"]
    QI = ["marital stat", "age", "ZIP code"]
    SA = ["crime"]
    age_hierarchy = {"age": [0, 2, 5, 10]}
    hierarchy = {
        "marital stat": [
            ["Single", "Not married", "*"],
            ["Separated", "Not married", "*"],
            ["Divorce", "Not married", "*"],
            ["Widowed", "Not married", "*"],
            ["Married", "Married", "*"],
            ["Re-married", "Married", "*"],
        ],
        "ZIP code": [
            ["32042", "3204*", "*"],
            ["32021", "3202*", "*"],
            ["32024", "3202*", "*"],
            ["32046", "3204*", "*"],
            ["32045", "3204*", "*"],
            ["32027", "3202*", "*"],
        ],
    }

    mix_hierarchy = dict(hierarchy, **utils.create_ranges(data, age_hierarchy))

    """ Tests the datafly function for an impossible k value for the given dataset. Doesn't use suppression.
        Ensure the k returned is smaller than the input k.
    """
    def test_datafly_higher_k_no_supp(self):
        k = 10
        supp_threshold = 0
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k > pycanon.anonymity.k_anonymity(new_data, self.QI)

    """ Tests the datafly function for an impossible k value for the given dataset. Uses suppression.
        Ensure the k returned is smaller than the input k.
    """
    def test_datafly_higher_k_supp(self):
        k = 10
        supp_threshold = 2
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k > pycanon.anonymity.k_anonymity(new_data, self.QI)

    """ Tests the datafly function for a real k value for the given dataset. Doesn't use suppression.
        Ensure the k returned is equal or greater than the input k.
    """
    def test_datafly_real_k_no_supp(self):
        k = 3
        supp_threshold = 0
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k <= pycanon.anonymity.k_anonymity(new_data, self.QI)

    """ Tests the datafly function for a real k value for the given dataset. Uses suppression.
        Ensure the k returned is equal or greater than the input k.
    """
    def test_datafly_real_k_supp(self):
        k = 3
        supp_threshold = 2
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k <= pycanon.anonymity.k_anonymity(new_data, self.QI)

    """ Tests the datafly function for a small k value for the given dataset. Doesn't use suppression.
        Ensure the k returned is equal or greater than the input k.
    """
    def test_datafly_small_k_no_supp(self):
        k = 2
        supp_threshold = 0
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k <= pycanon.anonymity.k_anonymity(new_data, self.QI)

    """ Tests the datafly function for a small k value for the given dataset. Uses suppression.
        Ensure the k returned is equal or greater than the input k.
    """
    def test_datafly_small_k_supp(self):
        k = 2
        supp_threshold = 2
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k <= pycanon.anonymity.k_anonymity(new_data, self.QI)

####

    """ Tests the incognito function for a high k value for the given dataset. Doesn't use suppression.
        Ensure the k returned is lesser than the input k.
    """
    def test_incognito_higher_k_no_supp(self):
        k = 10
        supp_threshold = 0
        new_data = tools.incognito(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k > pycanon.anonymity.k_anonymity(new_data, self.QI)

    """ Tests the incognito function for a small k value for the given dataset. Uses suppression.
        Ensure the k returned is lesser than the input k.
    """
    def test_incognito_higher_k_supp(self):
        k = 10
        supp_threshold = 2
        new_data = tools.incognito(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k > pycanon.anonymity.k_anonymity(new_data, self.QI)

    """ Tests the incognito function for a realistic k value for the given dataset. Doesn't use suppression.
        Ensure the k returned is equal or greater than the input k.
    """
    def test_incognito_real_k_no_supp(self):
        k = 3
        supp_threshold = 0
        new_data = tools.incognito(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k <= pycanon.anonymity.k_anonymity(new_data, self.QI)

    """ Tests the incognito function for a realistic k value for the given dataset. Uses suppression.
        Ensure the k returned is equal or greater than the input k.
    """
    def test_incognito_real_k_supp(self):
        k = 3
        supp_threshold = 2
        new_data = tools.incognito(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k <= pycanon.anonymity.k_anonymity(new_data, self.QI)

    """ Tests the incognito function for a low k value for the given dataset. Doesn't use suppression.
        Ensure the k returned is equal or greater than the input k.
    """
    def test_incognito_small_k_no_supp(self):
        k = 1
        supp_threshold = 0
        new_data = tools.incognito(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k <= pycanon.anonymity.k_anonymity(new_data, self.QI)

    """ Tests the incognito function for a low k value for the given dataset. Uses suppression.
        Ensure the k returned is equal or greater than the input k.
    """
    def test_incognito_small_k_supp(self):
        k = 1
        supp_threshold = 2
        new_data = tools.incognito(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert k <= pycanon.anonymity.k_anonymity(new_data, self.QI)


##################################################

    """ Tests the l-diversity function for a high l value for the given dataset. Doesn't use suppression.
        Ensure the l returned is lesser than the input l. Uses the data-fly function for anonymization.
    """
    def test_l_diversity_higher_l_no_supp_datafly(self):
        k = 2
        supp_threshold = 0
        l = 10
        k_method = "data_fly"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l > pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a high l value for the given dataset. Uses suppression.
        Ensure the l returned is lesser than the input l. Uses the data-fly function for anonymization.
    """
    def test_l_diversity_higher_l_supp_datafly(self):
        k = 2
        supp_threshold = 2
        l = 10
        k_method = "data_fly"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l > pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a high l value for the given dataset. Doesn't use suppression.
        Ensure the l returned is lesser than the input l. Uses the incognito function for anonymization.
    """
    def test_l_diversity_higher_l_no_supp_incognito(self):
        k = 2
        supp_threshold = 0
        l = 10
        k_method = "incognito"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l > pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a high l value for the given dataset. Uses suppression.
        Ensure the l returned is lesser than the input l. Uses the incognito function for anonymization.
    """
    def test_l_diversity_higher_l_supp_incognito(self):
        k = 2
        supp_threshold = 2
        l = 10
        k_method = "incognito"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l > pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a realistic l value for the given dataset. Doesn't use suppression.
        Ensure the l returned is equal or greater than the input l. Uses the data-fly function for anonymization.
    """
    def test_l_diversity_real_l_no_supp_datafly(self):
        k = 2
        supp_threshold = 0
        l = 2
        k_method = "data_fly"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l <= pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a realistic l value for the given dataset. Uses suppression.
        Ensure the l returned is equal or greater than the input l. Uses the data-fly function for anonymization.
    """
    def test_l_diversity_real_l_supp_datafly(self):
        k = 2
        supp_threshold = 2
        l = 3
        k_method = "data_fly"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l >= pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a realistic l value for the given dataset. Doesn't use suppression.
        Ensure the l returned is equal or greater than the input l. Uses the incognito function for anonymization.
    """
    def test_l_diversity_real_l_no_supp_incognito(self):
        k = 3
        supp_threshold = 0
        l = 3
        k_method = "incognito"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l >= pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a realistic l value for the given dataset. Uses suppression.
        Ensure the l returned is equal or greater than the input l. Uses the incognito function for anonymization.
    """
    def test_l_diversity_real_l_supp_incognito(self):
        k = 2
        supp_threshold = 1
        l = 2
        k_method = "incognito"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l <= pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a low l value for the given dataset. Doesn't use suppression.
        Ensure the l returned is equal or greater than the input l. Uses the data-fly function for anonymization.
    """
    def test_l_diversity_small_l_no_supp_datafly(self):
        k = 3
        supp_threshold = 0
        l = 1
        k_method = "data_fly"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l <= pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a low l value for the given dataset. Uses suppression.
        Ensure the l returned is equal or greater than the input l. Uses the data-fly function for anonymization.
    """
    def test_l_diversity_small_l_supp_datafly(self):
        k = 3
        supp_threshold = 2
        l = 1
        k_method = "data_fly"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l <= pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a low l value for the given dataset. Doesn't use suppression.
        Ensure the l returned is equal or greater than the input l. Uses the incognito function for anonymization.
    """
    def test_l_diversity_small_l_no_supp_incognito(self):
        k = 3
        supp_threshold = 0
        l = 1
        k_method = "incognito"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l <= pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the l-diversity function for a low l value for the given dataset. Uses suppression.
        Ensure the l returned is equal or greater than the input l. Uses the incognito function for anonymization.
    """
    def test_l_diversity_small_l_supp_incognito(self):
        k = 3
        supp_threshold = 2
        l = 1
        k_method = "incognito"
        new_data = tools.l_diversity(
            self.data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l <= pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)


#####################################################

    """ Tests the t-closeness function for a realistic t value for the given dataset. Doesn't use suppression.
        Ensure the t returned is equal or lesser than the input t. Uses the datafly function for anonymization.
    """
    def test_t_closeness_real_t_no_supp_datafly(self):
        supp_threshold = 0
        print(self.data[self.SA[0]][0])
        t = 0.7
        k_method = "data_fly"
        new_data = tools.t_closeness(
            self.data,
            self.SA,
            self.QI,
            t,
            k_method,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert t >= pycanon.anonymity.t_closeness(new_data[1], self.QI, self.SA)

    """ Tests the t-closeness function for a realistic t value for the given dataset. Doesn't use suppression.
       Ensure the t returned is equal or lesser than the input t. Uses the incognito function for anonymization.
    """
    def test_t_closeness_real_t_no_supp_incognito(self):
        supp_threshold = 0
        t = 0.7
        k_method = "incognito"
        new_data = tools.t_closeness(
            self.data,
            self.SA,
            self.QI,
            t,
            k_method,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert t >= pycanon.anonymity.t_closeness(new_data[1], self.QI, self.SA)

    """ Tests the t-closeness function for a lower t value for the given dataset. Doesn't use suppression.
        Ensure the t returned is equal or lesser than the input t. Uses the datafly function for anonymization.
    """
    def test_t_closeness_small_t_no_supp_datafly(self):
        supp_threshold = 0
        t = 0.2
        k_method = "data_fly"
        new_data = tools.t_closeness(
            self.data,
            self.SA,
            self.QI,
            t,
            k_method,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert t >= pycanon.anonymity.t_closeness(new_data[1], self.QI, self.SA)

    """ Tests the t-closeness function for a lower t value for the given dataset. Doesn't use suppression.
        Ensure the t returned is equal or lesser than the input t. Uses the incognito function for anonymization.
    """
    def test_t_closeness_small_t_no_supp_incognito(self):
        supp_threshold = 0
        t = 0.2
        k_method = "incognito"
        new_data = tools.t_closeness(
            self.data,
            self.SA,
            self.QI,
            t,
            k_method,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert t >= pycanon.anonymity.t_closeness(new_data[1], self.QI, self.SA)

    """ Tests the t-closeness function for a realistic t value for the given dataset. Uses suppression.
        Ensure the t returned is equal or lesser than the input t.
    """
    def test_t_closeness_real_t_supp(self):
        supp_limit = 0.6
        t = 0.8
        new_data = tools.t_closeness_supp(
            self.data,
            self.SA,
            self.QI,
            t,
            supp_limit,
        )
        assert t >= pycanon.anonymity.t_closeness(new_data, self.QI, self.SA)

    """ Tests the t-closeness function for a lower t value for the given dataset. Uses suppression.
        Ensure the t returned is equal or lesser than the input t.
    """
    def test_t_closeness_small_t_supp(self):
        supp_limit = 0.2
        t = 0.2
        new_data = tools.t_closeness_supp(
            self.data,
            self.SA,
            self.QI,
            t,
            supp_limit,
        )
        assert t <= pycanon.anonymity.t_closeness(new_data, self.QI, self.SA)

#####################################################

    """ Tests the correct integration of the l-diversity method when given an already anonymized dataset. It uses the
        datafly method to anonymize the dataset before passing it to the l-diversity function. 
        Uses suppression. Ensure the l returned is equal or greater than the input l.
    """
    def test_l_diversity_datafly(self):
        k = 3
        supp_threshold = 2
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )

        l = 2
        k_method = "data_fly"
        new_data = tools.l_diversity(
            new_data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l <= pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the correct integration of the l-diversity method when given an already anonymized dataset. It uses the
        incognito method to anonymize the dataset before passing it to the l-diversity function. 
        Uses suppression. Ensure the l returned is equal or greater than the input l.
    """
    def test_l_diversity_incognito(self):
        k = 3
        supp_threshold = 2
        new_data = tools.incognito(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )

        l = 2
        k_method = "incognito"
        new_data = tools.l_diversity(
            new_data,
            self.SA,
            self.QI,
            k_method,
            l,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
            k,
        )
        assert l <= pycanon.anonymity.l_diversity(new_data[1], self.QI, self.SA)

    """ Tests the correct integration of the t-closeness method when given an already anonymized dataset. It uses the
        datafly method to anonymize the dataset before passing it to the t-closeness function. 
        Doesn't use suppression. Ensure the t returned is equal or lesser than the input t.
    """
    def test_t_closeness_datafly(self):
        k = 3
        supp_threshold = 2
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )

        t = 0.8
        k_method = "data-fly"
        new_data = tools.t_closeness(
            new_data,
            self.SA,
            self.QI,
            t,
            k_method,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert t >= pycanon.anonymity.t_closeness(new_data[1], self.QI, self.SA)

    """ Tests the correct integration of the t-closeness method when given an already anonymized dataset. It uses the
        incognito method to anonymize the dataset before passing it to the t-closeness function. 
        Doesn't use suppression. Ensure the t returned is equal or lesser than the input t.
    """
    def test_t_closeness_incognito(self):
        k = 3
        supp_threshold = 2
        new_data = tools.incognito(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )

        t = 0.8
        k_method = "incognito"
        new_data = tools.t_closeness(
            new_data,
            self.SA,
            self.QI,
            t,
            k_method,
            self.ID,
            supp_threshold,
            self.mix_hierarchy,
        )
        assert t >= new_data[0]

    """ Tests the correct integration of the t-closeness method when given an already anonymized dataset. It uses the
        datafly method to anonymize the dataset before passing it to the t-closeness function. 
        Uses suppression. Ensure the t returned is equal or lesser than the input t.
    """
    def test_t_closeness_supp(self):
        k = 3
        supp_threshold = 2
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )

        supp_limit = 0.2
        t = 0.8
        new_data = tools.t_closeness_supp(
            new_data,
            self.SA,
            self.QI,
            t,
            supp_limit,
        )
        assert t >= pycanon.anonymity.t_closeness(new_data, self.QI, self.SA)


#####################################################################################

    """ Tests the correct integration of the generalized_information_loss by checking that the value returned when 
        using two datasets, one anonymized and one raw, as inputs is greater than 0.
    """
    def test_generalized_information_loss(self):
        k = 3
        supp_threshold = 2
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )

        inf_lost = generalized_information_loss(
            self.mix_hierarchy,
            self.data,
            new_data,
            self.QI
        )

        assert inf_lost > 0

    """ Tests the correct integration of the discernibility metric by checking that the value returned when 
        using two datasets, one anonymized and one raw, as inputs is greater than 0.
    """
    def test_discernibility(self):
        k = 3
        supp_threshold = 2
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )

        disc = discernibility(
            self.data,
            new_data,
            self.QI)

        assert disc > 0

    """ Tests the correct integration of the avr_equiv_class_size metric by checking that the value returned when 
        using two datasets, one anonymized and one raw, as inputs is greater than 0.
    """
    def test_avr_equiv_class_size(self):
        k = 3
        supp_threshold = 2
        new_data = tools.data_fly(
            self.data,
            self.ID,
            self.QI,
            k,
            supp_threshold,
            self.mix_hierarchy,
        )

        avr = avr_equiv_class_size(
            self.data,
            new_data,
            self.QI)

        assert avr > 0


if __name__ == "__main__":
    unittest.main()
