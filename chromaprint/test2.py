import acoustid
import chromaprint
import numpy as np

# Hàm để lấy fingerprint từ file audio
def get_fingerprint(audio_path):
    duration, fingerprint = acoustid.fingerprint_file(audio_path)
    return fingerprint


# Đường dẫn tới hai file âm thanh
audio_path1 = 'app/query/Without His Friends.mp3'
audio_path2 = 'app/data/Without His Friends.wav'
api_key = 'YOUR_ACOUSTID_API_KEY'

# Lấy fingerprint cho từng file
fingerprint1 = get_fingerprint(audio_path1)
fingerprint2 = get_fingerprint(audio_path2)

# Chuyển đổi fingerprints thành numpy arrays để so sánh
fp1_array = np.array(fingerprint1, dtype=np.int32)
fp2_array = np.array(fingerprint2, dtype=np.int32)

# Hàm tính khoảng cách Euclidean giữa hai fingerprints
def euclidean_distance(fp1, fp2):
    return np.linalg.norm(fp1 - fp2)

# Hàm tính độ tương đồng Cosine giữa hai fingerprints
def cosine_similarity(fp1, fp2):
    dot_product = np.dot(fp1, fp2)
    norm_fp1 = np.linalg.norm(fp1)
    norm_fp2 = np.linalg.norm(fp2)
    return dot_product / (norm_fp1 * norm_fp2)

# Tính toán và in ra kết quả
euclidean_dist = euclidean_distance(fp1_array, fp2_array)
cosine_sim = cosine_similarity(fp1_array, fp2_array)

print(f'Euclidean Distance: {euclidean_dist}')
print(f'Cosine Similarity: {cosine_sim}')