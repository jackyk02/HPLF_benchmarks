import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
df = pd.read_excel('plasma_bench.xlsx')

# Plotting
plt.figure()

# Time taken for Plasma and Shared Memory, using professional colors
# plt.subplot(1, 2, 1)
plt.rcParams.update({'font.size': 14})
plt.plot(df['Object Size (MB)'], df['Time Taken for Shared Memory in seconds']*1000,
         label='Python Shared Memory', marker='x', color='darkgreen')  # Dark green for Shared Memory
plt.plot(df['Object Size (MB)'], df['Time taken for Plasma in seconds']*1000,
         label='Plasma Object Store', marker='o', color='navy')  # Navy for Plasma
plt.xlabel('Object Size (MB)')
plt.ylabel('Delay (milliseconds)')
# plt.title('Time Taken by Plasma and Shared Memory')
plt.legend()
plt.show()