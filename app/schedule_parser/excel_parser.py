import re
from motor.motor_asyncio import AsyncIOMotorClient
import xlrd
from .formatter import Formatter
from .parser import Parser
from ..crud.schedule import save_schedule
from ..models.schedule import ScheduleModel


class ExcelParser(Parser):
    """Класс, реализующий методы для парсинга расписания из
    Excel документов
    """

    def __init__(self, conn: AsyncIOMotorClient, document_path: str, doc_type: str, formatter: Formatter,
                 path_to_error_log='errors/parser.log'):
        self.__xlsx_path = document_path
        self.__doc_type = self.doc_type_list[doc_type]
        self.__formatter = formatter
        self.__csv_data = []

        super().__init__(conn, path_to_error_log=path_to_error_log)

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
                gr = re.search(
                    r'([А-Яа-я]{4}-[0-9]{2}-[0-9]{2})', str(cell), re.I)
                if gr:
                    group_name_row_num = row_index
                    return group_name_row_num

        return group_name_row_num

    def __get_lessons(self, names, types, teachers, rooms, times,  week_num):
        def get_param(lessons_length, lesson_index, list_params):
            if lessons_length == len(list_params):
                return [list_params[lesson_index]]
            elif len(list_params) == 1:
                return [list_params[0]]
            else:
                return list_params

        # Получение данных об одной паре
        lesson_names = self.__formatter.get_lessons(names)
        lesson_types = self.__formatter.get_types(types)
        lesson_teachers = self.__formatter.get_teachers(teachers)
        lesson_rooms = self.__formatter.get_rooms(rooms)

        # стоит ли предмет на чётной неделе или нет
        is_even_number = True if week_num == 2 else False

        lesson_weeks = self.__formatter.get_weeks(
            names, is_even_number, self.max_weeks)

        lessons = []
        lessons_len = len(lesson_names)
        if lessons_len != 0:
            for i in range(lessons_len):
                types_by_lesson = get_param(lessons_len, i, lesson_types)
                types_by_lesson = '' if len(
                    types_by_lesson) == 0 else types_by_lesson[0]

                name = lesson_names[i]['name']
                teacher = get_param(lessons_len, i, lesson_teachers)
                rooms = get_param(lessons_len, i, lesson_rooms)
                weeks = lesson_weeks[i]
                type_ = lesson_names[i]['type'] if lesson_names[i]['type'] is not None else types_by_lesson
                time_start = times['start']
                time_end = times['end']

                if i - 1 >= 0:
                    if lesson_names[i - 1]['name'] == lesson_names[i]['name'] and lesson_weeks[i - 1] == lesson_weeks[i]:
                        lessons[i - 1]['teachers'] = lesson_teachers
                        lessons[i - 1]['rooms'] = lesson_rooms
                        continue

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

    def __read_group_for_semester(self, sheet, discipline_col_num,
                                  group_name_row_num, cell_range):
        """
        Получение расписания одной группы
        discipline_col_num(int): Номер столбца колонки 'Предмет'
        range(dict): Диапазон выбора ячеек
        """
        # Название группы
        group = sheet.cell(
            group_name_row_num, discipline_col_num).value
        group_name = re.search(r'([А-Яа-я]{4}-[0-9]{2}-[0-9]{2})', group)

        if group_name is None:
            raise ValueError(
                "Group name is none. Cell value: {}", format(group))

        group_name = group_name.group(0)

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
                week_num = lesson_range[2]
                string_index = lesson_range[3]

                # Перебор одного дня (1-6 пара)
                if 'lessons' not in one_day:
                    one_day['lessons'] = []

                # Получение данных об одной паре
                lesson_names = sheet.cell(
                    string_index, discipline_col_num).value
                lesson_types = sheet.cell(
                    string_index, discipline_col_num + 1).value
                lesson_teachers = sheet.cell(
                    string_index, discipline_col_num + 2).value
                lesson_rooms = sheet.cell(
                    string_index, discipline_col_num + 3).value

                if type(lesson_rooms) == float:
                    lesson_rooms = str(int(lesson_rooms))
                elif type(lesson_rooms) == int:
                    lesson_rooms = str(lesson_rooms)

                ready_lessons = self.__get_lessons(lesson_names, lesson_types, lesson_teachers, lesson_rooms,
                                                   time_, week_num)

                # инициализация списка
                if len(one_day['lessons']) < lesson_num:
                    one_day['lessons'].append([])

                if len(ready_lessons) != 0:
                    for ready_lesson in ready_lessons:
                        one_day['lessons'][lesson_num - 1].append(ready_lesson)

                # Объединение расписания
                one_group[day_num] = one_day

        return {'group': group_name, 'schedule': one_group}

    def __read_group_for_session(self, sheet, discipline_col_num,
                                 group_name_row_num, cell_range):
        """Получение расписания одной группы для формы экзаменационной сессии"""
        # TODO: IMPL
        pass

    def parse(self):
        """Чтение excel документа и парсинг данных из него в базу MongoDB
        """
        def fix_weeks_even_num(day_range_list):
            """В расписании бывают ошибки, когда 2 пары подрят стоят на
            неделе одной чётности. Получается, что 2 пары проходят в
            одно время, чего быть не может. Данный метод исправляет это.
            """
            for i in range(1, len(day_range_list)):
                if day_range_list[i - 1][2] == 1 and day_range_list[i][2] == 1:
                    new_lesson_range = (
                        day_range_list[i][0], day_range_list[i][1], 2, day_range_list[i][3])
                    day_range_list[i] = new_lesson_range
                elif day_range_list[i - 1][2] == 2 and day_range_list[i][2] == 2:
                    new_lesson_range = (
                        day_range_list[i][0], day_range_list[i][1], 1, day_range_list[i][3])
                    day_range_list[i] = new_lesson_range
            return day_range_list

        def get_semester_column_range(xlsx_sheet, group_name_cell, group_name_row_index):
            """Получение диапазона ячеек недели для типа расписания = семестр

            Args:
                xlsx_sheet (xlrd.sheet): Worksheet excel документа
                group_name_cell (int): Индекс ячейки с названием группы
                group_name_row_index (int): Индекс строки с названием группы

            Returns:
                dict: {1: [[1, {'start': "9:00", 'end': '10:30'}, 1, 3], [], ... , []],
                       2: [], 3: [], 4: [], 5: [], 6: []}

                    Главные ключи словаря (1-6) соответствуют номерам
                    дней недели (пн-сб), каждому такому ключу
                    соответствует список, состоящий из списков, в которых
                    хранится информация о предмете: номер, время,
                    чётность недели, строка.

                    Пример:     {"1": [[1, {'start': "9:00", 'end': '10:30'}, 1, 3], ... }

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
            day_num_val, lesson_num_val, lesson_time_start_val, lesson_time_end_val, lesson_week_num_val = 0, 0, 0, 0, 0
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
                    day_num_val = self._get_day_num(day_num_col.value)

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
                        elif lesson_num_val == 7 and lesson_count == 7 or lesson_num_val == 8 and lesson_count == 8:
                            lesson_count += 1

                # получаем время начала пары
                lesson_time_col = xlsx_sheet.cell(
                    lesson_num, group_name_row.index(group_name_cell) - 3)
                if lesson_time_col.value != '':
                    lesson_time_start_val = str(
                        lesson_time_col.value).replace('-', ':')

                # получаем время окончания пары
                lesson_time_col = xlsx_sheet.cell(
                    lesson_num, group_name_row.index(group_name_cell) - 2)
                if lesson_time_col.value != '':
                    lesson_time_end_val = str(
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

                if re.findall(r'\d+:\d+', str(lesson_time_start_val), flags=re.A):
                    lesson_range = (lesson_num_val, {'start': lesson_time_start_val,
                                                     'end': lesson_time_end_val},
                                    lesson_week_num_val, lesson_string_index)
                    week_range[day_num_val].append(lesson_range)
            return week_range

        book = xlrd.open_workbook(self.__xlsx_path, on_demand=True)
        sheet = book.sheet_by_index(0)
        DOC_TYPE_EXAM = self.doc_type_list['session']
        column_range = []

        group_list = []
        column_range = []

        # Индекс строки с названиями групп
        group_name_row_num = self.__find_group_name_row(sheet)
        group_name_row = sheet.row(group_name_row_num)

        # Поиск названий групп
        for group_cell in group_name_row:
            group = str(group_cell.value)
            group = re.search(r'([А-Яа-я]{4}-[0-9]{2}-[0-9]{2})', group)

            # Если название найдено, то получение расписания этой группы
            if group:
                group = group.group(0)
                try:
                    # обновляем column_range, если левее группы нет
                    # разметки с неделями, используем старый
                    if not group_list and self.__doc_type != DOC_TYPE_EXAM:
                        column_range = get_semester_column_range(
                            sheet, group_cell, group_name_row_num)
                        for i in range(1, len(column_range) + 1):
                            if len(column_range[i]) > 0:
                                column_range[i] = fix_weeks_even_num(
                                    column_range[i])

                    # TODO: парсинг сессии
                    # elif not group_list and self.__doc_type == DOC_TYPE_EXAM:
                    #     column_range = get_exam_column_range(
                    #         sheet, group_cell, group_name_row_num)

                    if group not in group_list:
                        group_list.append(group)
                        if self.__doc_type != DOC_TYPE_EXAM:
                            self._logger.info(f'Parsing {group}')

                            one_time_table = self.__read_group_for_semester(
                                sheet, group_name_row.index(group_cell),
                                group_name_row_num, column_range
                            )

                            save_schedule(self._db_conn, one_time_table['group'], ScheduleModel(
                                **one_time_table['schedule']))

                        # TODO: реализовать парсинг сессии
                        # else:
                        #     # По номеру столбца
                        #     one_time_table = self.__read_group_for_session(
                        #         sheet, group_name_row.index(group_cell), group_name_row_num, column_range)

                except Exception as ex:
                    self._logger.error(
                        'Error when parsing {}, file: {}. Message: {}'.format(
                            group, self.__xlsx_path, str(ex)
                        ))

        book.release_resources()
        del book
        return self.__csv_data
        # return group_list
