import os
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


def max_difference(arr):
    if len(arr) < 2:
        return 0  # Không có phần tử liên tiếp để so sánh

    # Tính hiệu giữa các phần tử liên tiếp
    differences = [abs(arr[i] - arr[i+1]) for i in range(len(arr) - 1)]

    # Tìm giá trị lớn nhất của hiệu
    max_diff = max(differences)
    return max_diff


def split_audio(file_name: str, duration: int, output_dir: str = "audio_segments"):
    """
    Split an audio file into segments of a specified duration and save them to a directory.

    Parameters:
    - file_name (str): Path to the audio file.
    - duration (int): Duration of each segment (in seconds).
    """
    # Load the audio file
    audio = AudioSegment.from_file(file_name)

    # Set the length of each segment (in milliseconds)
    segment_length = duration * 1000  # Convert seconds to milliseconds

    # Calculate the number of segments
    num_segments = len(audio) // segment_length

    # Directory to save the audio segments
    os.makedirs(output_dir, exist_ok=True)

    # Get the base name of the audio file without the extension
    base_name = os.path.splitext(os.path.basename(file_name))[0]

    # Split the audio file into segments and save them
    for i in range(num_segments):
        start_time = i * segment_length
        end_time = (i + 1) * segment_length
        segment = audio[start_time:end_time]

        # Save the audio segment
        segment.export(os.path.join(output_dir, f"{base_name}_segment_{i}.mp3"), format="mp3")

    # Handle the last segment if there is a remainder
    if len(audio) % segment_length != 0:
        start_time = num_segments * segment_length
        segment = audio[start_time:]
        segment.export(os.path.join(output_dir, f"{base_name}_segment_{num_segments}.mp3"), format="mp3")

    print("Audio segments created successfully!")
