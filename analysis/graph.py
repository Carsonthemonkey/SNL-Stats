import numpy as np
import matplotlib.pyplot as plt
from analysis.load_data import load_full_data


def draw_all_graphs_and_tables():
    # Load data
    data = load_full_data()
    draw_boxplot_for_scene_type(data, "view_count")
    table_of_mean_and_std_by_scene_type(data, "view_count")

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
        [getattr(sketch, attribute) for sketch in data if sketch.scene_type == scene_type and sketch.view_count is not None] for scene_type in scene_types
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

# make table of mean and std of views for each scene type
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
    
    

if __name__ == '__main__':
    draw_all_graphs_and_tables()