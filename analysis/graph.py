import numpy as np
import matplotlib.pyplot as plt
from analysis.load_data import load_full_data


def draw_all_graphs_and_tables(attribute):
    # Load data
    data = load_full_data()
    # draw_boxplot_for_scene_type(data, attribute)
    # table_of_mean_and_std_by_scene_type(data, attribute)
    # bar_chart_of_mean_and_std_by_scene_type(data, attribute)
    bar_chart_of_top_ten_actors_by_mean(data, attribute)

def draw_boxplot_for_scene_type(data, attribute):
    # check attribute is valid
    if not hasattr(data[0], attribute):
        raise AttributeError("Attribute " + attribute + " does not exist in data")
    # check is attribute is numeric
    if not np.issubdtype(type(getattr(data[0], attribute)), np.number):
        raise TypeError("Attribute " + attribute + " is not numeric")
    # find all scene types
    scene_types = set(sketch.scene_type for sketch in data if sketch.scene_type is not None)
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
    means = []
    sds = []
    scene_types = set(sketch.scene_type for sketch in data if sketch.scene_type is not None)
    for scene_type in scene_types:
        values = [getattr(sketch, attribute) for sketch in data if sketch.scene_type == scene_type and getattr(sketch, attribute) is not None]
        means.append(np.mean(values))
        sds.append(np.std(values))
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
    means = []
    sds = []
    scene_types = set(sketch.scene_type for sketch in data if sketch.scene_type is not None)
    for scene_type in scene_types:
        values = [getattr(sketch, attribute) for sketch in data if sketch.scene_type == scene_type and getattr(sketch, attribute) is not None]
        means.append(np.mean(values))
        sds.append(np.std(values))
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
    
# make a bar chart of the top ten actors by mean on an attribute
def bar_chart_of_top_ten_actors_by_mean(data, attribute):
    # check attribute is valid
    if not hasattr(data[0], attribute):
        raise AttributeError("Attribute " + attribute + " does not exist in data")
    # check is attribute is numeric
    if not np.issubdtype(type(getattr(data[0], attribute)), np.number):
        raise TypeError("Attribute " + attribute + " is not numeric")
    # calculate mean for each actor
    means = []
    # find all actors within the sketch.cast
    actors = set()
    for sketch in data:
        for actor in sketch.cast:
            if actor is not None:
                actors.add(actor)
    # calculate mean for each actor
    for actor in actors:
        values = []
        for sketch in data:
            for a in sketch.cast:
                if a == actor and getattr(sketch, attribute) is not None:
                    values.append(getattr(sketch, attribute))
        means.append(np.mean(values))
    # sort actors by mean
    actors = list(actors)
    means = list(means)
    actors, means = zip(*sorted(zip(actors, means), key=lambda x: x[1], reverse=True))
    # take top ten actors
    actors = actors[:10]
    means = means[:10]
    # plot bar chart
    plt.barh(list(actors), means)
    plt.title('Bar Chart of Mean ' + attribute + ' by Actors')
    plt.xlabel(attribute)
    plt.ylabel('Actors')
    plt.gca().invert_yaxis() # put in ascending order 
    plt.tight_layout()
    plt.show()
    # save figure
    plt.savefig('graphs/' + attribute + '_by_actor_bar_chart.png', bbox_inches='tight')

if __name__ == '__main__':
    draw_all_graphs_and_tables("view_count")