import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

def normalize_speed(audio, sr, target_sr=44100):
    # Compute the speed ratio
    speed_ratio = sr / target_sr

    # Adjust the speed of the audio
    normalized_audio = librosa.effects.time_stretch(audio, speed_ratio)
    return normalized_audio

# Load audio file
audio, sr = librosa.load('path_to_audio.wav')

# Normalize speed
normalized_audio = normalize_speed(audio, sr)

# Save the normalized audio
librosa.output.write_wav('normalized_audio.wav', normalized_audio, sr)

# Plot the spectrograms for comparison
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
librosa.display.specshow(librosa.amplitude_to_db(np.abs(librosa.stft(audio)), ref=np.max), sr=sr, y_axis='log', x_axis='time')
plt.title('Original Audio')
plt.colorbar(format='%+2.0f dB')
plt.subplot(2, 1, 2)
librosa.display.specshow(librosa.amplitude_to_db(np.abs(librosa.stft(normalized_audio)), ref=np.max), sr=sr, y_axis='log', x_axis='time')
plt.title('Normalized Audio')
plt.colorbar(format='%+2.0f dB')
plt.tight_layout()
plt.show()
