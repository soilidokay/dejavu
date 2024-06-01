import sys
sys.path.append('.')
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer_attach_offset import FileRecognizerAttchOffset
from dejavu.ultilities.helper import recreate_folder

config = {
    "database": {
        "host": "db",
        "user": "postgres",
        "password": "password",
        "database": "dejavu"
    },
    "database_type": "postgres"
}

data_dir = 'app/data'
result_dir = 'app/results'

if __name__ == '__main__':
    djv = Dejavu(config)

    # recognize_file = 'app/data/Without My Money.mp3'
    recognize_file = 'app/query/Without His Friends1.mp3'
    # recognize_file = 'app/query/Without His Friends.wav'
    # recognize_file = 'mp3/3z2Ovv5OV4U.mp3'
    # recognize_file = 'app/data/Without Your Everythi.wav'

    frao = FileRecognizerAttchOffset(djv, topq=1, throld_find=2)
    results = frao.recognize_result(recognize_file)

    recreate_folder(result_dir)

    is_match = False
    print(f'align_time : {results.align_time}')
    print(f'query_time : {results.query_time}')
    for idex_s, value in enumerate(results.matches):
        song_name = value.song_name.decode('utf-8')
        song_path = f'{data_dir}/{song_name}'
        songs = [song_path, recognize_file]
        for song_q in value.offsets:
            for idex, song_seg in enumerate(song_q):
                for idx2, song in enumerate(song_seg.all()):
                    is_match = True
                    file_out = f"{result_dir}/s{idex_s}_c{song_seg.count}_{song_name}_seg{idex}_{idx2}_{song.start_time}_{song.end_time}.mp3"
                    song.save(songs[idx2], file_out)
