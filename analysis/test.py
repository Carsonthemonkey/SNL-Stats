import scipy.stats as stats
import numpy as np
from analysis.load_data import load_full_data

stored_durations = None
stored_scene_types = None
stored_actors = None

def test():
    data = load_full_data()
    attributes = ["view_count", "like_count", "comment_count", "mean_sentiment", "std_sentiment"]
    for attribute in attributes:
        _check_attribute_is_valid(data, attribute)
        test_group(data, attribute, "DURATION")
        test_group(data, attribute, "SCENE TYPE")
        test_group(data, attribute, "ACTOR")
    

def test_group(data, attribute, group):
    values = {}
    print("\n" + attribute + " by " + group)
    print("----------------------------")
    if group == "DURATION":
        values = _get_attribute_values_by_duration(data, attribute)
    elif group == "SCENE TYPE":
        values = _get_attribute_values_by_scene_type(data, attribute)
    elif group == "ACTOR":
        values = _get_attribute_values_by_actor(data, attribute)
    values = test_normality(values)
    if len(values) < 2:
        print("\tNot enough groups to perform ANOVA\n")
        return
    print("\n\tANOVA result:", end=" ")
    result = stats.f_oneway(*values.values())
    if result.pvalue < 0.05:
        print("REJECT NULL (p-value < 0.05)")
    else:
        print("FAIL TO REJECT NULL (p-value > 0.05)")
    print("\t\tstatistic=" + str(result.statistic) + "\n\t\tp-value=" + str(result.pvalue) + "\n")


def test_normality(values) -> dict:
    normal_values = {}
    removed_count = 0
    for key in values:
        vals = values[key]
        if len(vals) > 5:
            if stats.shapiro(vals).pvalue > 0.05:
                # print(\tstats.shapiro(vals).pvalue)
                normal_values[key] = vals
            else:
            #     print("\tp-value < 0.05")
                removed_count += 1
    print("\tNumber of roughly normal value groups: " + str(len(normal_values)) + "\n")
    if removed_count > 0:
        print("\tNumber of groups removed due to non-normality: " + str(removed_count) + "\n")
    return normal_values


def _get_attribute_values_by_duration(data, attribute) -> dict:
    durations = _get_durations(data)
    value_dict = {} # key is duration, value is list of attribute values
    for d in durations:
        value_dict[d] = _get_duration_attribute_values(data, attribute, d)
    return value_dict

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


def _get_attribute_values_by_scene_type(data, attribute) -> dict:
    scene_types = _get_scene_types(data)
    value_dict = {} # key is scene type, value is list of attribute values
    for scene_type in scene_types:
        value_dict[scene_type] = _get_scene_type_attribute_values(data, attribute, scene_type)
    return value_dict

def _get_scene_types(data):
    global stored_scene_types
    if stored_scene_types is not None:
        return stored_scene_types
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


def _get_attribute_values_by_actor(data, attribute) -> dict:
    actors = _get_actors(data)
    value_dict = {} # key is actor, value is list of attribute values
    for actor in actors:
        value_dict[actor] = _get_actor_attribute_values(data, attribute, actor)
    return value_dict

def _get_actors(data):
    global stored_actors
    if stored_actors is not None:
        return stored_actors
    actors = set()
    for d in data:
        for actor in d.cast:
            if actor is not None:
                actors.add(actor)
    return actors

def _get_actor_attribute_values(data, attribute, actor):
    attribute_values = []
    for d in data:
        if actor in d.cast and getattr(d, attribute) is not None:
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