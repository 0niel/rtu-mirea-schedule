import unittest
import sys
import os

sys.path.insert(0, os.getcwd())

from schedule_parser.excel_formatter import ExcelFormatter


class ExcelFormatterGetTeachersTests(unittest.TestCase):
    """Класс юнит-тестирования статических методов форматирования
    класса Parser
    """

    def setUp(self) -> None:
        self.formatter = ExcelFormatter()
        
    def test_get_teacher_0(self):
        result = self.formatter.get_teachers("Козлова Г.Г.\nИсаев Р.А.")
        correct_result = ['Козлова Г.Г.', 'Исаев Р.А.']
        self.assertEqual(result, correct_result)

    def test_get_teacher_1(self):
        result = self.formatter.get_teachers("Шеверева Е.А., Богатырев С.И.")
        correct_result = ['Шеверева Е.А.', 'Богатырев С.И.']
        self.assertEqual(result, correct_result)