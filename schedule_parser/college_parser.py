from datetime import date, datetime, time, timedelta
import os
import re
import xlrd
from schedule_parser.formatter import Formatter
from schedule_parser.excel_formatter import ExcelFormatter
from schedule_parser.parser import Parser


class CollegeParser(Parser):
    """Парсинг расписания из документов колледжа"""

    def __init__(self, document_path: str, formatter: Formatter,
                 path_to_error_log='errors/college_parser.log'):
        self.__xlsx_path = document_path
        self.__formatter = formatter
        self.__csv_data = []

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
            row_values = sheet.row_values(row_index, end_colx=100)
            for cell in row_values:
                cell = str(cell).replace(' ', '')
                
                gr = re.search(
                    r'([А-Яа-я]{4}-[0-9]{2}-[0-9]{2})', str(cell), re.I)
                if gr:
                    group_name_row_num = row_index
                    return group_name_row_num

        return group_name_row_num

    def __get_lessons(self, names, types, teachers, rooms, times):
        def get_param(lessons_length, lesson_index, list_params):
            if lessons_length == len(list_params):
                return [list_params[lesson_index]]
            elif len(list_params) == 1:
                return [list_params[0]]
            else:
                return list_params

        # Получение данных об одной паре
        lesson_names = self.__formatter.get_lessons(names)
        lesson_types = types
        lesson_teachers = self.__formatter.get_teachers(teachers)
        lesson_rooms = self.__formatter.get_rooms(rooms)
        lesson_weeks = self.__formatter.get_weeks(
            names, None, self.max_weeks)

        lessons = []
        lessons_len = len(lesson_names)
        if lessons_len != 0:
            for i in range(lessons_len):
                name = lesson_names[i]
                teacher = get_param(lessons_len, i, lesson_teachers)
                rooms = get_param(lessons_len, i, lesson_rooms)
                weeks = lesson_weeks[i]
                type_ = lesson_types
                time_start = times['start']
                time_end = times['end']

                one_lesson = {
                    "name": name,
                    "weeks": weeks,
                    "time_start": time_start,
                    "time_end": time_end,
                    "types": type_,
                    "teachers": teacher,
                    "rooms": rooms
                }

                lessons.append(one_lesson)

        return lessons

    def __get_group_name(self, subst):
        group_test = subst.replace(' ', '')
        group_name = re.search(r'([А-Яа-я]{4}-[0-9]{2}-[0-9]{2})', group_test)
        if group_name is not None:
            return group_name.group(0)
        return None
        
    def __read_group_for_semester(self, sheet, discipline_col_num,
                                  group_name_row_num, cell_range):
        """
        Получение расписания одной группы
        discipline_col_num(int): Номер столбца колонки 'Предмет'
        range(dict): Диапазон выбора ячеек
        """
        # Название группы
        cell_group_value = sheet.cell(
            group_name_row_num, discipline_col_num).value
        group_name = self.__get_group_name(cell_group_value)
        
        if group_name is None:
            raise ValueError(
                "Group name is none. Cell value: {}", format(cell_group_value))

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
                lesson_num = lesson_range[0]
                time_ = lesson_range[1]
                string_index = lesson_range[2]

                # Перебор одного дня (1-6 пара)
                if 'lessons' not in one_day:
                    one_day['lessons'] = []

                # Получение данных об одной паре
                lesson_names = sheet.cell(
                    string_index, discipline_col_num).value
                if self.__get_group_name(lesson_names):
                    # в структуре документа после каждого дня идёт
                    # название учебной группы o_O
                    continue

                lesson_types = 'пр'
                lesson_teachers = sheet.cell(
                    string_index, discipline_col_num).value
                lesson_rooms = str(sheet.cell(
                    string_index, discipline_col_num + 1).value)

                lesson_rooms = str(int(lesson_rooms)) if isinstance(
                    lesson_rooms, float) else str(lesson_rooms)

                ready_lessons = self.__get_lessons(
                    lesson_names, lesson_types, lesson_teachers, lesson_rooms, time_)

                # инициализация списка
                if len(one_day['lessons']) < lesson_num:
                    one_day['lessons'].append([])

                if len(ready_lessons) != 0:
                    for ready_lesson in ready_lessons:
                        one_day['lessons'][lesson_num - 1].append(ready_lesson)

                # Объединение расписания
                one_group[day_num] = one_day
                
        one_group['6'] = {'lessons': [[], [], [], []]}
        return {'group': group_name, 'schedule': one_group}

    def __get_lesson_num(self, time_start):
        lessons = {
            '08:45': 1,
            '10:30': 2,
            '12:40': 3,
            '14:20': 4,
        }
        return lessons[time_start]

    def __get_column_range(self, xlsx_sheet, group_name_cell, group_name_row, group_name_row_index):
        """Получение диапазона ячеек недели для типа расписания = семестр

            Args:
                xlsx_sheet (xlrd.sheet): Worksheet excel документа
                group_name_cell (int): Индекс ячейки с названием группы
                group_name_row_index (int): Индекс строки с названием группы

            Returns:
                dict: {1: [[1, {'start': "9:00", 'end': '10:30'}, 1, 3], [], ... , []],
                       2: [], 3: [], 4: [], 5: []}

                    Главные ключи словаря (1-5) соответствуют номерам
                    дней недели (пн-пт), каждому такому ключу
                    соответствует список, состоящий из списков, в которых
                    хранится информация о предмете: номер, время, строка.

                    Пример:     {"1": [[1, {'start': "9:00", 'end': '10:30'}, 3], ... }

                    Нулевой элемент вложенного списка - это номер пары;

                    Первый элепмент вложенного списка - это
                    время начала пары;

                    Третий элемент - номер строки в столбце группы,
                    которой соответствует информация об этой паре.
            """
        # инициализация списка диапазонов пар
        week_range = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: []
        }

        # Номер строки, с которой начинается отсчет пар
        initial_row_num = group_name_row_index + 1
        lesson_count = 0  # Счетчик количества пар
        # Перебор столбца с номерами пар и вычисление на
        # основании количества пар в день диапазона выбора ячеек
        day_num_val, lesson_num_val, lesson_time_start_val, lesson_time_end_val = 0, 0, 0, 0,
        # кол-во строк в столбце группы
        row_s = len(xlsx_sheet.col(group_name_row.index(group_name_cell)))
        if row_s >= 200:
            row_s = 122

        # проходимся по каждой ячейке в колонке группы
        for lesson_num in range(initial_row_num, row_s):
            day_num_col = xlsx_sheet.cell(
                lesson_num, group_name_row.index(group_name_cell) - 2)

            # получаем день недели (крайняя левая ячейка в разметке)
            if day_num_col.value != '':
                day_num_val = self._get_day_num(day_num_col.value.replace(' ', ''))

            # получаем время начала и окончания пары
            lesson_time_col = xlsx_sheet.cell(
                lesson_num, group_name_row.index(group_name_cell) - 1)
            if lesson_time_col.value != '':
                if re.search(r'(\d\d\.\d\d)[\s-]*(\d\d\.\d\d)', str(lesson_time_col.value)) is not None:
                    lesson_time_value = str(lesson_time_col.value).split('-')
                    lesson_time_start_val = lesson_time_value[0].strip().replace(
                        '.', ':')
                    lesson_time_end_val = lesson_time_value[1].strip().replace(
                        '.', ':')

            # получаем номер пары
            if lesson_time_start_val != 0:
                lesson_num_val = self.__get_lesson_num(lesson_time_start_val)
                if lesson_num_val > lesson_count:
                    lesson_count = lesson_num_val

            lesson_string_index = lesson_num

            if re.findall(r'\d+:\d+', str(lesson_time_start_val), flags=re.A):
                lesson_range = (lesson_num_val, {'start': lesson_time_start_val,
                                                 'end': lesson_time_end_val}, lesson_string_index)
                week_range[day_num_val].append(lesson_range)
        return week_range

    def parse(self):
        """Чтение excel документа и парсинг данных из него в базу MongoDB
        """

        book = xlrd.open_workbook(self.__xlsx_path, on_demand=True)
        sheet = book.sheet_by_index(0)
        column_range = []

        group_list = []
        column_range = []

        # Индекс строки с названиями групп
        group_name_row_num = self.__find_group_name_row(sheet)
        group_name_row = sheet.row(group_name_row_num)

        # Поиск названий групп
        for group_cell in group_name_row:
            group = self.__get_group_name(str(group_cell.value))

            # Если название найдено, то получение расписания этой группы
            if group:
                try:
                    # обновляем column_range, если левее группы нет
                    # разметки с неделями, используем старый
                    if not group_list:
                        column_range = self.__get_column_range(
                            sheet, group_cell, group_name_row, group_name_row_num)

                    if group not in group_list:
                        group_list.append(group)
                        self._logger.info(f'Parsing {group}')

                        one_time_table = self.__read_group_for_semester(
                            sheet, group_name_row.index(group_cell),
                            group_name_row_num, column_range
                        )

                        self._schedule.save(
                            one_time_table['group'], one_time_table['schedule'])

                except Exception as ex:
                    self._logger.error(
                        'Error when parsing {}, file: {}. Message: {}'.format(
                            group, self.__xlsx_path, str(ex)
                        ))

        book.release_resources()
        del book
        return self.__csv_data
