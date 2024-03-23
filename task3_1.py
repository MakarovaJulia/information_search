import re
from task2 import get_tokens

def create_inverted_index(lemmas):
    inverted_index = {}

    # Читаем список лемм из файла
    with open(lemmas, 'r', encoding='utf-8') as f:
        terms = f.read().splitlines()

    # Проходим по всем файлам
    for i in range(1, 151):
        html_file = f'html/{i}.html'
        text = get_tokens(html_file)
        # Проверяем каждое слово из списка в тексте
        for word in text:
            for term in terms:
                pattern = r'\b' + re.escape(word) + r'\b'
                match = re.search(pattern, term)
                lemma = term.split()[0]
                num = re.search(r'\d+', html_file).group()
                if match:
                    if lemma in inverted_index:
                        inverted_index[lemma].add(num)
                    else:
                        inverted_index[lemma] = {num}
        print(i)
    with open('inverted_index.txt', 'w', encoding='utf-8') as file:
        for key, value in inverted_index.items():
            # Делаем из множества строку
            value = sorted(value, key=int)
            value_str = ', '.join(str(v) for v in value)
            file.write(f"{key} {value_str}\n")


create_inverted_index('lemmas.txt')

