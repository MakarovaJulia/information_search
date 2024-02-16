import requests
from bs4 import BeautifulSoup
import re
import os


# Берем ссылки со страницы
def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [link.get('href') for link in soup.find_all('a', href=True)]
    return links


# Качаем html
def download_html(url, file_name):
    response = requests.get(url)
    folder_name = 'html'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_path = os.path.join(folder_name, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response.text)


# Записываем ссылки в файл index
def write_to_file(num, url, file_name):
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(str(num) + '. ' + str(num) + '.html' + ' ' + '<a href="' + str(url) + '">' + str(num) + '</a>' + '\n')


def main():
    # Берем страницу сайта и все ссылки с нее
    base_url = 'http://fan.lib.ru/type/index_type_3-1.shtml'
    links = get_links(base_url)
    more_links = []
    count = 1
    index_file = 'index.txt'
    # Проходимся по ссылкам и сохраняем контент в файлы
    for link in links:
        pattern = r'^/[a-z]/'
        if re.search(pattern, link):
            if count < 151:
                link = 'http://fan.lib.ru' + link
                file_name = str(count) + '.html'
                download_html(link, file_name)
                write_to_file(count, link, index_file)
                count = count + 1
            else:
                break

if __name__ == "__main__":
    main()
