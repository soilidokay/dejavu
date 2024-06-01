from time import time
from typing import Dict, List, Tuple

import numpy as np

from dejavu import Dejavu
import dejavu.logic.decoder as decoder
from dejavu.base_classes.base_recognizer import BaseRecognizer
from dejavu.config.settings import (ALIGN_TIME, FINGERPRINT_TIME, QUERY_TIME,
                                    RESULTS, TOPN, TOPQ, TOTAL_TIME, THROLD_CONTINUOUS_ARRAY, QUERY_MIN_SECOND)
from dejavu.ultilities.result_process import result_process


class FileRecognizerAttchOffset(BaseRecognizer):
    def __init__(self, dejavu: Dejavu, topn=TOPN, topq=TOPQ, throld_find=THROLD_CONTINUOUS_ARRAY, min_second=QUERY_MIN_SECOND):
        super().__init__(dejavu)
        self._dejavu = dejavu
        self.top_seg = topq
        self.top_n = topn
        self.throld_find = topn
        self.min_second = min_second

    def _recognize2(self, *data,) -> Tuple[List[Dict[str, any]], int, int, int]:
        fingerprint_times = []
        hashes = set()  # to remove possible duplicated fingerprints we built a set.
        for channel in data:
            fingerprints, fingerprint_time = self._dejavu.generate_fingerprints(channel, Fs=self.Fs)
            fingerprint_times.append(fingerprint_time)
            hashes |= set(fingerprints)

        matches, dedup_hashes, query_time = self._dejavu.find_matches_attach_offset(hashes)

        t = time()
        final_results = self._dejavu.align_matches_attach_offset(
            matches, dedup_hashes, len(hashes), topn=self.top_n, topq=self.top_seg, throld_find=self.throld_find, min_second=self.min_second)
        align_time = time() - t

        return final_results, np.sum(fingerprint_times), query_time, align_time

    def recognize_file(self, filename: str) -> Dict[str, any]:
        channels, self.Fs, _ = decoder.read(filename, self._dejavu.limit)

        t = time()
        matches, fingerprint_time, query_time, align_time = self._recognize2(*channels)
        t = time() - t

        results = {
            TOTAL_TIME: t,
            FINGERPRINT_TIME: fingerprint_time,
            QUERY_TIME: query_time,
            ALIGN_TIME: align_time,
            RESULTS: matches
        }

        return results

    def recognize(self, filename: str) -> Dict[str, any]:
        return self.recognize_file(filename)

    def recognize_result(self, filename) -> result_process:
        result = self.recognize_file(filename)
        return result_process(result)
