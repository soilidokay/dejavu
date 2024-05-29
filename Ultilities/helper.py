import numpy as np
from pydub import AudioSegment

from dejavu.config.settings import DEFAULT_FS, DEFAULT_OVERLAP_RATIO, DEFAULT_WINDOW_SIZE


def extract_audio_segment(file_path, start_time, end_time, output_path):
    # Load the original audio file
    audio = AudioSegment.from_file(file_path)

    # Convert start and end times from seconds to milliseconds
    start_ms = start_time * 1000
    end_ms = end_time * 1000

    # Extract the segment
    segment = audio[start_ms:end_ms]

    # Export the extracted segment
    segment.export(output_path, format="mp3")


def to_timetamp_default(offset):
    return round(float(offset) / DEFAULT_FS * DEFAULT_WINDOW_SIZE * DEFAULT_OVERLAP_RATIO, 5)


def create_subarrays(arr, constant_diff, key=lambda x: x):
    subarrays = []

    current_subarray = [arr[0]]

    for i in range(1, len(arr)):
        if key(arr[i]) - key(arr[i-1]) <= constant_diff:
            current_subarray.append(arr[i])
        else:
            subarrays.append(current_subarray)
            current_subarray = [arr[i]]

    subarrays.append(current_subarray)
    return subarrays


def rotate_matrix_90_clockwise(matrix, axis=1):
    matrix = np.array(matrix)
    # Sử dụng np.transpose để chuyển vị ma trận và np.flip để lật ma trận theo hàng
    return np.flip(np.transpose(matrix), axis=axis)
