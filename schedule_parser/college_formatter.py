import re
from schedule_parser.parser import Parser
from schedule_parser.formatter import Formatter


class CollegeFormatter(Formatter):
    """Реализация форматирования ячеек excel таблицы расписания к нужному формату.
    
    Methods
    -------
    format_lesson_name(self, temp_name: str)
        Форматирование ячейки с названием предмета, получение названия и 
        списка недель.
    format_room_name(self, cell)
        Форматирование ячейки с аудиториями предмета. 
    format_teacher_name(self, teachers_names)
        Форматирования ячейки имён преподавателей.
    format_other(self, cell)
        Прочее форматирование.
    """

    def get_rooms(self, rooms: str):
        if len(rooms) > 1:
            rooms = rooms.split('/')
            for i in range(len(rooms)):
                rooms[i] = rooms[i].strip()
            return rooms
        else:
            return []

    def get_teachers(self, teachers_names: str):
        teachers = re.findall(r'(?:[а-яА-Я]+\s{1,3}[а-яА-Я]\.\s?[а-яА-Я](?:\.|\s|\b|$))', teachers_names)
        for i in range(len(teachers)):
            teachers[i] = teachers[i].strip()
        return teachers

    def get_weeks(self, lesson: str, is_even=None, max_weeks=16):
        result = []
        for lesson in self.__split_lessons(lesson):
            if len(self.get_lessons(lesson)) > 0:
                lessons_weeks_match = re.findall(r'(?:\d\s*н[.\s+]*)', lesson)
                if len(lessons_weeks_match) > 0:
                    for week_substr in lessons_weeks_match:
                        week = int(week_substr.strip().split()[0])
                        if week == 1:
                            result.append([x for x in range(1, max_weeks + 1) if x % 2 == 1])
                        elif week == 2:
                            result.append([x for x in range(1, max_weeks + 1) if x % 2 == 0])
                else:
                    result.append([x for x in range(1, max_weeks + 1)])
        return result
        
    def __split_lessons(self, lesson):
        lessons_weeks_match = [x for x in re.finditer(r'(?:\d\s*н[.\s+]*)', lesson)]
        if len(lessons_weeks_match) == 2:
            result = []
            result.append(lesson[lessons_weeks_match[0].span()[0]:lessons_weeks_match[1].span()[0]].strip())
            result.append(lesson[lessons_weeks_match[1].span()[0]:].strip())
            return result
        return [lesson]
    
    def get_lessons(self, lesson: str) -> list:      
        def remove_other(lesson):
            # удаления слов чётности недель
            remove_weeks = r'(?:\d\s*(?:нед|н)[.\s+]*)'
            # удаление ненужных символов в начале строки
            remove_trash_start = r'(\A\W+\s*)'
            # удаление ненужных символов в конце строки
            remove_trash_end = r'([-,_.\+;]+$)'
            # удаление имён учителей в формате: Фамилия И.О.
            remove_teachers = r'(?:[а-яА-Я]+\s{1,3}[а-яА-Я]\.\s?[а-яА-Я](?:\.|\s|\b|$))'

            lesson = re.sub(remove_weeks, "", lesson)
            lesson = re.sub(remove_teachers, "", lesson)
            lesson = re.sub(remove_trash_start, "", lesson)
            lesson = re.sub(remove_trash_end, "", lesson)
            lesson = lesson.strip()

            return lesson

        lesson = ' '.join(lesson.split())
        result = self.__split_lessons(lesson)

        for i in range(len(result)):
            result[i] = remove_other(result[i])
           
        return [lesson for lesson in result if lesson != '']

    def get_types(self, cell: str) -> list:
        pass