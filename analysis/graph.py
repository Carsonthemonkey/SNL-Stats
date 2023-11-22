import numpy as np
import matplotlib.pyplot as plt
from analysis.load_data import load_full_data


def draw_all_graphs():
    # Load data
    data = load_full_data()
    draw_boxplot_for_scene_type(data)

def draw_boxplot_for_scene_type(data):
    # Load data
    data = load_full_data()

    # find all scene types
    # scene_types = data["scene_type"].unique()
    # print(data)
    scene_types = set(sketch.scene_type for sketch in data if sketch.scene_type is not None)

    # box plot of views for different scence types
    boxplot_data = [
        [sketch.view_count for sketch in data if sketch.scene_type == scene_type and sketch.view_count is not None] for scene_type in scene_types
    ]
    boxplot_data = list(boxplot_data)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.boxplot(boxplot_data, vert=False, labels=scene_types)
    # ax.set_xticklabels(scene_types)
    ax.set_title('Boxplot of View Counts by Scene Types')
    ax.set_xlabel('View Counts (in 10,000,000s)')
    ax.set_ylabel('Scene Types')
    plt.show()

if __name__ == '__main__':
    draw_all_graphs()