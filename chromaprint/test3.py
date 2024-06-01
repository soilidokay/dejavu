import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from scipy.spatial.distance import cosine
# Hàm để tính toán và hiển thị MFCCs


# Hàm để tính toán MFCCs với các biến đổi tiền xử lý
def compute_preprocessed_mfcc(audio_path, sr=22050, n_mfcc=13, duration=None):
    # Tải audio với tốc độ lấy mẫu chuẩn
    y, _ = librosa.load(audio_path, sr=sr, duration=duration)

    # Resampling (nếu cần)
    y_resampled = librosa.resample(y, orig_sr=sr, target_sr=22050)

    # Normalization
    y_normalized = librosa.util.normalize(y_resampled)

    # Tính toán MFCCs
    mfccs = librosa.feature.mfcc(y=y_normalized, sr=sr, n_mfcc=n_mfcc)

    return mfccs


def compute_mfcc(audio_path):
    # Tính toán MFCCs
    mfccs = compute_preprocessed_mfcc(audio_path)

    # Vẽ MFCCs
    # plt.figure(figsize=(10, 4))
    # librosa.display.specshow(mfccs, x_axis='time')
    # plt.colorbar()
    # plt.title('MFCC')
    # plt.tight_layout()
    # plt.show()

    return mfccs[:, :6000]


# Tính toán và hiển thị MFCCs cho audio 1
mfccs1 = compute_mfcc('app/query/Without His Friends.mp3')

# Tính toán và hiển thị MFCCs cho audio 2
# mfccs2 = compute_mfcc('app/data/Without His Friends.wav')
mfccs2 = compute_mfcc('app/data/Without Your Name.wav')

# Hàm tính khoảng cách Euclidean giữa hai MFCCs


def euclidean_distance(mfcc1, mfcc2):
    return np.linalg.norm(mfcc1 - mfcc2)

# Hàm tính độ tương đồng sử dụng Dynamic Time Warping (DTW)


def dtw_distance(mfcc1, mfcc2):
    from librosa.sequence import dtw
    D, wp = dtw(mfcc1.T, mfcc2.T, subseq=True)
    return D[-1, -1]

# Hàm tính độ tương đồng Cosine giữa hai MFCCs


def cosine_similarity(mfcc1, mfcc2):
    # Tính toán độ tương đồng Cosine cho từng cặp vector
    cos_sim = np.mean([1 - cosine(mfcc1[:, i], mfcc2[:, i]) for i in range(min(mfcc1.shape[1], mfcc2.shape[1]))])
    return cos_sim


# Tính toán khoảng cách Euclidean giữa hai MFCCs
euclidean_dist = euclidean_distance(mfccs1, mfccs2)

# Tính toán khoảng cách DTW giữa hai MFCCs
dtw_dist = dtw_distance(mfccs1, mfccs2)

# Tính toán độ tương đồng Cosine giữa hai MFCCs
cosine_sim = cosine_similarity(mfccs1, mfccs2)

print(f'Cosine Similarity: {cosine_sim}')
print(f'Euclidean Distance: {euclidean_dist}')
print(f'DTW Distance: {dtw_dist}')
