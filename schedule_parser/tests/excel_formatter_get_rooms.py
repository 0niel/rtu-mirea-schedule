import unittest
import sys
import os

sys.path.insert(0, os.getcwd())

from schedule_parser.excel_formatter import ExcelFormatter


class ExcelFormatterGetRoomsTests(unittest.TestCase):
    """Класс юнит-тестирования статических методов форматирования
    класса Parser
    """

    def setUp(self) -> None:
        self.formatter = ExcelFormatter()
        
    def test_get_rooms_0(self):
        result = self.formatter.get_rooms("В-78*\nБ-105")
        correct_result = ['Проспект Вернадского, д.78 Б-105']
        self.assertEqual(result, correct_result)

    def test_get_rooms_1(self):
        result = self.formatter.get_rooms("23452     Б-105")
        correct_result = ['23452', 'Б-105']
        self.assertEqual(result, correct_result)

    def test_get_rooms_2(self):
        result = self.formatter.get_rooms('В-78*А318 \n429')
        correct_result = ['Проспект Вернадского, д.78 А318 429']
        self.assertEqual(result, correct_result)
        