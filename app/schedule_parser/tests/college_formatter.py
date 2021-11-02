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
        correct_result = ['МДК.04.02 Современные технологии управления структурным подразделением']
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_1(self):
        result = self.formatter.get_lessons(
            '1 н.                                                                ОП.15                                              ТЕОРИЯ ИНФОРМАЦИОННЫХ СИСТЕМ                                       Стоколос М.Д.                                                                             2 н.                                                          ОП.14                                              ИНФОРМАЦИОННАЯ БЕЗОПАСНОСТЬ                        Черный Д.В.                                                    ')
        correct_result = ['ОП.15 Теория информационных систем', 'ОП.14 Информационная безопасность']
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_2(self):
        result = self.formatter.get_lessons('1 н.                                       ОГСЭ.01                               ОСНОВЫ ФИЛОСОФИИ                      Тихомирова А.Ю.                  2 н.                                            --------------------------')
        correct_result = ['ОГСЭ.01 Основы философии']
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
        
    def test_get_rooms_0(self):
        result = self.formatter.get_rooms('206  \n/ 329 ')
        correct_result = ['206', '329']
        self.assertEqual(result, correct_result)
        
    def test_get_rooms_1(self):
        result = self.formatter.get_rooms(' 270')
        correct_result = ['270']
        self.assertEqual(result, correct_result)
        
    def test_get_rooms_2(self):
        result = self.formatter.get_rooms('')
        correct_result = []
        self.assertEqual(result, correct_result)
        
    def test_get_teachers_0(self):
        result = self.formatter.get_teachers('ОУД.09                                ФИЗИКА                           Михайлюкова Л.Я.')
        correct_result = ['Михайлюкова Л.Я.']
        self.assertEqual(result, correct_result)
        
    def test_get_teachers_1(self):
        result = self.formatter.get_teachers('1 н.                                       ЛИТЕРАТУРА                   Ванькина В.Б.                     2 н.                                           ---------------------')
        correct_result = ['Ванькина В.Б.']
        self.assertEqual(result, correct_result)
        
    def test_get_teachers_2(self):
        result = self.formatter.get_teachers('ОУД.03                                  ИНОСТРАННЫЙ ЯЗЫК                                 Олейник А.В.                        Михайлина А.А.')
        correct_result = ['Олейник А.В.', 'Михайлина А.А.']
        self.assertEqual(result, correct_result)
        
    def test_get_teachers_3(self):
        result = self.formatter.get_teachers('ОУД.04                             МАТЕМАТИКА: алгебра и начала математического анализа, геометрия            Сапрыгина С.В.')
        correct_result = ['Сапрыгина С.В.']
        self.assertEqual(result, correct_result)