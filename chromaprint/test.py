import librosa
import numpy as np
import matplotlib.pyplot as plt

# Hàm để tính toán và hiển thị chroma features


def plot_chroma(audio_path):
    # Tải audio
    y, sr = librosa.load(audio_path)

    # Tính toán chroma features
    chroma = librosa.feature.chroma_stft(y=y[:3000000], sr=sr)

    # Vẽ chroma features
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(chroma, y_axis='chroma', x_axis='time')
    plt.colorbar()
    plt.title('Chroma Feature')
    plt.tight_layout()
    plt.show()

    return chroma


# Tính toán và hiển thị chroma features cho audio 1
chroma1 = plot_chroma('app/query/Without His Friends.mp3')

# Tính toán và hiển thị chroma features cho audio 2
# chroma2 = plot_chroma('app/data/Without His Friends.wav')
chroma2 = plot_chroma('app/data/Without Your Name.wav')

# Tính toán sự tương đồng (Cosine Similarity)
cosine_sim = np.dot(chroma1.flatten(), chroma2.flatten()) / \
    (np.linalg.norm(chroma1.flatten()) * np.linalg.norm(chroma2.flatten()))

print(f'Cosine Similarity: {cosine_sim}')

# Nếu cần tính toán Euclidean Distance
euclidean_dist = np.linalg.norm(chroma1.flatten() - chroma2.flatten())

print(f'Euclidean Distance: {euclidean_dist}')
