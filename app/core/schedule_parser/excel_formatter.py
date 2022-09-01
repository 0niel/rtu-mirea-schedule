import re
from .formatter import Formatter


# Дорогой дневник, мне не подобрать слов, чтобы описать боль и унижение,
# которое я испытал, когда писал ExcelFormatter


class ExcelFormatter(Formatter):
    """Реализация форматирования ячеек excel таблицы расписания к нужному формату.
    """

    def __format_subgroups_and_type(self, lesson: str) -> list:
        """Метод форматирует самые сложне и редкие случаи, которые
        встречаются в ячейке предмета.

        Args:
            lesson (str): неотформатированная строка

        Returns:
            list: список разделённых и отформатированных предметов
        """
        result = []

        # 2,4,6,8,10 (лк),12,14н (пр) Инструментарий информационно-аналитической деятельности
        # группа 1 - номера недель, группа 2 - тип предмета
        regexp_1 = r'(?:((?:\d+[-, \.]*)+(?:н|нед)?[. ]*)(?:[( ]*(лк|пр|лек|лаб)[) ]+))'

        # 1гр.= 2н.; 2гр.=4н. Криптографические методы защиты информации;
        # группа 1 - номер группы, группа 2 - номера недель
        regexp_2 = r'(?:(\d+[-, \.]*)+(?:группа|груп|гр|подгруппа|подгр)[. -]*=\s*((?:\d+[-, \.]*)+(?:нед|н)?[;. \b]+))'

        # 6,12н-1гр 4,10н-2 гр Материалы и технологии трехмерной печати в машиностр
        # группа 1 - номера недель, группа 2 - номер группы
        regexp_3 = r'(?:((?:\d+[-, \.]*)+(?:нед|н)[. ]*\-)(?:(\d+[-, =\.]*)+(?:группа|груп|гр|подгруппа|подгр)[. \b]*))'

        # (3,7,11,15 н. - лк; 5,9,13,17 н. - пр) Современные проблемы и методы прикладной информатики и развития информационного общества
        # группа 1 - номера недель, группа 2 - тип предмета
        regexp_4 = r'((?:\d+[-,\s.]*)+(?:н|нед)?[. ]*)(?:[- ]*(лк|пр|лек|лаб)(\b|[; ]+))'

        expressions = [regexp_1, regexp_2, regexp_3, regexp_4]

        # проверяем, какие из регулярных выражений выше подходит в нашем случае,
        # затем разделяем предмет согласно подгруппам, типам пары, неделям,
        # удаляем мусор и возвращаем готовый список.
        for regexp in expressions:
            found = re.finditer(regexp, lesson)
            found_items = [x for x in found]
            if len(found_items) > 0:
                for week_types in found_items:
                    lesson = lesson.replace(week_types.group(), '')

                # удаление ненужных символов
                remove_trash = r'(\A\W+\s*)|([-,_\+;]+$)'
                lesson = re.sub(remove_trash, "", lesson)
                lesson = lesson.strip()
                list_lessons = lesson.split(';')

                group_substr = ' груп.' if regexp == regexp_2 or regexp == regexp_3 else ''

                if len(list_lessons) == 2 and len(found_items) == 4:
                    for i in range(len(found_items)):
                        index = int(i >= 2)

                        group_1 = re.sub(remove_trash, "",
                                         found_items[i].group(1))
                        group_1 = group_1.strip()

                        group_2 = re.sub(remove_trash, "",
                                         found_items[i].group(2))
                        group_2 = group_2.strip()

                        if regexp == regexp_2:
                            result.append(
                                group_2 + ' ' + list_lessons[index] + ' ' + group_1 + group_substr)
                        else:
                            result.append(
                                group_1 + ' ' + list_lessons[index] + ' ' + group_2 + group_substr)

                else:
                    for week_types in found_items:
                        group_1 = re.sub(remove_trash, "", week_types.group(1))
                        group_1 = group_1.strip()

                        group_2 = re.sub(remove_trash, "", week_types.group(2))
                        group_2 = group_2.strip()

                        if regexp == regexp_2:
                            result.append(group_2 + ' ' + lesson +
                                          ' ' + group_1 + group_substr)
                        else:
                            result.append(group_1 + ' ' + lesson +
                                          ' ' + group_2 + group_substr)

        return result

    def __split_lessons(self, lessons: str) -> list:
        """Разбивает строку с предметами на список названий предметов.

        Args:
            lessons (str): значение ячейки, в которой содержатся
            названия предметов.

        Returns:
            list: список названий предметов

            Пример:
            self.__split_lessons('1-3 н. Мат. анализ\nЛинейная алгебра')
                -> ['1-3 н. Мат. анализ', 'Линейная алгебра']
        """
        result = []

        # несколько предметов в одной ячейке и разделены
        # с помощью переноса строки.
        if '\n' in lessons:
            for one_lesson in lessons.split('\n'):
                result.append(one_lesson)
        # несколько предметов разделены большим количество пробелов.
        elif len(re.split(r" {3,}", lessons)) > 1:
            for one_lesson in re.split(r"\s\s\s+", lessons):
                result.append(one_lesson)

        # ниже мы используем __format_subgroups_and_type, чтобы разделить
        # предметы по типу, если он указан, иоли по подгруппам, если они
        # указаны
        if len(result) > 0:
            for lesson in sorted(result):
                formatted_lessons = self.__format_subgroups_and_type(lesson)
                if len(formatted_lessons) > 0:
                    result.remove(lesson)
                    result += formatted_lessons

        else:
            formatted_lessons = self.__format_subgroups_and_type(lessons)
            if len(formatted_lessons) > 0:
                result += formatted_lessons

        # если length == 0, то предыдущие методы форматирования не сработали,
        # а это скорее всего значит, что у нас один предмет, либо несколько
        # предметов записаны в одну строку
        if len(result) == 0:
            # пробуем разделить по ';'
            if ';' in lessons:
                result += lessons.split(';')
            else:
                # иначе обрабатываем случай, когда несколько предметов записаны
                # в одной строке, либо это просто один предмет.
                # пример нескольких предметов в одной строке:
                #
                # 1,3,9,13 Конфиденциальное делопроизводство 5,7,11,15 н. кр 5 н. Деньги, кредит,банки
                #
                # переноса строк нет, но делить на два предмета как-то надо.
                oneline_lessons_regexp = r'(?:\d+[-,\s.]*)+\s*(?:(?:нед|н)|\W)[.\s+]*\(?(?:кроме|кр)?(?![.\s,\-\d]*(?:подгруппа|подгруп|подгр|п\/г|группа|гр))[.\s]*'
                found = [x for x in re.finditer(
                    oneline_lessons_regexp, lessons)]
                # Разработка ПАОИиАС 2,6,10,14 н.+4,8,12,16н.
                length = len(found)
                if length > 1:
                    for i in range(1, length):
                        prev_found_pos = found[i-1].span()
                        current_found_pos = found[i].span()
                        is_last_elem = i + 1 > length - 1
                        # если конец предыдущей позиции не совпадает с началом текущей
                        if prev_found_pos[1] != current_found_pos[0]:
                            if is_last_elem is False:
                                result.append(
                                    lessons[prev_found_pos[0]:current_found_pos[0]])
                            else:
                                result.append(
                                    lessons[prev_found_pos[0]:current_found_pos[0]])
                                result.append(lessons[current_found_pos[0]:])
                        else:
                            if is_last_elem is False:
                                result.append(
                                    lessons[prev_found_pos[0]:found[i + 1].span()[0]])
                            else:
                                if length == 2:
                                    result.append(lessons)
                                else:
                                    result.append(lessons[prev_found_pos[0]:])

                else:
                    # значит это просто одиночный предмет
                    result.append(lessons)

        return [lesson for lesson in result if lesson.strip() != ""]

    def __fix_typos(self, names: str) -> str:
        """Исправление ошибок и опечаток в документе"""
        names = re.sub(r'деятельность\s*деятельность', 'деятельность', names)
        names = re.sub(r'^\s*Военная\s*$', 'Военная подготовка', names, flags=re.MULTILINE)
        names = re.sub(r'^\s*подготовка\s*$', 'Военная подготовка', names, flags=re.MULTILINE)
        names = re.sub(r'^\s*1\s*п\/г,\s*2\s*п\/г\s*$', '', names, flags=re.MULTILINE)
        names = re.sub(r'^\s*2\s*п\/г\s*,\s*1\s*п\/г$', '', names, flags=re.MULTILINE)    

        return names

    def get_rooms(self, rooms: str):
        re_rooms = r'\(.*\)'
        if re.search(re_rooms, rooms) is None:          
            for pattern in self.notes_dict:
                regex_result = re.findall(pattern, rooms, flags=re.A)
                if regex_result:
                    rooms = rooms.replace('  ', '').replace(
                        '*', '').replace('\n', '')
                    rooms = re.sub(
                        regex_result[0], self.notes_dict[regex_result[0]] + " ", rooms, flags=re.A)

        splitted_rooms = re.split(r' {2,}|\n', rooms)
        return [room for room in splitted_rooms if room != '']

    def get_teachers(self, teachers_names: str):
        teachers_names = str(teachers_names)
        splitted_teachers = re.split(r' {2,}|\n|,', teachers_names)
        return [teacher.strip() for teacher in splitted_teachers if teacher != '']

    def get_weeks(self, lesson: str, is_even=None, max_weeks=None):
        def get_weeks_list_by_str(weeks_substring, is_even):
            def get_interval_weeks(substring):
                """Получение списка недель из интервальной строки
                с неделями.

                Args:
                    substring (str): строка с интервальными неделями. Пример: '2-5'

                Returns:
                    list(int): возвращает из заданного интервала список номеров
                    недель согласно заданной чётности недели (is_even).

                    Пример (при is_even = True),
                    get_interval_weeks('2-5') -> [2, 4]
                """
                weeks_interval_result = []
                weeks_range = substring.split('-')
                for week in range(int(weeks_range[0].strip()), int(weeks_range[1].strip()) + 1):
                    if is_even is not None:
                        if bool(week % 2) != is_even:
                            weeks_interval_result.append(week)
                    else:
                        weeks_interval_result.append(week)
                return weeks_interval_result

            def get_listed_weeks(substring):
                """Получение списка недель из строки с перечислением недель через
                запятую

                Args:
                    substring (str): строка с перечислением недель. Пример: '2,3,4,5'

                Returns:
                    list(int): возвращает из заданного перечисления список номеров
                    недель согласно заданной чётности недели (is_even).

                    Пример (при is_even = False),
                    get_interval_weeks('2,3,4,5,6,7') -> [3, 5, 7]
                """
                weeks_listed_result = []
                substring = re.sub(r'^([\W\s])+|([\W\s])+$', "", substring)
                weeks_list = substring.split(',')
                for week in weeks_list:
                    week_num = int(week.strip())
                    if is_even is not None:
                        if bool(week_num % 2) != is_even:
                            weeks_listed_result.append(week_num)
                    else:
                        weeks_listed_result.append(week_num)
                return weeks_listed_result

            weeks_result = []

            # интервальный способ задания + перечисление доп. недель
            if '-' in weeks_substring and ',' in weeks_substring:
                interval_pattern = r'(\d+ *- *\d+)'
                interval_weeks_substring = re.findall(
                    interval_pattern, weeks_substring)[0]

                weeks_result += get_interval_weeks(interval_weeks_substring)
                weeks_substring = re.sub(interval_pattern, "", weeks_substring)
                # для удаления ненужных символов в начале и конце строки
                weeks_substring = re.sub(
                    r'^(?:[\W\s])+|(?:[\W\s])+$', "", weeks_substring)
                weeks_result += get_listed_weeks(weeks_substring)
                weeks_result.sort()

            # если это интервальный способ задания недель (прим.: 1-6 н.),
            # то создаём интервал из этих недель и не забываем проверить чётность
            elif '-' in weeks_substring:
                weeks_result += get_interval_weeks(weeks_substring)

            # список недель через запятую
            elif ',' in weeks_substring:
                weeks_result += get_listed_weeks(weeks_substring)

            # если задана одиночная неделя
            else:
                clear_week = weeks_substring.strip()
                if len(clear_week) > 0:
                    weeks_result.append(int(clear_week))

            return weeks_result

        result = []

        lesson = self.__fix_typos(lesson)

        lessons = self.__split_lessons(lesson)

        for lesson in lessons:
            # ниже мы ищем с помощью паттерна регулярного выражения только строку,
            # в которой перечисляются номера недель. Строку разбиваем на список
            # с помощью разделителя, убарем лишние пробелы и преобразуем строковые
            # номера в целочисленный формат, затем мы исключаем те недели,
            # которые были исключены в расписании с помощью ключевого слова "кроме",
            # а также проверяем, стоит ли неделя в правильной чётности.

            lesson = lesson.lower()

            include_weeks = \
                r'(\b(\d+[-, ]*)+)((н|нед)?(?![.\s,\-\d]*(?:подгруппа|подгруп|подгр|п\/г|группа|гр))(\.|\b))'
            exclude_weeks = r'(\b(кр|кроме)(\.|\b)\s*)' + include_weeks

            exclude_weeks_substr = re.search(exclude_weeks, lesson)
            # 4-я группа в данном контексте - это только номера недель.
            # см. https://regex101.com/
            exclude_weeks_substr = '' if exclude_weeks_substr is None \
                else exclude_weeks_substr.group(4)

            # необходимо исключить недели исключения из строки, чтобы недели
            # включения не пересекались с ними при вызове метода поиска
            lesson = re.sub(exclude_weeks, "", lesson)
            incldue_weeks_substr = re.search(include_weeks, lesson)
            incldue_weeks_substr = '' if incldue_weeks_substr is None else incldue_weeks_substr.group(
                1)

            # удаляем лишние пробелы слева и справа
            incldue_weeks_substr = incldue_weeks_substr.strip()
            exclude_weeks_substr = exclude_weeks_substr.strip()

            # получаем список int чисел неделю включения и исключения
            nums_include_weeks = get_weeks_list_by_str(
                incldue_weeks_substr, is_even)
            nums_exclude_weeks = get_weeks_list_by_str(
                exclude_weeks_substr, is_even)

            total_weeks = []

            # если не указаны недели включения, но указаны недели исключения,
            # то это значит, что предмет прозодит на всех неделяк, кроме
            # недель исключений
            if len(nums_include_weeks) == 0 and len(nums_exclude_weeks) > 0:
                for i in range(1, max_weeks + 1):
                    if i not in nums_exclude_weeks:
                        if is_even is not None:
                            if bool(i % 2) != is_even:
                                total_weeks.append(i)
                        else:
                            total_weeks.append(i)
            elif len(nums_include_weeks) > 0:
                # проверям, не исключены ли недели предмета с помощью
                # недель исключения
                for week in nums_include_weeks:
                    if week not in nums_exclude_weeks:
                        total_weeks.append(week)
            # если список недель вообще не задан, т.е. предмет проходит всегда
            elif len(nums_include_weeks) == 0 and len(nums_exclude_weeks) == 0:
                if max_weeks is not None:
                    for i in range(1, max_weeks + 1):
                        if is_even is not None:
                            if bool(i % 2) != is_even:
                                total_weeks.append(i)
                        else:
                            total_weeks.append(i)

            result.append(total_weeks)

        return result

    def get_lessons(self, lesson: str) -> list:
        def remove_other(lesson):
            # числа через запятую или тире
            numbers = r'(?:\d+[-,\s.]*)+'
            # удаление слова исключения недель
            remove_exclude = r'\W*(?:кр|кроме)(?:\.|\b)'
            # удаления слов включения недель, при этом игнорирование подгрупп
            remove_weeks = numbers + \
                r'\s*(?:(?:нед|н)|\W)(?![.\s\d,-]*(?:подгруппа|подгруп|подгр|п\/г|группа|гр))[.\s]*'
            # удаление типа проводимого предмета
            remove_types = r'(?:\b(лк|пр|лек|лаб)\b)?'
            # удаление ненужных символов в начале строки
            remove_trash_start = r'(\A\W+\s*)'
            # удаление ненужных символов в конце строки
            remove_trash_end = r'([-,_.\+;]+$)'

            lesson = re.sub(remove_weeks, "", lesson)
            lesson = re.sub(remove_exclude, "", lesson)
            lesson = re.sub(remove_types, "", lesson)
            lesson = re.sub(remove_trash_start, "", lesson)
            lesson = re.sub(remove_trash_end, "", lesson)
            lesson = lesson.strip()

            return lesson

        lesson = self.__fix_typos(lesson)

        result = self.__split_lessons(lesson)

        for i in range(len(result)):
            # если в названии предмета указан тип, то необходимо
            # вернуть его под ключём type
            types_regexp = r'(?:\b(лк|пр|лек|лаб)\b)'
            types_found = re.findall(types_regexp, result[i])
            if len(types_found) > 0:
                result[i] = {'name': remove_other(
                    result[i]), 'type': types_found[0]}
            else:
                result[i] = {'name': remove_other(result[i]), 'type': None}

        return [lesson for lesson in result if lesson['name'] != '']

    def get_types(self, cell: str) -> list:
        splitted_types = re.split(r' {2,}|\n|,', cell)
        lesson_types = [lesson_type.strip() for lesson_type in splitted_types if lesson_type != '']
        for i in range(len(lesson_types)):
            if lesson_types[i] == 'Л':
                lesson_types[i] = 'лек'
            elif lesson_types[i] == 'П':
                lesson_types[i] = 'пр'
            elif lesson_types[i] == 'ЛБ':
                lesson_types[i] = 'лаб'
            elif lesson_types[i] == 'СР':
                lesson_types[i] = 'с/р'
        return lesson_types