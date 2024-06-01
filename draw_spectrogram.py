from dejavu.logic import decoder
from dejavu.logic.fingerprint import fingerprint_test

file_name = "app/query/Without His Friends.wav"
channels, fs, file_hash = decoder.read(file_name)
fingerprints = set()
channel_amount = len(channels)

Fs: int = 44100
wsize: int = 4096
wratio: float = 0.5
fan_value: int = 10

hashes1 = []
for channeln, channel in enumerate(channels, start=1):
    hashes = fingerprint_test(
        channel, Fs=Fs, wsize=wsize, wratio=wratio, fan_value=fan_value, out_spec_filename=f"./spectrograms/3z2Ovv5OV4U_merged_2_segment_0_{channeln}.png")

    hashes1.extend(hashes)

hashes2 = []
file_name = "app/query/Without His Friends1.mp3"
channels, fs, file_hash = decoder.read(file_name, None)
fingerprints = set()
channel_amount = len(channels)
for channeln, channel in enumerate(channels, start=1):
    hashes = fingerprint_test(
        channel, Fs=Fs, wsize=wsize, wratio=wratio, fan_value=fan_value, out_spec_filename=f"./spectrograms/7zh2QCjp818_segment_0_{channeln}.png")
    hashes2.extend(hashes)


intersection = list(set(map(lambda x: x[0], hashes1)) & set(map(lambda x: x[0], hashes2)))

pass
