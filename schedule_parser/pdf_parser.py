# from schedule_parser.parser import Parser
# import re
# import pdfplumber

# class PDFParser(Parser):
#     """Класс, реализующий методы для парсинга расписания из
#     Excel документов
#     """

#     def __init__(self, path_to_pdf_file) -> None:
#         self.__pdf_path = path_to_pdf_file
#         self.max_weeks = 17

#     def parse(self):
#         """ Парсим pdf файл"""

#         def parseTable(table):
#             """Парсим таблицу"""
#             days = {}

#             for i in range(1, 7):
#                 lessons = {}
#                 lessons['lessons'] = [[], [], [], [], [], [], [], []]
#                 days[str(i)] = lessons

#             for rows in table:
#                 """
#                 Парсит по строчно таблицу пдф

                
#                 one_lesson = {
#                         'weeks: [1,2,3], #Example
#                         'time': 15:40, #It is example
#                         'type': 'пр'
#                         'room': 'Д', #Example
#                         'teacher': 'Лад в. п.' #Если больше одного препода то List
#                 }

#                 days = {
#                     1:{
#                         'lessons': [one_lesson, [], [], [], [], []], #example
#                     },
#                     2...6
#                 }

#                 group_dict = {
#                     "Название группы": "{days}"
#                 }
#                 """

#                 #Получаем именна групп из таблицы
#                 groups = [group_name for group_name in rows[0]
#                           if group_name != "Группа" and group_name != '']

#                 group_dict = {}

#                 #Удаление звёздочки у названия группы. Создание группы словаря
#                 for i in range(len(groups)):
#                     if groups[i][-1] == "*":
#                         groups[i] = groups[i][:-1]
#                     #Копируем заготовку
#                     group_dict[groups[i]] = copy.deepcopy(days)

#                 #Для работы, когда предметов на дни недели больше одного
#                 last_day_index = int
#                 #Работаем по строкам таблицы. Начинаем со 2.
#                 for i in range(2, len(rows)):
#                     day_index = last_day_index
#                     #Если В этот день ещё что-то есть у группы) Не работает!
#                     try:
#                         if rows[i][0] is not None:
#                             day_index = Parser.get_day_num(rows[i][0])
#                             last_day_index = day_index
#                     except:
#                         pass

#                     #Работаем по строке. Ищем информацию
#                     for j in range(1, len(rows[i])):
                        
#                         #Если нашли интеересную для нас информацию
#                         if rows[i][j] != '' and rows[i][j] != None:

#                             one_lesson = dict
#                             one_lesson = {}
#                             #номер пары
#                             time_start = re.findall(
#                                 '\d+:\d+', rows[i][j])[0]

#                             #Конец пары
#                             time_end = re.findall('\d+:\d+', rows[i][j])[1]

#                             #Разделяем информацию для работы
#                             info = re.split(
#                                 r'\n\d+:\d+', rows[i][j], maxsplit=1)

#                             #Поиск кабинетов в строке
#                             classes = re.findall(
#                                 r'\b\w{3}\. \S+', info[1])[0][5:]

#                             #Поиск преподавателей в строке
#                             teachers = re.findall(r'\w+ \w\.\w+', info[1])

#                             #ФОрматируем в нужный формат.
#                             lesson = self.__format_lesson_name(
#                                 re.split(r'\n\d+:\d+', rows[i][j], maxsplit=2)[0])

#                             #Убираем перенос строки
#                             one_lesson['name'] = re.sub(
#                                 "^\s+|\n|\r|\s+$", '',  lesson[0]['name'])

#                             #Берём из include
#                             one_lesson['weeks'] = lesson[0]['include']

#                             #Поумолчанию ставим практику
#                             one_lesson['type'] = 'пр'

#                             #Если переподавателей больше одного возвращаем список, иначе строку
#                             one_lesson['teacher'] = teachers if len(
#                                 teachers) > 1 else teachers[0]
#                             one_lesson['room'] = classes

#                             #Получаем кортечь. (index, time)
#                             list_tuples_Indexs_lesson = self._GetIndexListLessonsBetweenTime(
#                                 time_start, time_end)

#                             for tuple_index in list_tuples_Indexs_lesson:

#                                 #Получаем время из tuple
#                                 one_lesson['time'] = tuple_index[1]
#                                 group_dict[groups[j-1]][str(day_index)]['lessons'][tuple_index[0]-1] = [one_lesson]

#                             #Добавить логирование
#                 for group_name in list(group_dict):
#                     Schedule.save(
#                             group_name, group_dict[group_name])

#         #Работа при открытом файле
#         with pdfplumber.open(self.__pdf_path) as pdf:
#             pages = pdf.pages
#             for page in pages:
#                 try:
#                     parseTable(page.extract_tables(
#                         table_settings={"vertical_strategy": "lines"}))
#                 except:
#                     pass
