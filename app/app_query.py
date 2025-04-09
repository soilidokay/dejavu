from typing import Generator
from dejavu.ultilities.helper import create_folder, recreate_folder
from dejavu.logic.recognizer.file_recognizer_attach_offset import FileRecognizerAttchOffset
from dejavu import Dejavu
import os
import sys

from dejavu.ultilities.result_process import song_result
sys.path.append('.')

config = {
    "database": {
        "host": "db",
        "user": "postgres",
        "password": "password",
        "database": "dejavu"
    },
    "database_type": "postgres"
}

# data_dir = 'app/data2'
data_source_index_dir = os.environ.get('SOURCE_INDEX', 'data/source')
data_dir = os.environ.get('DATA_INDEX', 'data/index')
result_dir = os.environ.get('DATA_RESULT', 'data/results')
create_folder(data_dir)
create_folder(result_dir)


def match_and_save_segments(djv, recognize_file, data_dir, result_dir, topq=1, throld_find=10):
    """
    Hàm nhận diện và lưu các đoạn giống nhau từ file truy vấn và tập dữ liệu.

    Args:
        djv: Đối tượng Dejavu đã khởi tạo
        recognize_file: Đường dẫn tới file audio cần truy vấn
        data_dir: Thư mục chứa dữ liệu đã đánh fingerprint
        result_dir: Thư mục để lưu kết quả
        topq: Số lượng kết quả top cần lấy
        throld_find: Ngưỡng thời gian tối thiểu để coi là trùng khớp (đơn vị: giây)

    Returns:
        is_match (bool): Có khớp hay không
        results (object): Kết quả khớp chi tiết từ FileRecognizerAttchOffset
    """

    # Nhận diện đoạn khớp
    frao = FileRecognizerAttchOffset(djv, topq=topq, throld_find=throld_find)
    results = frao.recognize_result(recognize_file)

    recreate_folder(result_dir)

    is_match = False
    print(f'align_time : {results.align_time}')
    print(f'query_time : {results.query_time}')

    for idex_s, value in enumerate(results.matches):
        song_name = value.song_name.decode('utf-8')
        song_path = os.path.join(data_dir, song_name)
        songs = [song_path, recognize_file]

        for song_q in value.offsets:
            for idex, song_seg in enumerate(song_q):
                for idx2, song in enumerate(song_seg.all()):
                    is_match = True
                    file_out = os.path.join(
                        result_dir,
                        f"s{idex_s}_c{song_seg.count}_{song_name}_seg{idex}_{idx2}_{song.start_time}_{song.end_time}.mp3"
                    )
                    song.save(songs[idx2], file_out)

    return is_match, results


def match_and_save_segments2(djv, recognize_file, data_dir, result_dir, topq=1, throld_find=10):
    """
    Hàm nhận diện và lưu các đoạn giống nhau từ file truy vấn và tập dữ liệu.

    Args:
        djv: Đối tượng Dejavu đã khởi tạo
        recognize_file: Đường dẫn tới file audio cần truy vấn
        data_dir: Thư mục chứa dữ liệu đã đánh fingerprint
        result_dir: Thư mục để lưu kết quả
        topq: Số lượng kết quả top cần lấy
        throld_find: Ngưỡng thời gian tối thiểu để coi là trùng khớp (đơn vị: giây)

    Returns:
        is_match (bool): Có khớp hay không
        results (object): Kết quả khớp chi tiết từ FileRecognizerAttchOffset
    """

    # Nhận diện đoạn khớp
    frao = FileRecognizerAttchOffset(djv, topq=topq, throld_find=throld_find)
    results = frao.recognize_result(recognize_file)

    recreate_folder(result_dir)

    is_match = False
    print(f'align_time : {results.align_time}')
    print(f'query_time : {results.query_time}')

    # for idex_s, value in enumerate(results.matches):
    #     song_name = value.song_name.decode('utf-8')
    #     song_path = os.path.join(data_dir, song_name)
    #     songs = [song_path, recognize_file]

    #     for song_q in value.offsets:
    #         for idex, song_seg in enumerate(song_q):
    #             for idx2, song in enumerate(song_seg.all()):
    #                 is_match = True
    #                 file_out = os.path.join(
    #                     result_dir,
    #                     f"s{idex_s}_c{song_seg.count}_{song_name}_seg{idex}_{idx2}_{song.start_time}_{song.end_time}.mp3"
    #                 )
    #                 song.save(songs[idx2], file_out)
    def results_song_enum():
        for idex_s, value in enumerate(results.matches):
            song_name = value.song_name.decode('utf-8')
            song_path = os.path.join(data_dir, song_name)
            songs = [song_path, recognize_file]
            for song_q in value.offsets:
                for idex, song_seg in enumerate(song_q):
                    for idx2, song in enumerate(song_seg.all()):
                        is_match = True
                        file_out = os.path.join(
                            result_dir,
                            f"s{idex_s}_c{song_seg.count}_{song_name}_seg{idex}_{idx2}_{song.start_time}_{song.end_time}.mp3"
                        )
                        song.save(songs[idx2], file_out)
            yield value

    return is_match, results, results_song_enum()
