"""
Юнит тестирование парсера расписания
Автор: https://github.com/YaSlavar
"""
import unittest
import sys
sys.path.append('../..')
from schedule_parser.parser import Parser
import time
class FormatterTests(unittest.TestCase):
    """Класс юнит-тестирования статических методов форматирования
    класса Parser
    """

    def setUp(self) -> None:
        self.parser = Parser()

    def test_example_0(self):
        result = self.parser._format_lesson_name(
            '1-17 н. (кр. 3 н.) Архитектура утройств и систем вычислительной техники')
        correct_result = [{'name': 'Архитектура утройств и систем вычислительной техники',
                           'include': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], 
                           'except': [3]}]
        self.assertEqual(result, correct_result)

    def test_example_1(self):
        result = self.parser._format_lesson_name(
            "2,6,10,14 н Экология\n4,8,12,16 Правоведение")
        correct_result = [{'name': 'Экология',
                           'include': [2, 6, 10, 14], 'except': []},
                          {'name': 'Правоведение',
                           'include': [4, 8, 12, 16], 'except': []}]
        self.assertEqual(result, correct_result)

    def test_example_2(self):
        result = self.parser._format_lesson_name("Деньги, кредит, банки кр. 2,8,10 н.")
        correct_result = [{'name': 'Деньги, кредит, банки', 'include': [],
                           'except': [2, 8, 10]}]
        self.assertEqual(result, correct_result)

    def test_example_3(self):
        result = self.parser._format_lesson_name("Орг. Химия (1-8 н.)")
        correct_result = [{'name': 'Орг. Химия', 
                           'include': [1, 2, 3, 4, 5, 6, 7, 8], 'except': []}]
        self.assertEqual(result, correct_result)

    def test_example_4(self):
        result = self.parser._format_lesson_name("Web-технологии в деятельности экономических субьектов")
        correct_result = [{'name': 'Web-технологии в деятельности экономических субьектов', 
                           'include': [], 'except': []}]
        self.assertEqual(result, correct_result)

    def test_example_5(self):
        result = self.parser._format_lesson_name("1,5,9,13 н Оперционные системы\n3,7,11,15 н  Оперционные системы")
        correct_result = [{'name': 'Оперционные системы', 'include': [1, 5, 9, 13], 'except': []},
                          {'name': 'Оперционные системы', 'include': [3, 7, 11, 15], 'except': []}]
        self.assertEqual(result, correct_result)

    def test_example_6(self):
        result = self.parser._format_lesson_name(
            "3,7,11,15  н Физика                                                     кр. 5,8,13.17 н Организация ЭВМ и Систем"
            )
        correct_result = [{'name': 'Физика', 'include': [3, 7, 11, 15], 
                           'except': []},
                          {'name': 'Организация ЭВМ и Систем', 'include': [], 
                           'except': [5, 8, 13, 17]}]
        self.assertEqual(result, correct_result)

    def test_example_7(self):
        result = self.parser._format_lesson_name(
            "2,6,10,14 н Кроссплатформенная среда исполнения программного \
обеспечения 4,8,12,16 н Кроссплатформенная среда исполнения программного обеспечения"
            )
        correct_result = [{'name': 'Кроссплатформенная среда исполнения программного обеспечения', 
                           'include': [2, 6, 10, 14], 'except': []},
                          {'name': 'Кроссплатформенная среда исполнения программного обеспечения', 
                           'include': [4, 8, 12, 16], 'except': []}]
        self.assertEqual(result, correct_result)

    def test_example_8(self):
        result = self.parser._format_lesson_name("кр 1,13 н Интеллектуальные информационные системы")
        correct_result = [{'name': 'Интеллектуальные информационные системы', 'include': [],
                           'except': [1, 13]}]
        self.assertEqual(result, correct_result)

    def test_example_9(self):
        result = self.parser._format_lesson_name("кр1 н Модели информационных процессов и систем")
        correct_result = [{'name': 'Модели информационных процессов и систем', 
                           'include': [], 'except': [1]}]
        self.assertEqual(result, correct_result)

    def test_example_10(self):
        result = self.parser._format_lesson_name("Разработка ПАОИиАС 2,6,10,14 н.+4,8,12,16н.")
        correct_result = [{'name': 'Разработка ПАОИиАС', 
                           'include': [2, 6, 10, 14, 4, 8, 12, 16], 
                           'except': []}]
        self.assertEqual(result, correct_result)

    def test_example_11(self):
        result = self.parser._format_lesson_name("Физика, кроме 13 н")
        correct_result = [{'name': 'Физика', 'include': [], 'except': [13]}]
        self.assertEqual(result, correct_result)

    def test_example_12(self):
        result = self.parser._format_lesson_name("4, 8, 12,16 н ;2,10нед Программно-аппаратные средства защиты информации")
        correct_result = [{'name': 'Программно-аппаратные средства защиты информации', 
                           'include': [4, 8, 12, 16, 2, 10], 'except': []}]
        self.assertEqual(result, correct_result)

    def test_example_13(self):
        result = self.parser._format_lesson_name(
            "(3,7,11,15 н. - лк; 5,9,13,17 н. - пр) Современные проблемы и методы прикладной информатики и развития информационного общества")
        correct_result = [{
            'name': 'Современные проблемы и методы прикладной информатики и развития информационного общества', 
            'include': [3, 7, 11, 15, 5, 9, 13, 17], 
            'except': []}]
        self.assertEqual(result, correct_result)

    def test_example_14(self):
        result = self.parser._format_lesson_name(
            "2,6,10,14нед. Техническая защита информации")
        correct_result = [{'name': 'Техническая защита информации', 
                           'include': [2, 6, 10, 14], 
                           'except': []}]
        self.assertEqual(result, correct_result)

    def test_example_15(self):
        result = self.parser._format_lesson_name(
            "2-16 н. Разработка ПАОИАС")
        correct_result = [{'name': 'Разработка ПАОИАС',
                           'include': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                           'except': []}]
        self.assertEqual(result, correct_result)
        
    def test_example_15(self):
        result = self.parser._format_lesson_name(
            "2-16 н. Разработка ПАОИАС")
        correct_result = [{'name': 'Разработка ПАОИАС',
                           'include': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                           'except': []}]
        self.assertEqual(result, correct_result)
        
    def test_example_16(self):
        result = self.parser._format_lesson_name(
            "Ин. яз")
        correct_result = [{'name': 'Ин. яз',
                           'include': [],
                           'except': []}]
        self.assertEqual(result, correct_result)


    def test_format_teacher_name_example_1(self):
        result = self.parser._format_teacher_name("Козлова Г.Г.\nИсаев Р.А.")
        correct_result = ['Козлова Г.Г.', 'Исаев Р.А.']
        self.assertEqual(result, correct_result)

    def test_format_room_name_example_1(self):
        result = self.parser._format_room_name("В-78*\nБ-105")
        correct_result = ['Проспект Вернадского, д.78 Б-105']
        self.assertEqual(result, correct_result)

    def test_format_room_name_example_2(self):
        result = self.parser._format_room_name("23452     Б-105")
        correct_result = ['23452', 'Б-105']
        self.assertEqual(result, correct_result)

    def test_format_room_name_example_3(self):
        result = self.parser._format_room_name('В-78*А318 \n429')
        correct_result = ['Проспект Вернадского, д.78 А318 429']
        self.assertEqual(result, correct_result)

    def test_get_lesson_weeks_1(self):
        result = self.parser._get_lesson_with_weeks(
            'кр. 12 н. Математический анализ', True)
        correct_result = [{'name': 'Математический анализ', 
                           'weeks': [2, 4, 6, 8, 10, 14, 16]}]
        self.assertEqual(result, correct_result)

    def test_get_lesson_weeks_2(self):
        result = self.parser._get_lesson_with_weeks(
            "3-10 н. Математический анализ", True)
        correct_result = [{'name': 'Математический анализ', 
                           'weeks': [4, 6, 8, 10]}]
        self.assertEqual(result, correct_result)
        
    def test_get_lesson_weeks_3(self):
        result = self.parser._get_lesson_with_weeks(
            "5 н. Математический анализ", True)
        correct_result = [{'name': 'Математический анализ', 'weeks': []}]
        self.assertEqual(result, correct_result)
        
    def test_get_lesson_weeks_4(self):
        result = self.parser._get_lesson_with_weeks(
            "2-16 н. (кр. 12 н.) Технология проектирования устройств и систем ", True)
        correct_result = [{'name': 'Технология проектирования устройств и систем', 
                           'weeks': [2, 4, 6, 8, 10, 14, 16]}]
        self.assertEqual(result, correct_result)
        
    def test_get_lesson_weeks_5(self):
        result = self.parser._get_lesson_with_weeks(
            "Математическая логика и теория алгоритмов", False)
        correct_result = [{'name': 'Математическая логика и теория алгоритмов', 
                           'weeks': [i for i in range(1, self.parser.max_weeks + 1) if i % 2 == 1]}]
        self.assertEqual(result, correct_result)

if __name__ == '__main__':
    unittest.main()
