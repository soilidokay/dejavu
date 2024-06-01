import json
import os
import shutil

import numpy as np

from Ultilities.helper import rotate_matrix_90_clockwise, create_subarrays, extract_audio_segment, to_timetamp_default
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
from dejavu.logic.recognizer.file_recognizer_attach_offset import FileRecognizerAttchOffset
from dejavu.logic.recognizer.microphone_recognizer import MicrophoneRecognizer
from dejavu.ultilities.result_process import result_process

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
    # djv.fingerprint_directory("test2", [".wav"])
    # recognize_file = "mp3/3z2Ovv5OV4U.mp3"
    # recognize_file = "audio_segments/3z2Ovv5OV4U_segment_4.mp3"
    # recognize_file = "audio_segments/3z2Ovv5OV4U_merged_segment_7.mp3"
    # recognize_file = "mp3/3z2Ovv5OV4U_combined.mp3"
    # recognize_file = "mp3/Llw9Q6akRo4_combined.mp3"
    # recognize_file = "mp3/7zh2QCjp818_combined.mp3"
    # recognize_file = "mp3/3z2Ovv5OV4U_merged.mp3"
    # recognize_file = "mp32/3z2Ovv5OV4U_merged_2.wav"
    # recognize_file = "mp3/3z2Ovv5OV4U_merged.wav"
    recognize_file = "mp3/3z2Ovv5OV4U.mp3"
    # recognize_file = "mp32/3z2Ovv5OV4U.wav"
    # recognize_file = "mp3/r1OtnOs-utU.mp3"
    # Recognize audio from a file

    frao = FileRecognizerAttchOffset(djv, topq=1, throld_find=2)
    results = frao.recognize_result(recognize_file)

    # print(f"From file we recognized: {results}\n")
    if os.path.exists('results'):
        shutil.rmtree('results')
    os.makedirs('results', exist_ok=True)
    is_match = False
    print(f'align_time : {results.align_time}')
    print(f'query_time : {results.query_time}')
    for idex_s, value in enumerate(results.matches):
        song_name = value.song_name.decode('utf-8')
        song_path = f'test2/{song_name}.wav'
        songs = [song_path, recognize_file]
        for song_q in value.offsets:
            for idex, song_seg in enumerate(song_q):
                for idx2, song in enumerate(song_seg.all()):
                    is_match = True
                    file_out = f"{idex_s}_{idex}_{idx2}_{song.start_time}_{song.end_time}_output_segment.mp3"
                    song.save(songs[idx2], file_out)
    if not is_match:
        print("no match!")
