import os
import shutil
import librosa
import numpy as np
from pydub import AudioSegment
import soundfile as sf
from dejavu.config.settings import DEFAULT_FS, DEFAULT_OVERLAP_RATIO, DEFAULT_WINDOW_SIZE
from dejavu.third_party import wavio
from pydub.effects import normalize


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


def split_audio(file_name: str, duration: int, output_dir: str = "audio_segments", amount: int = -1):
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
        if amount > 0 and i >= amount:
            print("Audio segments created successfully!")
            return

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


def normalize_audio_pypub(input_file, target_dBFS=-1.0, sample_rate=44100):
    """
    Chuẩn hóa âm thanh của một tệp âm thanh sao cho đỉnh cao nhất đạt đến mức xác định.

    :param input_file: Đường dẫn tới tệp âm thanh đầu vào.
    :param output_file: Đường dẫn lưu tệp âm thanh đầu ra sau khi chuẩn hóa.
    :param target_dBFS: Mức âm lượng đích (dBFS). Mặc định là -1.0 dBFS.
    :param sample_rate: Tần số lấy mẫu mới cho âm thanh. Mặc định là 44100 Hz.
    """
    # Load audio file
    audio = AudioSegment.from_file(input_file)

    # Set sample rate
    audio = audio.set_frame_rate(sample_rate)

    # Compute difference to target dBFS
    change_in_dBFS = target_dBFS - audio.max_dBFS

    # Apply gain to normalize audio
    audio = audio.apply_gain(change_in_dBFS)

    # audio = audio.low_pass_filter(100)  # Example: applying low-pass filter for bass boost

    # Normalize audio to ensure consistent volume levels
    audio = normalize(audio)
    # Export the normalized audio to a file
    return audio


def normalize_audio_wavio(input_file, target_dBFS=-1.0, sample_rate=44100):
    """
    Chuẩn hóa âm thanh của một tệp âm thanh sao cho đỉnh cao nhất đạt đến mức xác định.

    :param input_file: Đường dẫn tới tệp âm thanh đầu vào.
    :param target_dBFS: Mức âm lượng đích (dBFS). Mặc định là -1.0 dBFS.
    :param sample_rate: Tần số lấy mẫu mới cho âm thanh. Mặc định là 44100 Hz.
    """
    # Load audio file using wavio
    wav = wavio.read(input_file)
    audio_data = wav.data
    original_sample_rate = wav.rate
    sampwidth = wav.sampwidth
    # Resample if necessary
    if original_sample_rate != sample_rate:
        audio_data = sf.resample(audio_data, original_sample_rate, sample_rate)

    # Calculate the current dBFS of the audio
    rms = np.sqrt(np.mean(np.square(audio_data)))
    current_dBFS = 20 * np.log10(rms / 32768)

    # Compute difference to target dBFS
    change_in_dBFS = target_dBFS - current_dBFS

    # Apply gain to normalize audio
    gain = 10 ** (change_in_dBFS / 20)
    normalized_audio = audio_data * gain

    # Ensure that the values are within the acceptable range
    max_val = 2**(sampwidth * 8 - 1) - 1
    min_val = -2**(sampwidth * 8 - 1)
    normalized_audio = np.clip(normalized_audio, min_val, max_val).astype(audio_data.dtype)

    # Create a new wavio object with the normalized audio
    normalized_wav = wavio.Wav(normalized_audio, sample_rate, sampwidth)
    return normalized_wav


def normalize_audio(input_file, output_file, target_dBFS=-1.0, sample_rate=44100):
    """
    Chuẩn hóa âm thanh của một tệp âm thanh sao cho đỉnh cao nhất đạt đến mức xác định.

    :param input_file: Đường dẫn tới tệp âm thanh đầu vào.
    :param output_file: Đường dẫn lưu tệp âm thanh đầu ra sau khi chuẩn hóa.
    :param target_dBFS: Mức âm lượng đích (dBFS). Mặc định là -1.0 dBFS.
    :param sample_rate: Tần số lấy mẫu mới cho âm thanh. Mặc định là 44100 Hz.
    """
    normalize_audio_pypub(input_file, target_dBFS, sample_rate).export(output_file, format="wav")
    print(f"Normalized audio saved to {output_file}")


