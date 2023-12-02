import scipy.stats as stats
import numpy as np
from analysis.load_data import load_full_data

def test():
    # print(stats.ttest_ind([1,2,3], [4,5,6])) # t-test example
    # print(stats.f_oneway([1,2,3], [4,5,6])) # ANOVA example (one-way)
    data = load_full_data()
    attributes = ["view_count", "like_count", "comment_count", "mean_sentiment", "std_sentiment"]
    for attribute in attributes:
        print("ANOVA for " + attribute + " by duration")
        print("----------------------------------------")
        test_attribute_values_by_duration(data, attribute)
    

def test_attribute_values_by_duration(data, attribute="view_count"):
    vals_by_duration = get_attribute_values_by_duration(data, attribute)
    # print length of arrays in vals_by_duration
    print("Printing length of vals in vals_by_duration...")
    for vals in vals_by_duration:
        print(len(vals))
    # remove first list of vals from vals_by_duration (because it only have one val)
    for i in range(3):
        print("ANOVA for all groups after duration group " + str(i+1))
        vals_by_duration = vals_by_duration[i:]
        print(stats.f_oneway(*vals_by_duration))
        print(stats.f_oneway(*vals_by_duration).pvalue)
    # print(stats.f_oneway(*get_attribute_values_by_duration(data, "view_count")))

# get array of attribute values grouped by duration
def get_attribute_values_by_duration(data, attribute):
    # check attribute is valid
    if not hasattr(data[0], attribute):
        raise AttributeError("Attribute " + attribute + " does not exist in data")
    # check is attribute is numeric
    if not np.issubdtype(type(getattr(data[0], attribute)), np.number):
        raise TypeError("Attribute " + attribute + " is not numeric")
    # get durations
    durations = get_durations(data)
    # get attribute values for each duration
    attribute_values_by_duration = []
    for d in durations:
        attribute_values_by_duration.append(get_attribute_values(data, attribute, d))
    return attribute_values_by_duration

def get_durations(data):
    durations = []
    for d in data:
        durations.append(d.duration)
    # find max and min duration
    durations = sorted(durations)
    min_duration = durations[0]
    max_duration = durations[-1]
    # create list of 5 groups of durations
    durations = []
    for i in range(5):
        durations.append(min_duration + i*(max_duration-min_duration)/4)
    return durations

def get_attribute_values(data, attribute, duration):
    data = sorted(data, key=lambda x: x.duration) # sort data by duration
    attribute_values = []
    for d in data:
        if d.duration <= duration and getattr(d, attribute) is not None:
            attribute_values.append(getattr(d, attribute))
        else:
            break
    return attribute_values

if __name__ == "__main__":
    test()