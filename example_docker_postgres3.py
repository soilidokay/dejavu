import json
import os
import shutil

import numpy as np

from Ultilities.helper import rotate_matrix_90_clockwise, create_subarrays, extract_audio_segment, to_timetamp_default
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
from dejavu.logic.recognizer.file_recognizer_attach_offset import FileRecognizerAttchOffset
from dejavu.logic.recognizer.microphone_recognizer import MicrophoneRecognizer

# load config from a JSON file (or anything outputting a python dictionary)
config = {
    "database": {
        "host": "db",
        "user": "postgres",
        "password": "password",
        "database": "dejavu"
    },
    "database_type": "postgres"
}

if __name__ == '__main__':

    # create a Dejavu instance
    djv = Dejavu(config)

    # Fingerprint all the mp3's in the directory we give it
    # djv.fingerprint_directory("test", [".mp3"])
    # recognize_file = "mp3/3z2Ovv5OV4U.mp3"
    # recognize_file = "audio_segments/3z2Ovv5OV4U_segment_4.mp3"
    # recognize_file = "audio_segments/3z2Ovv5OV4U_merged_segment_7.mp3"
    # recognize_file = "mp3/3z2Ovv5OV4U_combined.mp3"
    # recognize_file = "mp3/Llw9Q6akRo4_combined.mp3"
    # recognize_file = "mp3/7zh2QCjp818_combined.mp3"
    # recognize_file = "mp3/3z2Ovv5OV4U_merged_2.mp3"
    recognize_file = "mp32/3z2Ovv5OV4U_merged_2.wav"
    # recognize_file = "mp3/r1OtnOs-utU.mp3"
    # Recognize audio from a file
    results = djv.recognize(FileRecognizerAttchOffset, recognize_file)
    # print(f"From file we recognized: {results}\n")
    if os.path.exists('results'):
        shutil.rmtree('results')
    os.makedirs('results', exist_ok=True)

    if len(results["results"]) > 0:
        for idex_s,value in enumerate(results["results"]):
            song_name = value["song_name"].decode('utf-8')
            song_path = f'test/{song_name}.mp3'
            songs = [song_path, recognize_file]

            for song_q in value["offsets"]:
                start_time = 0
                for idex, song_seg in enumerate(song_q):
                    for idx2, song in enumerate(song_seg):
                        start_time = song[0]  # (DEFAULT_WINDOW_SIZE / DEFAULT_FS)
                        end_time = song[1]  # (DEFAULT_WINDOW_SIZE / DEFAULT_FS)

                        file_out = f"{idex_s}_{idex}_{idx2}_{start_time}_{end_time}_output_segment.mp3"
                        extract_audio_segment(songs[idx2], start_time, end_time,
                                            f"results/{file_out}")
                        print(
                            f"Extracted segment from {start_time} to {end_time} seconds. {file_out}")
                break
                # for offset_pair in offsets:
                #     for idex, first_match_offset in enumerate(offset_pair):
                #             # Ví dụ: Trích xuất đoạn âm thanh dựa trên offset đầu tiên và độ dài mặc định (10 giây)
                #             # Bạn có thể điều chỉnh start_time và duration theo nhu cầu của mình
                #             # Chuyển đổi offset từ mẫu sang giây
                #             start_time = to_timetamp_default(first_match_offset)  # (DEFAULT_WINDOW_SIZE / DEFAULT_FS)
                #             duration = 5  # Độ dài đoạn âm thanh cần trích xuất (giây)
                #             end_time = start_time + duration
                #             if start_time < 32 and idex == 0: break
                #             extract_audio_segment(recognize_file, start_time, end_time, f"output_segment{idex}.mp3")
                #             print(f"Extracted segment from {start_time} to {end_time} seconds. output_segment{idex}.mp3")
                #     if start_time < 32:
                #         continue
                #     print()
            # Or use a recognizer without the shortcut, in anyway you would like
            # recognizer = FileRecognizer(djv)
            # results = recognizer.recognize_file("mp3/Josh-Woodward--I-Want-To-Destroy-Something-Beautiful.mp3")
            # print(f"No shortcut, we recognized: {results}\n")
    else:
        print("no match!")
