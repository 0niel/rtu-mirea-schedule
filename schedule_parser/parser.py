"""
Реализация класса Parser, с помощью которого осуществляется парсинг 
расписания из документов и сохранение расписания в нужном формате в 
базу данных Mongo
"""
import re
import json
import csv
import sqlite3
import os.path
import subprocess
import datetime
from itertools import cycle
from sqlite3.dbapi2 import Connection
import traceback
import xlrd
import time
from schedule_parser import setup_logger
from database import semester_collection, exam_collection


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
        'semester': 0
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

    def __init__(self, path_to_error_log='errors/parser.log'):
        """Инициализация клсса
            src(str): Абсолютный путь к XLS файлу
        """
        self._logger = setup_logger(path_to_error_log, __name__)

    @staticmethod
    def is_trash(lesson: str):
        """Проверка названия занятия на мусорные символы

        Args:
        -------
            lesson (str): название занятия

        Returns:
        -------
            bool: True, если занятия не существует (мусорные символы)
                и False, если оно существует
        """

        # рассчитываем, что в названии есть хотя бы одна буква
        # русского алфавита
        if lesson is None or lesson == '':
            return True
        rus_letters = re.search(r'[а-яА-Я]', lesson)
        if rus_letters is None:
            return True
        return False

    @staticmethod
    def get_lesson_weeks(lesson: str, is_even_number: bool):
        """
        Метод возвращает список недель, на которых данное занятие проходит.
        Вернёт None, если занятие (название предмета) не является занятием. 

        Note:
            В качестве значения максимального кол-ва недель используется статическое поле
            max_weeks класса Parser.

        Examples
        ----------
        get_lesson_weeks("............", True) -> None

        get_lesson_weeks("кр. 12 н. Математический анализ", True) -> [2, 4, 6, 8, 10, 14, 16]

        get_lesson_weeks("3-10 н. Математический анализ", True) -> [4, 6, 8, 10]
        
        get_lesson_weeks("5 н. Математический анализ", True) -> []
        
        Параметры
        ----------
        lesson: str, обязательный
            Название предмета из ячейки предмета
        is_even_number: bool, обязательный
            Стоит ли предмет на чётной неделе (II). True, если по чётным, False, если нет.
        """

        div_result = 0 if is_even_number else 1

        if Parser.is_trash(lesson):
            return None

        # чтобы не триггериться на эту несчастную н-ку
        lesson.replace('Ин.', '')
        
        # todo: реализовать выбор нужной информации с помощью регулярок
        
        # кр - кроме
        # пример: "кр. 12 н. Математический анализ"
        # пример: "кр. 13-15 н. Математический анализ"
        if "кр." in lesson or "кр " in lesson:
            # todo: кажется, что данная схема является нестабильной
            # лучше верейти на какую-то регулярку
            split_pattern = 'н.'
            if ' н ' in lesson:
                split_pattern = ' н '
            elif ' нед ' in lesson:
                split_pattern = ' нед '
            elif ' нед. ' in lesson:
                split_pattern = ' нед. '
                
            exclude = lesson.split(split_pattern)[0]
            lesson = lesson.split(split_pattern)[1].strip()
                
            regex_num = re.compile(r'\d+')
            # поиск всех вхождений чисел
            exclude_weeks = [int(item) for item in regex_num.findall(exclude)]
            if "-" in exclude:
                exclude_weeks = [i for i in range(
                    exclude_weeks[0], exclude_weeks[1]+1) if i % 2 == div_result]

            weeks = []
            for i in range(1, Parser.max_weeks+1):
                if i not in exclude_weeks and i % 2 == div_result:
                    weeks.append(i)
            return weeks

        # предмет без исключения недель
        # пример: "11 н. Математический анализ"
        # пример: "2,4,6,8,10 н. Математический анализ"
        # пример: "3-10 н. Математический анализ"
        elif " н." in lesson or " н " in lesson:
            if " н." in lesson:
                exc = lesson.split(" н.")[0]
                lesson = lesson.split(" н.")[1].strip()
            elif "н." in lesson:
                exc = lesson.split("н.")[0]
                lesson = lesson.split("н.")[1].strip()
            elif " н " in lesson:
                exc = lesson.split(" н ")[0]
                lesson = lesson.split(" н ")[1].strip()
            regex_num = re.compile(r'\d+')
            weeks = [int(item) for item in regex_num.findall(exc)]

            if "-" in exc:
                weeks = [i for i in range(
                    weeks[0], weeks[1]+1) if i % 2 == div_result]
            if len(weeks) == 1:
                if weeks[0] % 2 != div_result:
                    return []
            return weeks

        return [i for i in range(1, Parser.max_weeks+1) if i % 2 == div_result]

    @staticmethod
    def get_day_num(day_name: str):
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
        return Parser.days_dict[day_name.upper()]

    @staticmethod
    def get_month_num(month_name: str):
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

    def _format_other_cells(self, cell):
        """
        Разделение строки по "\n"
        :param cell:
        :return:
        """
        cell = cell.split("\n")
        return cell

    def _format_teacher_name(self, teachers_names):
        """Форматирование имён учителей в нужный формат. Возвращает список учителей.
        Если в качестве значения ячейки указаны 2 преподавателя, то вернёт список из двух элементов.

        Примеры
        ----------
        format_teacher_name('Бишаев А.М.  Коробкин Ю.В.') -> ['Бишаев А.М.', 'Коробкин Ю.В.']
        
        format_teacher_name('Бишаев А.М.\nКоробкин Ю.В.') -> ['Бишаев А.М.', 'Коробкин Ю.В.']
        
        Параметры
        ----------
        teachers_names: str, обязательный
            Имена преподавателя: значение ячейки с информацией о преподавателях.
        """

        teachers_names = str(teachers_names)
        return re.split(r' {2,}|\n', teachers_names)

    def _format_room_name(self, cell):
        if isinstance(cell, float):
            cell = int(cell)
        string = str(cell)
        for pattern in Parser.notes_dict:
            regex_result = re.findall(pattern, string, flags=re.A)
            if regex_result:
                string = string.replace('  ', '').replace(
                    '*', '').replace('\n', '')
                string = re.sub(
                    regex_result[0], Parser.notes_dict[regex_result[0]] + " ", string, flags=re.A)

        return re.split(r' {2,}|\n', string)

    def _format_lesson_name(self, lesson: str):
        """
        Возвращает только название предмета (без списка недель)

        
        Args
        ----------
        lesson: str, обязательный
            Название предмета из ячейки предмета
        """
        if Parser.is_trash(lesson):
            return None

        # удаляем исключающую недели скобку
        # пример: Мант. анализ (кр. 10,12,14,16, 18 н.)
        lesson = re.sub(r"\(кр.*(.+)\d(.*)н.?\)", "", lesson)
        # пример: Ин. яз. кр. 15 н.
        lesson = re.sub(r'кр(.*\d.?)н.?', '', lesson)
        # пример: 3,7,11,15 н. Философия
        lesson = re.sub(r'\d.*?н.?', '', lesson)

        lesson = lesson.strip()
        
        return lesson

    def _get_lesson_num_from_time(self, time_str):
        if time_str in self.time_dict:
            return self.time_dict[time_str]
        else:
            return 0


