import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fftpack import fft
import scipy.signal as signal
import librosa


def draw_spectogram(audio_file: str):
    # Read the audio file
    audio, sample_rate = librosa.load(audio_file)

    # If stereo, take only one channel
    if len(audio.shape) == 2:
        audio = audio[:, 0]


    
    # Compute the spectrogram
    frequencies, times, Sxx = signal.spectrogram(audio, sample_rate)
    # Apply log transform since specgram function returns linear array. 0s are excluded to avoid np warning.
    # audio = 10 * np.log10(audio, out=np.zeros_like(audio), where=(audio != 0))


    # Plot the spectrogram
    plt.figure(figsize=(10, 6))
    plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='gouraud')
    plt.title('Spectrogram')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.colorbar(label='Intensity [dB]')
    plt.savefig(f'spectrograms/{os.path.basename(audio_file)}.png')


audio = 'app/query/Without His Friends.wav'
draw_spectogram(audio)
audio = 'app/query/Without His Friends1.mp3'
draw_spectogram(audio)
