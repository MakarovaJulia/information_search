import re
from collections import deque
from pymorphy2 import MorphAnalyzer

# not начинающий or (справка and рейтинг)
def read_from_file(filename):
    inverted_index = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            lemma, file_num = line.strip().split(':')
            file_num = file_num.strip().split(', ')
            inverted_index[lemma] = set(file_num)
    return inverted_index

def apply_operator(operator, stack):
    # Применение указанного оператора к операндам в стеке
    if operator == "AND":
        operand2 = stack.pop()
        operand1 = stack.pop()
        result = set(operand1) & set(operand2)
        stack.append(result)
    elif operator == "OR":
        operand2 = stack.pop()
        operand1 = stack.pop()
        result = set(operand1) | set(operand2)
        stack.append(result)
    elif operator == "NOT":
        operand = stack.pop()
        result = set(inverted_index.keys()) - set(operand)
        stack.append(result)

def priority(operator):
    # Определение приоритета операторов
    if operator == "NOT":
        return 3
    elif operator == "AND":
        return 2
    elif operator == "OR":
        return 1
    else:
        return 0

def boolean_search(expression, inverted_index):
    # Инициализация MorphAnalyzer для нормализации слов
    morph = MorphAnalyzer()
    # Инициализация стека для хранения операндов
    stack = []
    # Инициализация стека для хранения операторов
    operator_stack = deque()
    tokens = re.findall(r'\(|\)|\w+|[^\s\w]', expression)
    # Инициализация индекса для обработки токенов
    index = 0

    def process_token():
        nonlocal index
        if index < len(tokens): # Проверяем, есть ли еще токены для обработки
            token = tokens[index]  # Получаем текущий токен
            index += 1 # Переходим к следующему токену
            if token in ['AND', 'OR', 'NOT', '(', ')']:
                # Если токен является оператором
                if token == '(':
                    # Помещаем открывающую скобку в стек операторов
                    operator_stack.append(token)
                elif token == ')':
                    while operator_stack and operator_stack[-1] != '(':
                        # Применяем операторы до достижения соответствующей открывающей скобки
                        apply_operator(operator_stack.pop(), stack)
                    operator_stack.pop()
                else:
                    operator = token
                    # Проверяем и применяем операторы в зависимости от приоритета
                    if operator_stack and priority(operator) <= priority(operator_stack[-1]):
                        apply_operator(operator_stack.pop(), stack)
                    operator_stack.append(token)
                # Рекурсивно обрабатываем следующий токен
                process_token()

            else:
                # Если все токены обработаны, нормализуем последнее слово и добавляем его в стек
                token = morph.parse(token)[0].normal_form
                stack.append(inverted_index.get(token, {'0'}))
                # Рекурсивно обрабатываем оставшиеся операции
                process_token()

    # Начало рекурсивной обработки токенов
    process_token()

    while operator_stack:
        apply_operator(operator_stack.pop(), stack)

    return sorted(stack[-1], key=int)

inverted_index = read_from_file('inverted_index.txt')
query = input()
result = boolean_search(query, inverted_index)

with open('index.txt', 'r') as file:
    links = file.read().splitlines()

if result and not (len(result) == 1 and result[0] == '0'):
    print('Найдены страницы ')
    for item in result:
        if item != '0':
            print(links[int(item) - 1])
        else:
            print('Ничего не найдено')