class ExcelParser(Parser):
    """Класс, реализующий методы для парсинга расписания из
    Excel документов
    """

    def __init__(self, xlsx_path: str,
                 path_to_error_log='errors/parser.log'):
        self.__xlsx_path = xlsx_path
        self.__doc_type = self.__get_doc_type_code(xlsx_path)
        super().__init__(path_to_error_log=path_to_error_log)

    def __find_group_name_row(self, sheet):
        """Поиск строки, которая содержит информаци о названиях групп

        Args:
        ----------
            sheet (xlrd.sheet): Рабочий лист (worksheet) excel документа

        Returns:
        ----------
            int: индекс строки, которая содержит названия групп
        """
        # Индекс строки с названиями групп
        group_name_row_num = 1

        # Поиск номера строки, содержащей названия групп
        leng = len(sheet.col(1))
        if leng > 200:
            leng = 122
        # проходимся по всем строкам
        for row_index in range(leng):
            # получаем значения ячеек в данной строке
            row_values = sheet.row_values(row_index, end_colx=50)
            for cell in row_values:
                gr = re.findall(r'([А-Я]+-\w+-\w+)', str(cell), re.I)
                if gr:
                    group_name_row_num = row_index
                    break

        return group_name_row_num

    def __read_one_group_for_semester(self, sheet, discipline_col_num,
                                      group_name_row_num, cell_range):
        """
        Получение расписания одной группы
        discipline_col_num(int): Номер столбца колонки 'Предмет'
        range(dict): Диапазон выбора ячеек
        """
        # Название группы
        group_name = sheet.cell(
            group_name_row_num, discipline_col_num).value
        # Инициализация словаря
        one_group = {}

        # перебор по дням недели (понедельник-суббота)
        # номер дня недели (1-6)
        for day_num in cell_range:
            one_day = {}
            for lesson_range in cell_range[day_num]:
                # приведение к строке нужно из-за того, что 
                # bson формат не умеет кушать нестроковые ключи
                day_num = str(day_num)
                lesson_num = str(lesson_range[0])
                time_ = lesson_range[1]
                week_num = lesson_range[2]
                string_index = lesson_range[3]

                # Перебор одного дня (1-6 пара)
                if 'lessons' not in one_day:
                    one_day['lessons'] = {}

                # Получение данных об одной паре
                lesson_name = str(sheet.cell(
                    string_index, discipline_col_num).value)
                lesson_name_clear = self._format_lesson_name(lesson_name)
                is_even_number = True if week_num == 2 else False
                lesson_weeks = Parser.get_lesson_weeks(
                    lesson_name, is_even_number)
                lesson_type = sheet.cell(
                    string_index, discipline_col_num + 1).value
                teacher = self._format_teacher_name(sheet.cell(
                    string_index, discipline_col_num + 2).value)
                room = self._format_room_name(sheet.cell(
                    string_index, discipline_col_num + 3).value)

                one_lesson = {"weeks": lesson_weeks, "time": time_, "name": lesson_name_clear,
                              "type": lesson_type, "teacher": teacher, "room": room}

                # инициализация списка
                if lesson_num not in one_day['lessons']:
                    one_day['lessons'][lesson_num] = []
                    
                if Parser.is_trash(lesson_name) is False:
                    one_day['lessons'][lesson_num].append(one_lesson)
                else:
                    one_day['lessons'][lesson_num].append(None)
                    
                # Объединение расписания
                one_group[day_num] = one_day

        return {'group': group_name, 'schedule': one_group}

    def __read_one_group_for_exam(self, sheet, discipline_col_num,
                                  group_name_row_num, cell_range):
        """
        Получение расписания одной группы для формы экзаменационной сессии
        discipline_col_num(int): Номер столбца колонки 'Предмет'
        range(dict): Диапазон выбора ячеек
        """
        EXAM_PASS_INDEX = 0
        one_group = {}
        group_name = sheet.cell(
            group_name_row_num, discipline_col_num).value  # Название группы
        one_group[group_name] = {}

        for date in cell_range:
            string_index = cell_range[date][0]
            lesson_type, dist_name, teacher = None, None, None
            if len(cell_range[date]) > 1:
                lesson_type_index = cell_range[date][0]
                dist_name_index = cell_range[date][1]
                teacher_name_index = cell_range[date][2]

                lesson_type = sheet.cell(
                    lesson_type_index, discipline_col_num).value
                dist_name = sheet.cell(
                    dist_name_index, discipline_col_num).value
                teacher = self._format_teacher_name(sheet.cell(
                    teacher_name_index, discipline_col_num).value)

            time = sheet.cell(string_index, discipline_col_num + 1).value
            if isinstance(time, str):
                time = time.replace("-", ":")
            if isinstance(time, float):
                time = xlrd.xldate.xldate_as_datetime(
                    time, 0).strftime("%H:%M")

            lesson_num = self._get_lesson_num_from_time(time)

            room = self._format_room_name(sheet.cell(
                string_index, discipline_col_num + 2).value)
            if isinstance(room, float):
                room = int(room)

            one_day = {"lesson_{}".format(lesson_num): {}}

            if dist_name is not None:
                one_lesson = {"date": date, "time": time,
                              "name": dist_name, "type": lesson_type,
                              "teacher": teacher, "room": room,
                              "include": '', "exception": ''}

                if dist_name and room:
                    if "week_{}".format(EXAM_PASS_INDEX) not in one_day["lesson_{}".format(lesson_num)]:
                        one_day["lesson_{}".format(lesson_num)][
                            "week_{}".format(EXAM_PASS_INDEX)] = []  # Инициализация списка

                    one_day["lesson_{}".format(lesson_num)]["week_{}".format(
                        EXAM_PASS_INDEX)].append(one_lesson)

            # Объединение расписания
            one_group[group_name]["day_{}".format(date)] = one_day

        return one_group

    def __get_doc_type_code(self, path_to_xlsx_file):
        """
        Получение типа документа, для каждого типа документа
        path_to_xlsx_file
        :return:
        """
        doc_type_str = os.path.dirname(
            os.path.relpath(path_to_xlsx_file, start='xls'))
        return Parser.doc_type_list[doc_type_str]

    def parse(self):
        """Чтение excel документа и парсинг данных из него в базу MongoDB
        """
        def get_column_range_for_type_eq_semester(xlsx_sheet, group_name_cell, group_name_row_index):
            """Получение диапазона ячеек недели для типа расписания = семестр

            Args:
                xlsx_sheet (xlrd.sheet): Worksheet excel документа
                group_name_cell (int): Индекс ячейки с названием группы
                group_name_row_index (int): Индекс строки с названием группы

            Returns:
                dict: {1: [[1, "9:00", 1, 3], [], ... , []], 
                       2: [], 3: [], 4: [], 5: [], 6: []}
                       
                    Главные ключи словаря (1-6) соответствуют номерам
                    дней недели (пн-сб), каждому такому ключу 
                    соответствует список, состоящий из списков, в которых
                    хранится информация о предмете: номер, время,
                    чётность недели, строка.
                    
                    Пример:     {"1": [[1, "9:00", 1, 3], ... }
                    
                    Нулевой элемент вложенного списка - это номер пары;
                    
                    Первый элепмент вложенного списка - это 
                    время начала пары;
                    
                    Второй элемент вложенного списка - проходит
                    и предмет на нечётной (1) или чётной (2) недели;
                    
                    Третий элемент - номер строки в столбце группы, 
                    которой соответствует информация об этой паре.
            """
            # инициализация списка диапазонов пар
            week_range = {
                1: [],
                2: [],
                3: [],
                4: [],
                5: [],
                6: []
            }

            # Номер строки, с которой начинается отсчет пар
            initial_row_num = group_name_row_index + 1
            lesson_count = 0  # Счетчик количества пар
            # Перебор столбца с номерами пар и вычисление на
            # основании количества пар в день диапазона выбора ячеек
            day_num_val, lesson_num_val, lesson_time_val, lesson_week_num_val = 0, 0, 0, 0
            # кол-во строк в столбце группы
            row_s = len(xlsx_sheet.col(group_name_row.index(group_name_cell)))
            if row_s >= 200:
                row_s = 122

            # проходимся по каждой ячейке в колонке группы
            for lesson_num in range(initial_row_num, row_s):
                day_num_col = xlsx_sheet.cell(
                    lesson_num, group_name_row.index(group_name_cell) - 5)

                # получаем день недели (крайняя левая ячейка в разметке)
                if day_num_col.value != '':
                    day_num_val = Parser.get_day_num(day_num_col.value)

                # получаем номер пары
                lesson_num_col = xlsx_sheet.cell(
                    lesson_num, group_name_row.index(group_name_cell) - 4)
                if lesson_num_col.value != '':
                    lesson_num_val = lesson_num_col.value
                    # является ли значение числом
                    if isinstance(lesson_num_val, float):
                        lesson_num_val = int(lesson_num_val)
                        if lesson_num_val > lesson_count:
                            lesson_count = lesson_num_val

                # получаем время начала пары
                lesson_time_col = xlsx_sheet.cell(
                    lesson_num, group_name_row.index(group_name_cell) - 3)
                if lesson_time_col.value != '':
                    lesson_time_val = str(
                        lesson_time_col.value).replace('-', ':')

                # получаем номер недели (нечётная/чётная)
                lesson_week_num = xlsx_sheet.cell(
                    lesson_num, group_name_row.index(group_name_cell) - 1)
                if lesson_week_num.value != '':
                    if lesson_week_num.value == 'I':
                        lesson_week_num_val = 1
                    elif lesson_week_num.value == 'II':
                        lesson_week_num_val = 2
                else:
                    if lesson_week_num_val == 1:
                        lesson_week_num_val = 2
                    else:
                        lesson_week_num_val = 1

                lesson_string_index = lesson_num

                if re.findall(r'\d+:\d+', str(lesson_time_val), flags=re.A):
                    lesson_range = (lesson_num_val, lesson_time_val,
                                    lesson_week_num_val, lesson_string_index)
                    week_range[day_num_val].append(lesson_range)
            return week_range

        def get_column_range_for_type_eq_exam(xlsx_sheet, group_name_cell, group_name_row_index):
            """
            Получение диапазона ячеек недели для типа расписания = экзамен
            :param group_name_row_index: 
            :param xlsx_sheet:
            :param group_name_cell:
            :return:
            """

            def fix_date_range(date_range_list):
                """
                На случай, если в шаблоне есть незаполненные ячейки
                :param date_range_list:
                :return:
                """
                is_fuck = False
                this_index, this_date = 0, 0
                for date_item in date_range_list:
                    if None in date_item:
                        is_fuck = True
                    elif is_fuck is True:
                        this_date = datetime.date(
                            datetime.datetime.now().year, date_item[1], date_item[0])
                        this_index = date_range.index(date_item)
                        break

                for range_index in range(this_index, 0, -1):
                    if date_range_list[range_index - 1][0] != date_range_list[range_index][0]:
                        this_date = this_date - datetime.timedelta(1)
                    date_range_list[range_index - 1][0] = this_date.day
                    date_range_list[range_index - 1][1] = this_date.month

                return date_range_list

            # Номер строки, с которой начинается отсчет пар
            initial_row_nam = group_name_row_index + 1

            date_range = []
            # Перебор столбца с номерами пар и вычисление на основании количества пар в день диапазона выбора ячеек
            date_num_val, month_num_val = None, None
            row_s = len(xlsx_sheet.col(group_name_row.index(group_name_cell)))
            if row_s >= 200:
                row_s = 122

            for day_num in range(initial_row_nam, row_s):

                month_num_col = xlsx_sheet.cell(
                    day_num, group_name_row.index(group_name_cell) - 2)
                if month_num_col.value != '':
                    month_num_val = Parser.get_month_num(month_num_col.value)

                date_num_col = xlsx_sheet.cell(
                    day_num, group_name_row.index(group_name_cell) - 1)
                if date_num_col.value != '':
                    if isinstance(date_num_col.value, float):
                        temp_date_num_val = str(round(date_num_col.value))
                    else:
                        temp_date_num_val = str(date_num_col.value)

                    date_num_val = re.findall(r'\d+', temp_date_num_val)

                    if date_num_val:
                        date_num_val = int(date_num_val[0])
                    else:
                        break

                date_range.append([date_num_val, month_num_val, day_num])

            date_range = fix_date_range(date_range)

            date_range_dict = {}
            for date_item in date_range:
                this_row_date = datetime.date(
                    datetime.datetime.now().year, date_item[1], date_item[0])
                if this_row_date.strftime("%d.%m") not in date_range_dict:
                    date_range_dict[this_row_date.strftime("%d.%m")] = []

                date_range_dict[this_row_date.strftime(
                    "%d.%m")].append(date_item[2])

            return date_range_dict

        book = xlrd.open_workbook(self.__xlsx_path, on_demand=True)
        sheet = book.sheet_by_index(0)
        DOC_TYPE_EXAM = 2
        column_range = []
        # todo: реализовать отдельную коллекцию всех групп
        group_list = []

        # Индекс строки с названиями групп
        group_name_row_num = self.__find_group_name_row(sheet)
        group_name_row = sheet.row(group_name_row_num)

        # Поиск названий групп
        for group_cell in group_name_row:
            group = str(group_cell.value)
            group = re.search(r'[А-Яа-я]{4}-[0-9]{2}-[0-9]{2}', group)

            # Если название найдено, то получение расписания этой группы
            if group:
                try:
                    self._logger.info(f'Parsing {group.group(0)}')
                    # обновляем column_range, если левее группы нет
                    # разметки с неделями, используем старый
                    if not group_list and self.__doc_type != DOC_TYPE_EXAM:
                        column_range = get_column_range_for_type_eq_semester(
                            sheet, group_cell, group_name_row_num)

                    elif not group_list and self.__doc_type == DOC_TYPE_EXAM:
                        column_range = get_column_range_for_type_eq_exam(
                            sheet, group_cell, group_name_row_num)

                    group_list.append(group.group(0))

                    if self.__doc_type != DOC_TYPE_EXAM:
                        # По номеру столбца
                        one_time_table = self.__read_one_group_for_semester(
                            sheet, group_name_row.index(group_cell), 
                            group_name_row_num, column_range
                            )
                        semester_collection.update_one(
                            {'group': one_time_table['group']}, 
                            {'$set': {'group': one_time_table['group'],
                                    'schedule':  one_time_table['schedule']}}, 
                                        upsert=True)
                    else:
                        # По номеру столбца
                        one_time_table = self.__read_one_group_for_exam(
                            sheet, group_name_row.index(group_cell), group_name_row_num, column_range)
                except Exception as ex:
                    self._logger.error(
                        'Error when parsing {}, file: {}. Message: {}'.format(
                            group.group(0), self.__xlsx_path, str(ex)
                        ))

        book.release_resources()
        del book
        return group_list
