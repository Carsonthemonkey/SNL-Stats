import scipy.stats as stats
import numpy as np
from analysis.load_data import load_full_data
import statsmodels.api as sm # for ANOVA table
from statsmodels.formula.api import ols # for ANOVA table
import pandas as pd

stored_durations = None
stored_scene_types = None
stored_actors = None

def test():
    data = load_full_data()
    attributes = ["view_count", "like_count", "comment_count", "mean_sentiment", "std_sentiment"]
    for attribute in attributes:
        _check_attribute_is_valid(data, attribute)
        # test_group(data, attribute, "DURATION")
        test_group(data, attribute, "SCENE TYPE")
        # test_group(data, attribute, "ACTOR")
    

def test_group(data, attribute, group):
    values = {}
    print("\n" + attribute + " by " + group)
    print("----------------------------")
    if group == "DURATION":
        values = _get_all_attribute_values_for_durations(data, attribute)
    elif group == "SCENE TYPE":
        values = _get_all_attribute_values_for_scene_types(data, attribute)
    elif group == "ACTOR":
        values = _get_all_attribute_values_for_actors(data, attribute)
    if len(values) < 2:
        print("\tNot enough groups to perform ANOVA\n")
        return
    # ANOVA test
    print("\n\tANOVA result:", end=" ")
    result = stats.f_oneway(*values.values())
    # Fit the ANOVA model
    values_for_df = [(value, key) for key, values in values.items() for value in values]
    df = pd.DataFrame(values_for_df, columns=["value", "group"])
    model = ols('value ~ group', data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    if result.pvalue < 0.01:
        print("REJECT NULL (p-value < 0.01)")
        # Tukey's HSD test
        fisher_rejects = set()
        key_list = list(values.keys())
        for i in range(len(values)):
            key1 = key_list[i]
            for j in range(len(values)):
                key2 = key_list[j]
                if i != j:
                    if fisher_lsd(values, anova_table, key1, key2, alpha=0.005):
                        # print("\t\t" + key1 + " vs " + key2 + ": REJECT NULL")
                        fisher_rejects.add(frozenset([key1, key2])) # use frozenset so that order doesn't matter
        print("\t\tFisher LSD rejects " + str(len(fisher_rejects)) + " pairs of groups")
        # print("No duplicates:", len(fisher_rejects) == len(set(map(tuple, fisher_rejects)))) # Check for duplicates
    else:
        print("FAIL TO REJECT NULL (p-value > 0.01)")
    # print("\t\tANOVA statistic=" + str(result.statistic) + "\n\t\tp-value=" + str(result.pvalue) + "\n")


# get the result for Fisher LSD test
# return true if there is significant data to reject the null hypothesis
def fisher_lsd(values, anova_table, key1, key2, alpha=0.05):
    residual_df = anova_table['df']['Residual']
    t025 = stats.t.ppf(1 - (alpha / 2), residual_df)
    residual_sum_of_squares = anova_table['sum_sq']['Residual']
    mse = residual_sum_of_squares / residual_df
    # find LSD: LSD = t.025, DFw * √MSW(1/n1 + 1/n1)
    lsd = t025 * np.sqrt(mse * ((1/len(values[key1])) + (1/len(values[key2]))))
    # find mean difference
    mean_difference = np.mean(values[key1]) - np.mean(values[key2])
    # return true if mean difference is greater than LSD (reject null hypothesis)
    return mean_difference >= lsd


def _get_all_attribute_values_for_durations(data, attribute) -> dict:
    durations = _get_durations(data)
    value_dict = {} # key is duration, value is list of attribute values
    for d in durations:
        # add only if there are more than 2 sketches of this duration
        attribute_values = _get_duration_attribute_values(data, attribute, d)
        if len(attribute_values) > 2:
            value_dict[d] = attribute_values
    return value_dict

def _get_durations(data) -> list:
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

def _get_duration_attribute_values(data, attribute, duration) -> list:
    data = sorted(data, key=lambda x: x.duration) # sort data by duration
    attribute_values = []
    for d in data:
        if d.duration <= duration and getattr(d, attribute) is not None:
            attribute_values.append(getattr(d, attribute))
        else:
            break
    return attribute_values


def _get_all_attribute_values_for_scene_types(data, attribute) -> dict:
    scene_types = _get_scene_types(data)
    value_dict = {} # key is scene type, value is list of attribute values
    for scene_type in scene_types:
        # add only if there are more than 2 sketches of this scene type
        attribute_values = _get_scene_type_attribute_values(data, attribute, scene_type)
        if len(attribute_values) > 2:
            value_dict[scene_type] = attribute_values
    return value_dict

def _get_scene_types(data) -> set:
    global stored_scene_types
    if stored_scene_types is not None:
        return stored_scene_types
    scene_types = set()
    for d in data:
        scene_types.add(d.scene_type)
    return scene_types

def _get_scene_type_attribute_values(data, attribute, scene_type) -> list:
    attribute_values = []
    for d in data:
        if d.scene_type == scene_type and getattr(d, attribute) is not None:
            attribute_values.append(getattr(d, attribute))
    return attribute_values


def _get_all_attribute_values_for_actors(data, attribute) -> dict:
    actors = _get_actors(data)
    value_dict = {} # key is actor, value is list of attribute values
    for actor in actors:
        # add only if there are more than 2 sketches of this actor
        attribute_values = _get_actor_attribute_values(data, attribute, actor)
        if len(attribute_values) > 2:
            value_dict[actor] = attribute_values
    return value_dict

def _get_actors(data) -> set:
    global stored_actors
    if stored_actors is not None:
        return stored_actors
    actors = set()
    for d in data:
        for actor in d.cast:
            if actor is not None:
                actors.add(actor)
    return actors

def _get_actor_attribute_values(data, attribute, actor) -> list:
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