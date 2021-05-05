import logging
import sys
import sys
import os.path
import json


def setup_logger(path_to_error_log, logger_name):
    """Инициализация объекта для логирования информации

    Parameters
    ----------
    path_to_error_log: str, обязательный
        Путь и название файла, куда будут сохраняться логи. Пример: errors.log
    logger_name: str или None, обязательный
        Название логгера

    Вернёт logger с указанным именем (logger_name), если имя указано как None, то вернёт корневой логгер
    """
    logging_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] - %(message)s')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(path_to_error_log)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging_formatter)

    # логирование в консоль
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging_formatter)
    logger.addHandler(handler)
    logger.addHandler(file_handler)
    return logger


def start_parsing():
    """Главная функция, реализующая выполнение парсинга данных с помощью
    интерфейса класса Parse
    """
    # во избежание рекурсивного включения
    from .parser import ExcelParser
    from .downloader import Downloader

    downloader = Downloader(
        path_to_error_log='downloader.log', base_file_dir='xls/')
    downloader.run()
    # директория, в которой хранятся excel документы
    xlsx_dir = 'xls/'
    for path, dirs, files in os.walk(xlsx_dir):
        for file_name in files:
            # todo: вынести проверку актуальности документа
            # в отдельный метод
            if "зима" in file_name or "лето" in file_name:
                continue

            path_to_xlsx_file = os.path.join(path, file_name)
            if("ИКиб_маг_2к" in path_to_xlsx_file):
                continue

            excel_parser = ExcelParser(path_to_xlsx_file,
                                       path_to_error_log='parser.log')
            excel_parser.parse()
