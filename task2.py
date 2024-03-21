import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pymorphy2
import re
from bs4 import BeautifulSoup

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# список токенов
tokens = list()


def get_tokens(page):
    with open(page, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser').find('body')

    # удаляем ненужные теги
    for script in soup(["script", "style", "a", "span", "button", "label", "footer", "article"]):
        script.extract()

    # извлеакем текст из HTML, удаляем все пробелы и переносы
    text = soup.get_text(separator=' ', strip=True)

    # токенизация текста
    tokens_in_page = word_tokenize(text)

    # приводим токены к нижнему регистру, оставляем только слова
    tokens_in_page = [word.lower() for word in tokens_in_page if word.isalpha()]

    # оставляем только русские слова
    russian_pattern = re.compile('[а-яА-ЯёЁ]+')
    tokens_in_page = [word for word in tokens_in_page if russian_pattern.match(word)]

    # удаляем стоп-слов
    stop_words = stopwords.words("russian")
    tokens_in_page = [word for word in tokens_in_page if word not in stop_words]

    return tokens_in_page


# группировка токенов по леммам
def group_tokens_by_lemmas(unique_tokens):
    # инициализация объекта pymorphy2 для лемматизации
    morph = pymorphy2.MorphAnalyzer()
    lemma_tokens = {}

    for token in unique_tokens:
        # находим лемму для каждого токена
        parsed_token = morph.parse(token)[0]
        lemma = parsed_token.normal_form

        # группируем токены по леммам
        if lemma not in lemma_tokens:
            lemma_tokens[lemma] = []
        lemma_tokens[lemma].append(token)

    return lemma_tokens


def main():
    # извлечение токенов из каждой страницы
    for i in range(1, 150):
        page_tokens = get_tokens(f'html/{i}.html')
        tokens.extend(page_tokens)

    # список уникальных токенов
    unique_tokens = list(set(tokens))

    # группировка токенов по леммам
    grouped_tokens = group_tokens_by_lemmas(unique_tokens)

    # запись уникальных токенов в файл
    with open('tokens.txt', 'w', encoding='utf-8') as file:
        for token in unique_tokens:
            file.write(token + '\n')

    # запись групп токенов по леммам в файл
    with open('lemmas.txt', 'w', encoding='utf-8') as file:
        for key, values in grouped_tokens.items():
            values_str = ' '.join(values)
            file.write(f"{key}: {values_str}\n")


if __name__ == "__main__":
    main()
