"""
Реализация класса Parser, с помощью которого осуществляется парсинг 
расписания из документов и сохранение расписания в нужном формате в 
базу данных Mongo

Оригинальный автор: Vyacheslav (https://github.com/YaSlavar/parser_mirea)
"""
import re
from schedule_parser.formatter import Formatter
from schedule_data.schedule import Schedule
from abc import ABC, abstractmethod
import os.path
import xlrd
from schedule_parser import setup_logger
from datetime import datetime, timedelta, date
import copy


class Parser:
    """Родительский класс парсинга. Реализует основной интерфейс для дочерних."""

    notes_dict = {
        'МП-1': "ул. Малая Пироговская, д.1",
        'В-78': "Проспект Вернадского, д.78",
        'В-86': "Проспект Вернадского, д.86",
        'С-20': "ул. Стромынка, 20",
        'СГ-22': "5-я ул. Соколиной горы, д.22"
    }

    doc_type_list = {
        'semester': 0,
        'session': 1
    }

    days_dict = {
        'ПОНЕДЕЛЬНИК': 1,
        'ВТОРНИК': 2,
        'СРЕДА': 3,
        'ЧЕТВЕРГ': 4,
        'ПЯТНИЦА': 5,
        'СУББОТА': 6
    }

    months_dict = {
        'ЯНВАРЬ': 1,
        'ФЕВРАЛЬ': 2,
        'МАРТ': 3,
        'АПРЕЛЬ': 4,
        'МАЙ': 5,
        'ИЮНЬ': 6,
        'ИЮЛЬ': 7,
        'АВГУСТ': 8,
        'СЕНТЯБРЬ': 9,
        'ОКТЯБРЬ': 10,
        'НОЯБРЬ': 11,
        'ДЕКАБРЬ': 12
    }

    time_dict = {
        "9:00": 1,
        "10:40": 2,
        "12:40": 3,
        "14:20": 4,
        "16:20": 5,
        "18:00": 6,
        "18:30": 7,
        "20:10": 8
    }

    # максимальное количество недель в текущем семестре
    # todo: вынести подобные значения куда-то типа конфига или в
    # переменные среды
    max_weeks = 17

    def __init__(self, path_to_error_log='parser.log'):
        """Инициализация клсса
            src(str): Абсолютный путь к XLS файлу
        """
        self._logger = setup_logger(path_to_error_log, __name__)
        self._schedule = Schedule()

    def _get_day_num(self, day_name: str):
        """Получение номера дня недели

        Args:
        ----------
            day_name (str): название дня недели в верхнем регистре

        Returns:
        ----------
            int: номер дня недели в диапазоне от 1 до 6 (пн-сб)
            
        Examples
        ----------
        get_day_num("понедельник") -> 1
        
        get_day_num("СУББОТА") -> 6
        """
        print(day_name)
        return Parser.days_dict[day_name.upper()]

    def _get_month_num(self, month_name: str):
        """Получение номера месяца

        Args:
        ----------
            month_name (str): название месяца

        Returns:
        ----------
            int: номер месяца в диапазоне от 1 до 12 (январь-декабрь)
            
        Examples
        ----------
        get_month_num("январь") -> 1
        
        get_month_num("ДЕКАБРЬ") -> 12
        """
        return Parser.months_dict[month_name.upper().replace(' ', '')]

    def _get_lesson_num_by_time(self, time_str):
        """Возвращает номер пары по времени её начала.

        Args:
            time_str (str): время начала пары. Пример: "9:00"

        Returns:
            int: порядковый номер пары или 0, если не существует пары 
            с таким временем начала
        """
        if time_str in self.time_dict:
            return self.time_dict[time_str]
        else:
            return 0

    def __get_doc_type_code(self, path_to_file) -> int:
        """Получение типа документа по его пути

        Args:
            path_to_file (str): путь к документу

        Returns:
            int: тип документа (doc_type_list)
        """
        pass
    
    @abstractmethod
    def parse(self):
        """Чтение документа и парсинг данных о расписании из него в базу MongoDB
        """
        pass