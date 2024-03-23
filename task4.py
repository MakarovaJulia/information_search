import math
import os
from collections import Counter

import nltk
import pymorphy2
from task2 import get_tokens

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Инициализация лемматизатора
morph = pymorphy2.MorphAnalyzer()

html_folder = "html"  # Путь к папке с файлами документов
lemmas_tf_idf = "lemmas_tf-idf"  # tf-idf для лемм
tokens_tf_idf = "tokens_tf-idf"  # tf-idf для токенов
inverted_index_lemmas = "inverted_index.txt"
inverted_index_tokens = "inverted_tokens_index.txt"
number_of_docs = 150


def create_inverted_index_tokens():
    index = {}

    for i in range(1, number_of_docs + 1):
        html_file = f'html/{i}.html'
        tokens = get_tokens(html_file)
        unique_tokens = list(set(tokens))

        for token in unique_tokens:
            if token in index:
                index[token].append(i)
            else:
                index[token] = [i]

    with open(inverted_index_tokens, 'w') as output_file:
        for i in index:
            output_file.write(i + ": " + ", ".join(map(lambda file_number: str(file_number), index[i])) + "\n")


def inverted_index_count(file):
    token_pages = {}
    for line in file:
        token, pages = line.strip().split(': ')
        pages_list = [int(page) for page in pages.split(', ')]
        token_pages[token] = len(pages_list)
    return token_pages


def get_counts(tokens):
    token_counts = Counter(tokens)
    # Лемматизация токенов
    lemmas = [morph.parse(token)[0].normal_form for token in tokens]
    lemma_counts = Counter(lemmas)
    return token_counts, lemma_counts


def calculate_tf(counts):
    total_tokens = sum(counts.values())
    tf = {token: count / total_tokens for token, count in counts.items()}
    return tf


def calculate_idf(counts, pages):
    idf_data = {}
    for token, count in counts.items():
        if token in pages:
            idf_data[token] = math.log(number_of_docs / pages[token])
        else:
            idf_data[token] = 0
    return idf_data


def main():
    # create_inverted_index_tokens()

    if not os.path.exists(lemmas_tf_idf):
        os.makedirs(lemmas_tf_idf)

    if not os.path.exists(tokens_tf_idf):
        os.makedirs(tokens_tf_idf)

    with open(inverted_index_lemmas, 'r', encoding='utf-8') as file:
        lemmas_count_per_pages = inverted_index_count(file)

    with open(inverted_index_tokens, 'r', encoding='utf-8') as file:
        tokens_count_per_pages = inverted_index_count(file)

    # Обработка каждого файла выкачки
    for i in range(1, number_of_docs + 1):
        html_file = f'html/{i}.html'
        tokens = get_tokens(html_file)
        # Counter для токенов и для лемм в текущем документе
        token_counts, lemma_counts = get_counts(tokens)

        # Вычисление TF, IDF для лемм
        tf_lemma = calculate_tf(lemma_counts)
        idf_lemma = calculate_idf(lemma_counts, lemmas_count_per_pages)

        # Вычисление TF, IDF для токенов
        tf_tokens = calculate_tf(token_counts)
        idf_tokens = calculate_idf(token_counts, tokens_count_per_pages)

        # Запись результатов в файл для лемм
        with open(os.path.join(lemmas_tf_idf, f"{i}_lemmas.txt"), 'w',
                  encoding='utf-8') as output_file:
            for lemma, res in tf_lemma.items():
                output_file.write(f"{lemma} {idf_lemma[lemma]} {tf_lemma[lemma] * idf_lemma[lemma]}\n")

        # Запись результатов в файл для токенов
        with open(os.path.join(tokens_tf_idf, f"{i}_tokens.txt"), 'w',
                  encoding='utf-8') as output_file:
            for token, res in tf_tokens.items():
                output_file.write(f"{token} {idf_tokens[token]} {tf_tokens[token] * idf_tokens[token]}\n")


if __name__ == "__main__":
    main()
