import scipy.stats as stats
import numpy as np
from analysis.load_data import load_full_data

stored_durations = None

def test():
    data = load_full_data()
    attributes = ["view_count", "like_count", "comment_count", "mean_sentiment", "std_sentiment"]
    print("DURATION")
    for attribute in attributes:
        print("ANOVA for " + attribute + " by duration")
        print("----------------------------------------")
        test_attribute_values_by_duration(data, attribute)
    print("SCENE TYPE")
    for attribute in attributes:
        print("ANOVA for " + attribute + " by scene type")
        print("----------------------------------------")
        test_attribute_values_by_scene_type(data, attribute)
    

def test_attribute_values_by_duration(data, attribute="view_count"):
    vals_by_duration = _get_attribute_values_by_duration(data, attribute)
    # print("Printing length of vals in vals_by_duration...")
    # for vals in vals_by_duration:
    #     print(len(vals))
    # remove first list of vals from vals_by_duration (because it only have one val)
    for i in range(3):
        print("ANOVA for all groups after duration group " + str(i+1))
        vals_by_duration = vals_by_duration[i:]
        print(stats.f_oneway(*vals_by_duration))
        print(stats.f_oneway(*vals_by_duration).pvalue)


def test_attribute_values_by_scene_type(data, attribute="view_count"):
    vals_by_scene_type = _get_attribute_values_by_scene_type(data, attribute)
    # print("Printing length of vals in vals_by_scene_type...")
    # for vals in vals_by_scene_type:
    #     print(len(vals))
    print(stats.f_oneway(*vals_by_scene_type))
    print(stats.f_oneway(*vals_by_scene_type).pvalue)


def _get_attribute_values_by_duration(data, attribute):
    _check_attribute_is_valid(data, attribute)
    # get durations
    durations = _get_durations(data)
    # get attribute values for each duration
    attribute_values_by_duration = []
    for d in durations:
        attribute_values_by_duration.append(_get_duration_attribute_values(data, attribute, d))
    return attribute_values_by_duration

def _get_durations(data):
    global stored_durations
    if stored_durations is not None:
        return stored_durations
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

def _get_duration_attribute_values(data, attribute, duration):
    data = sorted(data, key=lambda x: x.duration) # sort data by duration
    attribute_values = []
    for d in data:
        if d.duration <= duration and getattr(d, attribute) is not None:
            attribute_values.append(getattr(d, attribute))
        else:
            break
    return attribute_values


def _get_attribute_values_by_scene_type(data, attribute):
    _check_attribute_is_valid(data, attribute)
    # get scene types
    scene_types = _get_scene_types(data)
    # get attribute values for each scene type
    attribute_values_by_scene_type = []
    for scene_type in scene_types:
        attribute_values_by_scene_type.append(_get_scene_type_attribute_values(data, attribute, scene_type))
    return attribute_values_by_scene_type

def _get_scene_types(data):
    scene_types = set()
    for d in data:
        scene_types.add(d.scene_type)
    return scene_types

def _get_scene_type_attribute_values(data, attribute, scene_type):
    attribute_values = []
    for d in data:
        if d.scene_type == scene_type and getattr(d, attribute) is not None:
            attribute_values.append(getattr(d, attribute))
    return attribute_values


def _check_attribute_is_valid(data, attribute):
    # check attribute is valid
    if not hasattr(data[0], attribute):
        raise AttributeError("Attribute " + attribute + " does not exist in data")
    # check is attribute is numeric
    if not np.issubdtype(type(getattr(data[0], attribute)), np.number):
        raise TypeError("Attribute " + attribute + " is not numeric")


if __name__ == "__main__":
    test()