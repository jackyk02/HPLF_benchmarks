import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
df = pd.read_excel('plasma_bench.xlsx')

# Plotting
plt.figure(figsize=(14, 8))

# Time taken for Plasma and Shared Memory, using professional colors
plt.subplot(1, 2, 1)
plt.plot(df['Object Size (MB)'], df['Time taken for Plasma in seconds'],
         label='Plasma', marker='o', color='navy')  # Navy for Plasma
plt.plot(df['Object Size (MB)'], df['Time Taken for Shared Memory in seconds'],
         label='Shared Memory', marker='x', color='darkgreen')  # Dark green for Shared Memory
plt.xlabel('Object Size (MB)')
plt.ylabel('Time taken (seconds)')
plt.title('Time Taken by Plasma and Shared Memory')
plt.legend()

# Throughput for Plasma and Shared Memory, using professional colors
plt.subplot(1, 2, 2)
plt.plot(df['Object Size (MB)'], df['Plasma Throughput (MB/s)'],
         label='Plasma Throughput', marker='o', color='navy')  # Navy for Plasma Throughput
plt.plot(df['Object Size (MB)'], df['Shared Memory Throughput (MB/s)'], label='Shared Memory Throughput',
         marker='x', color='darkgreen')  # Dark green for Shared Memory Throughput
plt.xlabel('Object Size (MB)')
plt.ylabel('Throughput (MB/s)')
plt.title('Throughput of Plasma and Shared Memory')
plt.legend()

plt.tight_layout()
plt.show()
