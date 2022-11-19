from typing import Dict
from io import StringIO
import gallicaGetter
import random
from collections import deque, Counter


def get_gallica_core(root_gram, distance, sample_size, start_date, end_date) -> Dict:
    text_to_analyze = get_sample_text(root_gram, sample_size, start_date, end_date)
    notable_words_in_distance = get_associated_words(text_to_analyze, root_gram, distance)
    return notable_words_in_distance


def get_sample_text(root_gram, sample_size, start_date, end_date) -> StringIO:

    def get_text_for_codes(volume_codes) -> str:
        text_wrapper = gallicaGetter.connect('text')
        text = ''
        for code in volume_codes:
            text_record = text_wrapper.get(code)
            text += text_record.get_text()
        return text

    sru_wrapper = gallicaGetter.connect('sru')
    num_volumes_with_root_gram = sru_wrapper.get(
        term=root_gram,
        startDate=start_date,
        endDate=end_date
    )
    indices_to_sample = random.sample(range(num_volumes_with_root_gram), sample_size)
    volumes_with_root_gram = sru_wrapper.get(
        term=root_gram,
        startDate=start_date,
        endDate=end_date,
        startRecord=indices_to_sample
    )
    volume_codes = (volume_record.get_code() for volume_record in volumes_with_root_gram)
    return StringIO(get_text_for_codes(volume_codes))


def get_associated_words(text_to_analyze: StringIO, root_gram, distance) -> Dict:
    text_to_analyze.seek(0)
    word_counts = {}
    words_in_window = []
    current_word = ''
    for char in text_to_analyze.read():
        char = char.lower()
        if char == ' ':
            if current_word != '':
                words_in_window.append(current_word)
                current_word = ''
                if len(words_in_window) > distance:
                    words_in_window.pop(0)
        else:
            current_word += char
            if current_word == root_gram:
                next_words = []
                current_word = ''
                while len(next_words) < distance:
                    char = text_to_analyze.read(1)
                    if char == ' ':
                        next_words.append(current_word)
                        current_word = ''
                    else:
                        current_word += char
                words_in_window += next_words
                word_counts.update(Counter(words_in_window))
                words_in_window = next_words
    return word_counts



