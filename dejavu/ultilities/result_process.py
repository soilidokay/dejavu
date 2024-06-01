from typing import List, Tuple, Generator

from Ultilities.helper import extract_audio_segment
from dejavu.config.settings import ALIGN_TIME, FIELD_FILE_SHA1, FIELD_OFFSETS, FINGERPRINT_TIME, FINGERPRINTED_CONFIDENCE, FINGERPRINTED_HASHES, HASHES_MATCHED, INPUT_CONFIDENCE, INPUT_HASHES, QUERY_TIME, RESULTS, SONG_ID, SONG_NAME, TOTAL_TIME


class match_song:
    def __init__(self, results: List[float], count: int):
        self.results = results
        self.count = count

    def all(self):
        return [self.original, self.matched]

    @property
    def original(self):
        return song_segment(self.results[0])

    @property
    def matched(self):
        return song_segment(self.results[1])


class song_segment:
    def __init__(self, results: List[float]):
        self.results = results

    @property
    def start_time(self):
        return self.results[0]

    @property
    def end_time(self):
        return self.results[1]

    def save(self, source_file, filename):
        extract_audio_segment(source_file, self.start_time, self.end_time, filename)
        print(
            f"Extracted segment from {self.start_time} to {self.start_time} seconds. {filename}")


class song_result:
    def __init__(self, results: dict):
        self.results = results

    @property
    def song_id(self):
        return self.results.get(SONG_ID, None)

    @property
    def song_name(self) -> bytes:
        return self.results.get(SONG_NAME, None)

    @property
    def input_hashes(self):
        return self.results.get(INPUT_HASHES, None)

    @property
    def fingerprinted_hashes(self):
        return self.results.get(FINGERPRINTED_HASHES, None)

    @property
    def hashes_matched(self):
        return self.results.get(HASHES_MATCHED, None)

    @property
    def input_confidence(self):
        return self.results.get(INPUT_CONFIDENCE, None)

    @property
    def fingerprinted_confidence(self):
        return self.results.get(FINGERPRINTED_CONFIDENCE, None)

    @property
    def file_sha1(self):
        return self.results.get(FIELD_FILE_SHA1, None)

    @property
    def offsets(self) -> Generator[List[match_song], None, None]:
        offsets = self.results.get(FIELD_OFFSETS, [])
        for count, value in offsets:
            buff = []
            for v2 in value:
                buff.append(match_song(v2, count))
            yield buff


class result_process:
    def __init__(self, results: dict):
        self.results = results

    @property
    def total_time(self):
        return self.results.get(TOTAL_TIME, None)

    @property
    def fingerprint_time(self):
        return self.results.get(FINGERPRINT_TIME, None)

    @property
    def query_time(self):
        return self.results.get(QUERY_TIME, None)

    @property
    def align_time(self):
        return self.results.get(ALIGN_TIME, None)

    @property
    def matches(self) -> Generator[song_result, None, None]:
        temp = self.results.get(RESULTS, [])
        for i in temp:
            yield song_result(i)
