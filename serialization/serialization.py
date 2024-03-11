import pickle
import numpy as np
import time
import matplotlib.pyplot as plt

# Adjusted function definitions for serialization and deserialization


def serialize_data(data, protocol):
    start_time = time.time()
    buffers = []
    if protocol == 5:
        pickled_data = pickle.dumps(
            data, protocol=protocol, buffer_callback=buffers.append)
    else:
        pickled_data = pickle.dumps(data, protocol=5)
    end_time = time.time()
    # Convert to milliseconds
    return pickled_data, buffers, (end_time - start_time) * 1000


def deserialize_data(pickled_data, protocol, buffers=None):
    start_time = time.time()
    if protocol == 5 and buffers:
        data = pickle.loads(pickled_data, buffers=buffers)
    else:
        data = pickle.loads(pickled_data)
    end_time = time.time()
    return data, (end_time - start_time) * 1000  # Convert to milliseconds

# Adjusted benchmark function


def benchmark(protocol):
    data = np.ones(655360)  # 5MB Object
    pickled_data, buffers, serialize_time = serialize_data(data, protocol)
    _, deserialize_time = deserialize_data(pickled_data, protocol, buffers)
    return serialize_time, deserialize_time


# Perform benchmarks
serialize_time_4, deserialize_time_4 = benchmark(4)
serialize_time_5, deserialize_time_5 = benchmark(5)

# Plotting adjustments
labels = ['In-Band', 'Out-of-Band']
serialize_times = [serialize_time_4, serialize_time_5]
deserialize_times = [deserialize_time_4, deserialize_time_5]

x = np.arange(len(labels))
width = 0.2  # Make the bars narrower

object_size_mb = 5
serialize_throughput_4 = object_size_mb / (serialize_times[0] / 1000)  # MB/s
deserialize_throughput_4 = object_size_mb / \
    (deserialize_times[0] / 1000)  # MB/s
serialize_throughput_5 = object_size_mb / (serialize_times[1] / 1000)  # MB/s
deserialize_throughput_5 = object_size_mb / \
    (deserialize_times[1] / 1000)  # MB/s

throughput_serialize = [serialize_throughput_4, serialize_throughput_5]
throughput_deserialize = [deserialize_throughput_4, deserialize_throughput_5]

peak_memory_usage = [1063.01, 2062.81]  # Placeholder values

# Adjusting the left subplot to display throughput
fig, axs = plt.subplots(1, 2, figsize=(16, 6), dpi=100)

# Throughput Plot for Serialization and Deserialization
ax1 = axs[0]
rects1 = ax1.bar(x - width/2, throughput_serialize, width,
                 label='Serialize', color='skyblue')
rects2 = ax1.bar(x + width/2, throughput_deserialize, width,
                 label='Deserialize', color='lightgreen')

ax1.set_ylabel('Throughput (MB/s)')
ax1.set_title('Throughput of Serializing and Deserializing 5MB Object')
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.legend(loc='upper left')
ax1.bar_label(rects1, padding=3, fmt='%.2f')
ax1.bar_label(rects2, padding=3, fmt='%.2f')
ax1.set_yscale("log")
ax1.grid(True, which="both", ls="--", linewidth=0.5)

# Peak Memory Usage Plot with adjustments
ax2 = axs[1]
rects3 = ax2.bar(labels, peak_memory_usage, width, color='royalblue')

ax2.set_ylabel('Megabytes (MB)')
ax2.set_title('Peak Memory Usage for 1GB Object')
ax2.set_xticks(x)
ax2.set_xticklabels(labels)
ax2.bar_label(rects3, padding=3, fmt='%.2f')
ax2.grid(True, which="major", ls="--", linewidth=0.5)

plt.tight_layout()
plt.show()
