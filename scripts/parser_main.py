"""Код собирает данные со всех страниц и категорий на сайте тренажере 
(parsinger.ru) и сохраняет всё в таблицу CSV."""
# region импорты
from collections import namedtuple
import logging
import csv

from bs4 import BeautifulSoup, Tag
from requests import get
import lxml
# endregion

# region НАСТРОЙКИ ДЛЯ РЕВЬЮЕРА
NAME_FILE = 'res.csv'  # Названия файла
INFO_MODE = False  # Вывод информации на консоль
# endregion

# region приватные переменные
__PRODUCT = namedtuple('Product',
                       ['name',
                        'param_1',
                        'param_2',
                        'param_3',
                        'param_4',
                        'price'])
# endregion


def GetResponse(url: str) -> str:
    """Возвращает текст c указанного сайта\n
    в случае ошибки выведет статус код на консоль

    Args:
        url (str): ссылка на сайт от куда нужно получить текст

    Returns:
        str: Возвращает строку с исходной страницы запроса, 
        в случае ошибке вернёт пустую строку
    """
    response = get(url=url)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        return response.text
    else:
        logging.error(f"Ответ от сервера: {response.status_code}")
        logging.warning('Возврат пустой строки!')
        return ''


def CookingSoup(html_text: str) -> BeautifulSoup:
    """Варит суп

    Args:
        html_text (str): Исходный текст HTML страницы

    Returns:
        BeautifulSoup: Сваренный суп
    """
    soup = BeautifulSoup(html_text, 'lxml')
    logging.debug('Суп сварен')
    return soup


def GetListProducts(soup: BeautifulSoup) -> list[namedtuple]:
    """Получить список из супа.

    Args:
        soup (BeautifulSoup): Вкусный суп с полезной информацией

    Returns:
        list[namedtuple]: Лист с продуктами
    """
    products = []
    for item_card in soup.select('.item'):
        product = __PRODUCT(item_card.select_one('.name_item').text.strip(),
                            *[param.text.strip()
                              for param in item_card.select('.description li')],
                            item_card.select_one('.price').text)
        products.append(product)
    logging.info(f"Собрано {len(products)} товаров.")
    return products


def CreateCsvFile(name_file: str) -> bool:
    """Создаёт новый файл csv для записи

    Args:
        name_file (str): путь/название файла

    Returns:
        bool: успешность выполнения
    """
    try:
        with open(file=name_file, mode='w',
                  encoding='utf-8-sig',
                  newline='') as file:
            # ? Добавление заголовка
            logging.info('Файл создан')
            return True
    except Exception as ex:
        logging.error(f"ФАЙЛ НЕ СОЗДАН! \n ошибка: {ex}")
        return False


def WriteProductsInFile(name_file: str, products: list[namedtuple]) -> bool:
    """Совершает запись в файл

    Args:
        name_file (str): путь/название файла
        products (list[namedtuple]): список продуктов из namedtuple

    Returns:
        bool: Успешность выполнения
    """
    try:
        with open(name_file,
                  mode='a',
                  encoding='utf-8-sig',
                  newline='') as file:
            writer = csv.writer(file, dialect='excel')
            for product in products:
                writer.writerow(product)
            logging.info('\tПроизведена запись в файл.')
            return True
    except:
        return False


def GenerateUrl(number_category: str = 1, number_page: str = 1) -> str:
    """Генерация ссылки на страницу

    Args:
        number_category (str, default = 1): Номер категории. Defaults to 1.
        number_page (str, default = 1): номер страницы. Defaults to 1.

    Returns:
        str: готовая ссылка
    """
    base_url = 'https://parsinger.ru/'
    url = f"html/index{number_category}_page_{number_page}.html"
    logging.debug(f"\nНовая ссылка:\n{url} \n")
    return base_url+url


def StartParse(info_mode: bool = False) -> None:
    if info_mode:
        logging.basicConfig(level=logging.INFO)

    logging.info(f"\n\t\tСбор данных начат\n{'-'*50}")

    if CreateCsvFile(NAME_FILE):
        for number_category in range(1, 6):
            for number_page in range(1, 5):
                current_url = GenerateUrl(number_category, number_page)
                html_text = GetResponse(url=current_url)  # Запрос на сайт
                soup = CookingSoup(html_text)
                products = GetListProducts(soup=soup)
                WriteProductsInFile(name_file=NAME_FILE, products=products)

    logging.info(f"\n\t\tСбор данных окончен\n{'-'*50}")


if __name__ == '__main__':
    StartParse(info_mode=INFO_MODE)
