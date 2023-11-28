import numpy as np
import matplotlib.pyplot as plt
from analysis.load_data import load_full_data

all_scene_types = None
all_actors = None

def draw_all_graphs_and_tables(attribute):
    # Load data
    data = load_full_data()
    # draw_boxplot_for_scene_type(data, attribute)
    # table_of_mean_and_std_by_scene_type(data, attribute)
    # bar_chart_of_mean_and_std_by_scene_type(data, attribute)
    bar_chart_of_most_extreme_actors_by_mean(data, attribute, top=False, n=15)

def draw_boxplot_for_scene_type(data, attribute):
    # check attribute is valid
    if not hasattr(data[0], attribute):
        raise AttributeError("Attribute " + attribute + " does not exist in data")
    # check is attribute is numeric
    if not np.issubdtype(type(getattr(data[0], attribute)), np.number):
        raise TypeError("Attribute " + attribute + " is not numeric")
    # find all scene types
    scene_types = get_scene_types(data)
    # box plot of views for different scene types
    boxplot_data = [
        [getattr(sketch, attribute) for sketch in data if sketch.scene_type == scene_type and getattr(sketch, attribute) is not None] for scene_type in scene_types
    ]
    boxplot_data = list(boxplot_data)
    fig, ax = plt.subplots(figsize=(12, 5)) # set size so y labels aren't cut off
    ax.boxplot(boxplot_data, vert=False, labels=scene_types)
    ax.set_title('Boxplot of ' + attribute + ' by Scene Types')
    ax.set_xlabel(attribute)
    ax.set_ylabel('Scene Types')
    plt.show()
    # save figure
    fig.savefig('graphs/' + attribute + '_by_scene_type_boxplot.png', bbox_inches='tight')

# make table of mean and std of an attribute for each scene type
def table_of_mean_and_std_by_scene_type(data, attribute):
    # check attribute is valid
    if not hasattr(data[0], attribute):
        raise AttributeError("Attribute " + attribute + " does not exist in data")
    # check is attribute is numeric
    if not np.issubdtype(type(getattr(data[0], attribute)), np.number):
        raise TypeError("Attribute " + attribute + " is not numeric")
    # calculate mean and std for each scene type
    scene_types, means, sds = get_mean_and_std_by_scene_type(data, attribute)
    # print table
    column_width = 20
    print(f"{'Scene Type':<{column_width}} {'Mean':<{column_width}} {'Standard Deviation':<{column_width}}")
    print(f"{'-'*column_width} {'-'*column_width} {'-'*column_width}")
    for st, m, sd in zip(scene_types, means, sds):
        print(f"{st:<{column_width}} {m:<{column_width}} {sd:<{column_width}}")

# make a bar chart of mean and std on an attribute for each scene type
def bar_chart_of_mean_and_std_by_scene_type(data, attribute):
    # check attribute is valid
    if not hasattr(data[0], attribute):
        raise AttributeError("Attribute " + attribute + " does not exist in data")
    # check is attribute is numeric
    if not np.issubdtype(type(getattr(data[0], attribute)), np.number):
        raise TypeError("Attribute " + attribute + " is not numeric")
    # calculate mean and std for each scene type
    scene_types, means, sds = get_mean_and_std_by_scene_type(data, attribute)
    # plot bar chart
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.bar(list(scene_types), means, yerr=sds, align='center', ecolor='black', capsize=5)
    ax.set_title('Bar Chart of Mean ' + attribute + ' by Scene Types')
    ax.set_xlabel('Scene Types')
    ax.set_ylabel(attribute)
    ax.yaxis.grid(True)
    plt.show()
    # save figure
    fig.savefig('graphs/' + attribute + '_by_scene_type_bar_chart.png', bbox_inches='tight')
    
# make a bar chart of the actors with highest/lowest mean of an attribute
def bar_chart_of_most_extreme_actors_by_mean(data, attribute, top=True, n=10):
    # check attribute is valid
    if not hasattr(data[0], attribute):
        raise AttributeError("Attribute " + attribute + " does not exist in data")
    # check is attribute is numeric
    if not np.issubdtype(type(getattr(data[0], attribute)), np.number):
        raise TypeError("Attribute " + attribute + " is not numeric")
    # find correct n actors and their means
    actors, means = get_sorted_actors_and_means(data, attribute)
    if top:
        actors = actors[:n]
        means = means[:n]
    else:
        actors = actors[-n:]
        means = means[-n:]
    # plot bar chart
    plt.barh(list(actors), means)
    plt.title('Bar Chart of Mean ' + attribute + ' by Actors')
    plt.xlabel(attribute)
    plt.ylabel('Actors')
    if top:  # put in ascending order
        plt.gca().invert_yaxis() 
    plt.tight_layout()
    plt.show()
    # save figure
    plt.savefig('graphs/' + attribute + '_by_actor_bar_chart.png', bbox_inches='tight')


def get_scene_types(data):
    global all_scene_types
    if all_scene_types is None:
        all_scene_types = set(sketch.scene_type for sketch in data if sketch.scene_type is not None)
    return all_scene_types

def get_actors(data):
    global all_actors
    if all_actors is None:
        all_actors = set()
        for sketch in data:
            for actor in sketch.cast:
                if actor is not None:
                    all_actors.add(actor)
    return all_actors

def get_mean_and_std_by_scene_type(data, attribute):
    means = []
    sds = []
    scene_types = get_scene_types(data)
    for scene_type in scene_types:
        values = [getattr(sketch, attribute) for sketch in data if sketch.scene_type == scene_type and getattr(sketch, attribute) is not None]
        means.append(np.mean(values))
        sds.append(np.std(values))
    return scene_types, means, sds

def get_sorted_actors_and_means(data, attribute):
    actors = get_actors(data)
    means = []
    for actor in actors:
        values = [getattr(sketch, attribute) for sketch in data if actor in sketch.cast and getattr(sketch, attribute) is not None]
        means.append(np.mean(values))
    return zip(*sorted(zip(actors, means), key=lambda x: x[1], reverse=True))

if __name__ == '__main__':
    draw_all_graphs_and_tables("view_count")