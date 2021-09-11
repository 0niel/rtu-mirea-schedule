import unittest
import sys
import os

sys.path.insert(0, os.getcwd())

from schedule_parser.excel_formatter import ExcelFormatter


class ExcelFormatterGetTypesTests(unittest.TestCase):

    def setUp(self) -> None:
        self.formatter = ExcelFormatter()
        
    def test_get_types_0(self):
        result = self.formatter.get_types("лк\nлк")
        correct_result = ['лк', 'лк']
        self.assertEqual(result, correct_result)

    def test_get_types_1(self):
        result = self.formatter.get_types("пр")
        correct_result = ['пр']
        self.assertEqual(result, correct_result)

    def test_get_types_2(self):
        result = self.formatter.get_types('лаб \nлаб')
        correct_result = ['лаб', 'лаб']
        self.assertEqual(result, correct_result)
        
    def test_get_types_3(self):
        result = self.formatter.get_types('лк\nлк\nлк\nлк')
        correct_result = ['лк', 'лк', 'лк', 'лк']
        self.assertEqual(result, correct_result)