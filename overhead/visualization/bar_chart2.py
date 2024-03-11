import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load and clean the datasets
average_overhead_df = pd.read_excel('average overhead.xlsx').iloc[1:].reset_index(drop=True)
standard_deviation_df = pd.read_excel('standard_deviation.xlsx').iloc[1:].reset_index(drop=True)
average_overhead_df.columns = ['Configuration', '1MB', '5MB', '10MB', '25MB', '50MB']
standard_deviation_df.columns = ['Configuration', '1MB', '5MB', '10MB', '25MB', '50MB']

# Merge the datasets on configuration to include standard deviations
merged_df = pd.merge(average_overhead_df, standard_deviation_df, on='Configuration', suffixes=('_avg', '_std'))

# Data for plotting
object_sizes = ['1MB', '5MB', '10MB', '25MB', '50MB']
configurations = merged_df['Configuration'].tolist()
data_avg = merged_df[[size + '_avg' for size in object_sizes]].values.T  # Transpose for plotting
data_std = merged_df[[size + '_std' for size in object_sizes]].values.T  # Transpose for error bars

# Bar chart settings
bar_width = 0.15  # Adjusted for the number of configurations
index = np.arange(len(object_sizes))

# Set the style for the plot
sns.set_style("whitegrid")

# Colors for each configuration, extended to fit new configurations
colors = ['#6699ff', '#ff6666', '#9999ff', '#ff9933', '#66cc66']

# Plot each configuration with error bars
plt.figure(figsize=(12, 8))
for i, (config, color) in enumerate(zip(configurations, colors)):
    plt.bar(index + i * bar_width, data_avg[:, i], yerr=data_std[:, i],
            width=bar_width, label=config, color=color, capsize=5)

plt.xlabel('Object Size')
plt.ylabel('Latency (milliseconds)')
plt.title('Mean Latency of Broadcast and Gather on 4 nodes\nwith Different Object Sizes and Standard Deviations')
plt.xticks(index + bar_width * 2, object_sizes)
plt.yscale("log")

plt.legend()
plt.tight_layout()

# Save the updated plot to a file
plt.savefig("plot_with_std.png")  # Update this path as necessary
plt.show()
