import os
from collections import Counter
import pandas as pd
import numpy as np
import re
import operator
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from task4 import inverted_index_count, calculate_tf, calculate_idf
from task4 import morph

lemmas_file = "lemmas.txt"
lemmas_tf_idf = "lemmas_tf-idf"  # tf-idf для лемм
inverted_index_lemmas = "inverted_index.txt"
words = []
number_of_docs = len(os.listdir(lemmas_tf_idf))

with open(lemmas_file, 'r') as file:
    # количество строк в лемма файле
    line_count = sum(1 for line in file)

number_of_words = line_count


def create_vector_matrix():
    # print(number_of_docs)
    with open(lemmas_file, 'r') as file1:
        lemmas = file1.read().splitlines()
        for lemma in lemmas:
            lemma = lemma.split(':')
            words.append(lemma[0])

    # датафрейм, где строки - номера файлов, столбцы - леммы, а значения ячеек это tf-idf
    _df_tf_idf = pd.DataFrame(np.zeros((number_of_docs + 1, number_of_words)), columns=words)

    for i in range(1, number_of_docs + 1):
        with open(os.path.join(lemmas_tf_idf, f'{i}_lemmas.txt'), 'r') as file2:
            document = file2.read().splitlines()
            for line in document:
                line = line.split()
                word = line[0]
                tf_idf = round(float(line[2]), 8)
                _df_tf_idf.loc[i, word] = tf_idf

    return _df_tf_idf


df_tf_idf = create_vector_matrix()

with open(inverted_index_lemmas, 'r') as file:
    lemmas_count_per_pages = inverted_index_count(file)


def preprocess_query(query):
    tokens_in_query = word_tokenize(query)
    tokens_in_query = [word.lower() for word in tokens_in_query if word.isalpha()]
    russian_pattern = re.compile('[а-яА-ЯёЁ]+')
    tokens_in_query = [word for word in tokens_in_query if russian_pattern.match(word)]
    stop_words = stopwords.words("russian")
    tokens_in_query= [word for word in tokens_in_query if word not in stop_words]
    return tokens_in_query


def get_lemma_counts(tokens):
    # Лемматизация токенов
    lemmas = [morph.parse(token)[0].normal_form for token in tokens]
    lemma_counts = Counter(lemmas)
    return lemma_counts


def calculate_tf_idf(tf, idf):
    tf_idf = {}
    for lemma, res in tf.items():
        tf_idf[lemma] = tf[lemma] * idf[lemma]
    return tf_idf


# Вычисляем косинусное сходство вектора запроса и векторов документов
def calculate_similarities(query):
    tokens_query = preprocess_query(query)
    lemma_counts = get_lemma_counts(tokens_query)
    # Вычисляем tf запроса
    tf_lemma_query = calculate_tf(lemma_counts)
    # Вычисляем idf запроса
    idf_lemma_query = calculate_idf(lemma_counts, lemmas_count_per_pages)
    # Получаем tf-idf
    result = calculate_tf_idf(tf_lemma_query, idf_lemma_query)


    # Преобразуем словарь в DataFrame
    vector_df = pd.DataFrame.from_dict(result, orient='index', columns=['вектор'])
    vector_df = vector_df.reindex(df_tf_idf.columns, fill_value=0.0)

    # Вычисляем косинусное сходство
    cos_sim = cosine_similarity(vector_df.values.reshape(1, -1), df_tf_idf.values)

    similarity_dict = {}

    # список номеров файлов
    file_numbers = df_tf_idf.index.tolist()

    # Для каждого файла перебираем соответствующие ему значения косинусного сходства
    for file_number, similarity_value in zip(file_numbers, cos_sim[0]):
        similarity_dict[file_number] = similarity_value
    return dict(sorted(similarity_dict.items(), key=operator.itemgetter(1), reverse=True))


def get_top_k_dict(dictionary, k):
    top_k_dict = {item: dictionary[item] for item in list(dictionary)[:k]}
    return top_k_dict


# Обрабатываем запрос
while True:
    query = input("Введите запрос: ")
    if query.lower() == 'exit':
        exit()
    try:
        result = calculate_similarities(query)
        result = get_top_k_dict(result, 10)
        dict_items = result.items()
        i = 1
        with open('index.txt', 'r') as file:
            links = file.read().splitlines()
            for key, value in dict_items:
                if value > 0:
                    print(f'{i}.', links[int(key) - 1])
                    i += 1
    except Exception as e:
        print(f"Error occurred: {e}. Please try again")