def convert_folder(input_folder, output_folder):
    """
    Convert all audio files in input_folder and save to output_folder.
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all files in the input folder
    files = os.listdir(input_folder)

    # Process each file in the input folder
    for file in files:
        # Check if the file is an audio file
        if file.endswith('.wav') or file.endswith('.mp3'):
            # Construct the full path of the input file
            input_file = os.path.join(input_folder, file)

            # Construct the full path of the output file
            output_file = os.path.join(output_folder, file)

            # Normalize the audio and save to the output folder
            normalize_audio(input_file, change_extension(output_file, ".wav"))


def normalize_audio2(input_file, output_file, target_pitch=440.0, target_sr=44100):
    """
    Chuẩn hóa âm thanh từ một tệp đầu vào và lưu vào tệp đầu ra.

    :param input_file: Đường dẫn tới tệp âm thanh đầu vào.
    :param output_file: Đường dẫn lưu tệp âm thanh đầu ra sau khi chuẩn hóa.
    :param target_pitch: Cao độ mục tiêu (Hz), mặc định là 440.0 Hz.
    :param target_sr: Tần số lấy mẫu mục tiêu (Hz), mặc định là 44100 Hz.
    """
    # Load audio file
    audio, sr = librosa.load(input_file, sr=None)

    # Step 1: Normalize Pitch
    # Estimate the pitch of the audio signal
    pitches, magnitudes = librosa.core.piptrack(y=audio, sr=sr)
    pitch = np.array(pitches).flatten()[np.argmax(magnitudes)]

    # Calculate the number of steps to shift
    steps = librosa.core.hz_to_midi(target_pitch) - librosa.core.hz_to_midi(pitch)

    # Shift the pitch
    normalized_audio_pitch = librosa.effects.pitch_shift(y=audio, sr=sr, n_steps=steps)

    # Step 2: Normalize Speed (if needed)
    if sr != target_sr:
        # Compute the speed ratio
        speed_ratio = sr / target_sr

        # Adjust the speed of the audio
        normalized_audio = librosa.effects.time_stretch(normalized_audio_pitch, rate=speed_ratio)
    else:
        normalized_audio = normalized_audio_pitch

    # Save the normalized audio
    sf.write(output_file, normalized_audio, target_sr)

    print(f"Normalized audio saved to {output_file}")


def convert_folder2(input_folder, output_folder):
    """
    Convert all audio files in input_folder and save to output_folder.
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all files in the input folder
    files = os.listdir(input_folder)

    # Process each file in the input folder
    for file in files:
        # Check if the file is an audio file
        if file.endswith('.wav') or file.endswith('.mp3'):
            # Construct the full path of the input file
            input_file = os.path.join(input_folder, file)

            # Construct the full path of the output file
            output_file = os.path.join(output_folder, file)

            # Normalize the audio and save to the output folder
            normalize_audio2(input_file, output_file)


def change_extension(filename, new_extension):
    base_name, old_extension = os.path.splitext(filename)
    return base_name + new_extension


def recreate_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)


def normalize_frequencies(frequencies):
    """
    Normalize a list of frequencies to the range [0, 1].

    Parameters:
    frequencies (list of float): List of frequencies to normalize.
    f_min (float): Minimum frequency in the original range.
    f_max (float): Maximum frequency in the original range.

    Returns:
    list of float: List of normalized frequencies in the range [0, 1].
    """

    f_min = min(frequencies)
    f_max = max(frequencies)

    if f_min >= f_max:
        raise ValueError("f_min should be less than f_max")

    normalized_frequencies = [(f - f_min) / (f_max - f_min) for f in frequencies]
    return normalized_frequencies


def normalize_frequency(frequency, f_min, f_max):
    """
    Normalize a list of frequencies to the range [0, 1].

    Parameters:
    frequencies (list of float): List of frequencies to normalize.
    f_min (float): Minimum frequency in the original range.
    f_max (float): Maximum frequency in the original range.

    Returns:
    list of float: List of normalized frequencies in the range [0, 1].
    """

    if f_min >= f_max:
        raise ValueError("f_min should be less than f_max")

    return (frequency - f_min) / (f_max - f_min)


def normalize_frequencies_ampli(frequencies):
    """
    Normalize a list of frequencies to the range [0, 1].

    Parameters:
    frequencies (list of float): List of frequencies to normalize.
    f_min (float): Minimum frequency in the original range.
    f_max (float): Maximum frequency in the original range.

    Returns:
    list of float: List of normalized frequencies in the range [0, 1].
    """

    f_min = min(frequencies)
    f_max = max(frequencies)

    if f_min >= f_max:
        raise ValueError("f_min should be less than f_max")

    normalized_frequencies = [2 * (f - f_min) / (f_max - f_min) - 1 for f in frequencies]
    return normalized_frequencies
