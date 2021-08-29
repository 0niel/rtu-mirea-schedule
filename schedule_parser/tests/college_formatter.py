import unittest
import sys
import os

sys.path.insert(0, os.getcwd())

from schedule_parser.college_formatter import CollegeFormatter


class CollegeFormatterTests(unittest.TestCase):
    """Класс юнит-тестирования статических методов форматирования
    класса Parser
    """

    def setUp(self) -> None:
        self.formatter = CollegeFormatter()

    def test_get_lessons_0(self):
        result = self.formatter.get_lessons(
            'МДК.04.02                                                СОВРЕМЕННЫЕ ТЕХНОЛОГИИ УПРАВЛЕНИЯ СТРУКТУРНЫМ ПОДРАЗДЕЛЕНИЕМ                         Служевенкова О.С.')
        correct_result = ['МДК.04.02 СОВРЕМЕННЫЕ ТЕХНОЛОГИИ УПРАВЛЕНИЯ СТРУКТУРНЫМ ПОДРАЗДЕЛЕНИЕМ']
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_1(self):
        result = self.formatter.get_lessons(
            '1 н.                                                                ОП.15                                              ТЕОРИЯ ИНФОРМАЦИОННЫХ СИСТЕМ                                       Стоколос М.Д.                                                                             2 н.                                                          ОП.14                                              ИНФОРМАЦИОННАЯ БЕЗОПАСНОСТЬ                        Черный Д.В.                                                    ')
        correct_result = ['ОП.15 ТЕОРИЯ ИНФОРМАЦИОННЫХ СИСТЕМ', 'ОП.14 ИНФОРМАЦИОННАЯ БЕЗОПАСНОСТЬ']
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_2(self):
        result = self.formatter.get_lessons('1 н.                                       ОГСЭ.01                               ОСНОВЫ ФИЛОСОФИИ                      Тихомирова А.Ю.                  2 н.                                            --------------------------')
        correct_result = ['ОГСЭ.01 ОСНОВЫ ФИЛОСОФИИ']
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_3(self):
        result = self.formatter.get_lessons('1 н.                                                ---------------------  ')
        correct_result = []
        self.assertEqual(result, correct_result)
        
    def test_get_weeks_0(self):
        result = self.formatter.get_weeks('1 н.                                                ---------------------  ')
        correct_result = []
        self.assertEqual(result, correct_result)
        
    def test_get_weeks_1(self):
        result = self.formatter.get_weeks('1 н.                                       ОГСЭ.01                               ОСНОВЫ ФИЛОСОФИИ                      Тихомирова А.Ю.                  2 н.                                            --------------------------')
        correct_result = [[1, 3, 5, 7, 9, 11, 13, 15]]
        self.assertEqual(result, correct_result)
        
    def test_get_weeks_2(self):
        result = self.formatter.get_weeks('МДК.04.02                                                СОВРЕМЕННЫЕ ТЕХНОЛОГИИ УПРАВЛЕНИЯ СТРУКТУРНЫМ ПОДРАЗДЕЛЕНИЕМ                         Служевенкова О.С.')
        correct_result = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]]
        self.assertEqual(result, correct_result)