import pyarrow as pa
import numpy as np
import pickle
import time
from multiprocessing import shared_memory
import pyarrow.plasma as plasma
from contextlib import contextmanager


def serialize_numpy_array(array: np.ndarray) -> bytes:
    """Serialize a NumPy array using pickle."""
    return pickle.dumps(array)


def calculate_serialized_size(serialized_array: bytes) -> int:
    """Calculate the size of the serialized NumPy array."""
    return len(serialized_array)


def export_to_shared_memory(name: str, serialized_array: bytes):
    """Export serialized NumPy array to shared memory."""
    size = len(serialized_array)
    shm = shared_memory.SharedMemory(create=True, name=name, size=size)
    # Write serialized array data to shared memory
    shm.buf[:size] = serialized_array
    return shm


def clear_shared_memory(name: str):
    """Clear shared memory."""
    try:
        shm = shared_memory.SharedMemory(name=name)
        shm.unlink()
    except FileNotFoundError:
        pass


def export_to_plasma(client, object_id: bytes, serialized_array: bytes):
    """Export serialized NumPy array to Plasma."""
    size = len(serialized_array)
    # Create a new Plasma object and get its buffer
    buffer = client.create(object_id, size)
    # Create an Arrow buffer from the serialized array
    arrow_buffer = pa.py_buffer(serialized_array)
    # Write the serialized array data to the Plasma object using the Arrow buffer
    stream = pa.FixedSizeBufferWriter(buffer)
    stream.write(arrow_buffer)
    stream.close()
    client.seal(object_id)


def clear_plasma(client, object_id: bytes):
    """Clear Plasma store."""
    client.delete([object_id])


if __name__ == "__main__":
    n_iters = 50
    n_rows = 62500*10  # 62500 rows is 1MB, 5MB, 10MB, 25MB
    array = np.random.random((n_rows, 2))  # 2 columns for x and y

    # Serialize the array outside the timing loop to focus on export time
    serialized_array = serialize_numpy_array(array)
    array_size = calculate_serialized_size(serialized_array)

    plasma_times = []
    shared_memory_times = []

    # Example with Plasma
    plasma_client = plasma.connect("/tmp/plasma")
    object_id = plasma.ObjectID.from_random()
    for i in range(n_iters):
        clear_plasma(plasma_client, object_id)
        start_time = time.time()
        export_to_plasma(plasma_client, object_id, serialized_array)
        end_time = time.time()
        plasma_times.append(end_time - start_time)

    # Example with shared memory
    shared_memory_name = "numpy_array"
    for i in range(n_iters):
        clear_shared_memory(shared_memory_name)
        start_time = time.time()
        shm = export_to_shared_memory(shared_memory_name, serialized_array)
        shm.close()
        end_time = time.time()
        shared_memory_times.append(end_time - start_time)

    average_plasma_time = sum(plasma_times) / len(plasma_times)
    average_shared_memory_time = sum(
        shared_memory_times) / len(shared_memory_times)

    print("Plasma: %f" % average_plasma_time)
    print("Shared Memory: %f" % average_shared_memory_time)
