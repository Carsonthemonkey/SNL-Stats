import numpy as np
import matplotlib.pyplot as plt
from analysis.load_data import load_full_data
import pandas as pd
import matplotlib.dates as mdates

all_scene_types = None
all_actors = None

def draw_all_graphs_and_tables(attribute, show=False):
    # check attribute is valid
    if not hasattr(data[0], attribute):
        raise AttributeError("Attribute " + attribute + " does not exist in data")
    # check is attribute is numeric
    if not np.issubdtype(type(getattr(data[0], attribute)), np.number):
        raise TypeError("Attribute " + attribute + " is not numeric")
    # Load data
    data = load_full_data()
    # draw_boxplot_for_scene_type(data, attribute, show)
    # table_of_mean_and_std_by_scene_type(data, attribute)
    # bar_chart_of_mean_and_std_by_scene_type(data, attribute, show)
    # bar_chart_of_most_extreme_actors_by_mean(data, attribute, show, top=True, n=15)
    # time_series_of_attribute_over_time(data, attribute, show)

def draw_boxplot_for_scene_type(data, attribute, show=True):
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
    # save figure
    fig.savefig('graphs/' + attribute + '/' + attribute + '_by_scene_type_boxplot.png', bbox_inches='tight')
    if show is True:
        plt.show()
    plt.clf()

# make table of mean and std of an attribute for each scene type
def table_of_mean_and_std_by_scene_type(data, attribute):
    # calculate mean and std for each scene type
    scene_types, means, sds = get_mean_and_std_by_scene_type(data, attribute)
    # print table
    column_width = 20
    print(f"{'Scene Type':<{column_width}} {'Mean':<{column_width}} {'Standard Deviation':<{column_width}}")
    print(f"{'-'*column_width} {'-'*column_width} {'-'*column_width}")
    for st, m, sd in zip(scene_types, means, sds):
        print(f"{st:<{column_width}} {m:<{column_width}} {sd:<{column_width}}")

# make a bar chart of mean and std on an attribute for each scene type
def bar_chart_of_mean_and_std_by_scene_type(data, attribute, show=True):
    # calculate mean and std for each scene type
    scene_types, means, sds = get_mean_and_std_by_scene_type(data, attribute)
    # plot bar chart
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.bar(list(scene_types), means, yerr=sds, align='center', ecolor='black', capsize=5)
    ax.set_title('Bar Chart of Mean ' + attribute + ' by Scene Types')
    ax.set_xlabel('Scene Types')
    ax.set_ylabel(attribute)
    ax.yaxis.grid(True)
    # save figure
    fig.savefig('graphs/' + attribute + '/' + attribute + '_by_scene_type_bar_chart.png', bbox_inches='tight')
    if show is True:
        plt.show()
    plt.clf()
    
# make a bar chart of the actors with highest/lowest mean of an attribute
def bar_chart_of_most_extreme_actors_by_mean(data, attribute, show, top=True, n=10):
    # find correct n actors and their means
    actors, means = get_sorted_actors_and_means(data, attribute)
    if top:
        actors = actors[:n]
        means = means[:n]
    else:
        actors = actors[-n:]
        means = means[-n:]
    # get string for title and filename
    direction_str = 'Top' if top else 'Bottom'
    # plot bar chart
    plt.barh(list(actors), means)
    plt.title('Bar Chart of Mean ' + attribute + ' by ' + direction_str + ' ' + str(n) + ' Actors')
    plt.xlabel(attribute)
    plt.ylabel('Actors')
    if top:  # put in ascending order
        plt.gca().invert_yaxis() 
    plt.tight_layout()
    # save figure
    if top:
        plt.savefig('graphs/' + attribute + '/' + attribute + '_by_actor_bar_chart_' + direction_str.lower() + '_' + str(n) + '.png', bbox_inches='tight')
    else:
        plt.savefig('graphs/' + attribute + '/' + attribute + '_by_actor_bar_chart_' + direction_str.lower() + '_' + str(n) + '.png', bbox_inches='tight')
    if show is True:
        plt.show()
    plt.clf()

# make a time series of an attribute over time (based on upload_date)
def time_series_of_attribute_over_time(data, attribute, show=True):
    # sort data by upload date
    data = sorted(data, key=lambda x: x.upload_date)
    # Convert the 'upload_date' column to datetime
    data_dates = [pd.to_datetime(sketch.upload_date, format='%Y-%m-%dT%H:%M:%SZ') for sketch in data]
    plt.figure(figsize=(16, 6))
    plt.plot(data_dates, [getattr(sketch, attribute) for sketch in data])
    # Format x-axis ticks to show years
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.title('Time Series of ' + attribute + ' Over Time')
    plt.xlabel('Upload Date')
    plt.ylabel(attribute)
    plt.savefig('graphs/' + attribute + '/' + attribute + '_over_time.png', bbox_inches='tight')
    if show is True:
        plt.show()
    plt.clf()


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
    # clear files with graph subfolders (uncomment when needed)
    # import os
    # for attr in ["view_count", "like_count", "comment_count", "mean_sentiment", "std_sentiment", "duration"]:
    #     folder = "graphs/" + attr
    #     for filename in os.listdir(folder):
    #         file_path = os.path.join(folder, filename)
    #         if os.path.isfile(file_path):
    #             os.unlink(file_path)

    attributes = ["view_count", "like_count", "comment_count", "mean_sentiment", "std_sentiment", "duration"]
    for attr in attributes:
        draw_all_graphs_and_tables(attr, show=False)
    # draw_all_graphs_and_tables("view_count", show=True)