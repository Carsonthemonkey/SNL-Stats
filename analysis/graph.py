import numpy as np
import matplotlib.pyplot as plt
from analysis.load_data import load_full_data


def draw_all_graphs():
    # Load data
    data = load_full_data()
    draw_boxplot_for_scene_type(data, "view_count")

def draw_boxplot_for_scene_type(data, attribute):
    # check attribute is valid
    if not hasattr(data[0], attribute):
        raise AttributeError("Attribute " + attribute + " does not exist in data")
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

if __name__ == '__main__':
    draw_all_graphs()