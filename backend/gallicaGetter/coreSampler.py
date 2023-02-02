from typing import Dict, List
from io import StringIO
import random
from collections import Counter
from wrapperFactory import WrapperFactory
from collections import Counter
from bs4 import BeautifulSoup
import os

here = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(here, "stopwordsFR.txt"), "r") as stopwords_file:
    stopwords_fr = set(stopwords_file.read().splitlines())
with open(os.path.join(here, "stopwordsEN.txt"), "r") as stopwords_file:
    stopwords_en = set(stopwords_file.read().splitlines())


def get_gallica_core(
    root_gram: str,
    start_date: str,
    end_date: str,
    sample_size: int = 50,
    onUpdateProgress=None,
    api_wrapper: WrapperFactory | None = None,
) -> Dict[str, int]:
    """An experimental tool that returns the most frequent words in the surrounding context of a target word occurrence."""
    if api_wrapper is None:
        api_wrapper = WrapperFactory()
    text_to_analyze = get_sample_text(
        root_gram, sample_size, start_date, end_date, api_wrapper, onUpdateProgress
    )
    notable_words_in_distance = get_associated_words(text_to_analyze, root_gram)
    return notable_words_in_distance


def get_sample_text(
    root_gram: str,
    sample_size: int,
    start_date: str,
    end_date: str,
    api_wrapper: WrapperFactory,
    onUpdateProgress=None,
) -> StringIO:
    def get_text_for_codes(codes: List[str], target_word: str) -> str:
        text_wrapper = api_wrapper.context()
        text = ""
        text_records = text_wrapper.get([(code, target_word) for code in codes])
        for record in text_records:
            for page in record.pages:
                soup = BeautifulSoup(page.context, "html.parser")
                text += soup.get_text()
        return text

    volume_wrapper = api_wrapper.volume()
    num_volumes_with_root_gram = volume_wrapper.get_num_results_for_args(
        terms=[root_gram],
        start_date=start_date,
        end_date=end_date,
        grouping="all",
    )
    num_volumes = sum(query.gallica_results_for_params for query in num_volumes_with_root_gram)
    indices_to_sample = random.sample(range(num_volumes), sample_size)
    volumes_with_root_gram = volume_wrapper.get(
        terms=[root_gram],
        start_date=start_date,
        end_date=end_date,
        start_index=indices_to_sample,
        onProgressUpdate=onUpdateProgress,
    )
    volume_codes = [
        volume_record.url.split("/")[-1] for volume_record in volumes_with_root_gram
    ]
    return StringIO(get_text_for_codes(codes=volume_codes, target_word=root_gram))


def get_associated_words(text_to_analyze: StringIO, root_gram: str) -> Dict:
    counts = Counter(text_to_analyze.read().split())
    counts = {k.lower(): v for k, v in counts.items()}
    for stopword in stopwords_fr | stopwords_en:
        counts.pop(stopword, None)
    counts = {k: v for k, v in counts.items() if k.isalnum()}
    for word in root_gram.split():
        counts.pop(word, None)
    return counts


if __name__ == "__main__":
    test = get_gallica_core("paix", "1941", "1946")
    print(Counter(test).most_common(10))
