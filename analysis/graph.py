import numpy as np
import matplotlib.pyplot as plt
from analysis.load_data import load_full_data

# Load data
data = load_full_data()

# find all scene types
scene_types = data["scene_type"].unique()

# box plot of views for different scence types
fig, ax = plt.subplots()
ax.boxplot(
    [data[data["scene_type"] == scene_type]["view_count"] for scene_type in scene_types]
)
ax.set_xticklabels(scene_types)
ax.set_ylabel("Views")
ax.set_title("Views by Scene Type")
plt.show()

