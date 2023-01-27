from typing import Dict, List
from io import StringIO
import gallicaGetter
import random
from collections import Counter
from gallicaGetter.gallicaWrapper import VolumeOccurrenceWrapper
import os

here = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(here, "stopwordsFR.txt"), "r") as stopwords_file:
    stopwords_fr = set(stopwords_file.read().splitlines())
with open(os.path.join(here, "stopwordsEN.txt"), "r") as stopwords_file:
    stopwords_en = set(stopwords_file.read().splitlines())


def get_gallica_core(
    root_gram: str,
    distance: int,
    start_date: str,
    end_date: str,
    sample_size: int = 20,
    api_wrapper=gallicaGetter,
    onUpdateProgress=None,
) -> Dict:

    text_to_analyze = get_sample_text(
        root_gram, sample_size, start_date, end_date, api_wrapper, onUpdateProgress
    )
    notable_words_in_distance = get_associated_words(
        text_to_analyze, root_gram, distance
    )
    return notable_words_in_distance


def get_sample_text(
    root_gram: str,
    sample_size: int,
    start_date: str,
    end_date: str,
    api_wrapper,
    onUpdateProgress=None,
) -> StringIO:
    def get_text_for_codes(codes: List[str]) -> str:
        text_wrapper = api_wrapper.connect("text")
        text = ""
        text_records = text_wrapper.get(
            codes, onUpdateProgress=lambda x: print(x.elapsed_time)
        )
        for record in text_records:
            text += record.get_text()
        return text

    sru_wrapper: VolumeOccurrenceWrapper = api_wrapper.connect("volume")
    num_volumes_with_root_gram = sru_wrapper.get_num_results_for_args(
        terms=root_gram,
        start_date=start_date,
        end_date=end_date,
        grouping="all",
    )
    num_volumes = sum(query.num_results for query in num_volumes_with_root_gram)
    indices_to_sample = random.sample(range(num_volumes), sample_size)
    volumes_with_root_gram = sru_wrapper.get(
        terms=root_gram,
        start_date=start_date,
        end_date=end_date,
        start_index=indices_to_sample,
        onProgressUpdate=onUpdateProgress,
    )
    volume_codes = [
        volume_record.paper_code for volume_record in volumes_with_root_gram
    ]
    return StringIO(get_text_for_codes(volume_codes))


def get_associated_words(
    text_to_analyze: StringIO, root_gram: str, distance: int
) -> Dict:
    word_counts = {}
    text_to_analyze.seek(0)
    words_in_window = []
    current_word = ""
    root_behind = False
    compare_index = 0
    current_word_delta = 0

    def count_window(word_window):
        for word, count in Counter(word_window).items():
            if word in word_counts:
                word_counts[word] += count
            else:
                word_counts[word] = count
        return []

    def reset_current_word():
        nonlocal current_word
        nonlocal current_word_delta
        nonlocal compare_index
        current_word = ""
        current_word_delta = 0
        compare_index = 0

    def update_window(new_word):
        nonlocal words_in_window
        nonlocal root_behind
        if new_word not in stopwords_fr and new_word not in stopwords_en:
            words_in_window.append(new_word)
            if len(words_in_window) > distance:
                words_in_window.pop(0)
        if len(words_in_window) == distance:
            if root_behind:
                words_in_window = count_window(words_in_window)
                root_behind = False
        reset_current_word()

    for char in text_to_analyze.read():
        char = char.lower()
        if not char.isalpha():
            if current_word:
                update_window(current_word)
        else:
            if compare_index < len(root_gram) and root_gram[compare_index] != char:
                current_word_delta += 1
            compare_index += 1
            current_word += char
            if compare_index == len(root_gram) and current_word_delta <= 1:
                reset_current_word()
                words_in_window = count_window(words_in_window)
                root_behind = True
    if current_word:
        update_window(current_word)
    return word_counts
