import unittest
import sys
import os

sys.path.insert(0, os.getcwd())

from schedule_parser.excel_formatter import ExcelFormatter

# todo:
# 11,15 н/ 17 н Технологии обработки материалов концентрированными потоками энергии	[] лек/ лр

# 2,4,6,16 н - пр/ 10,14 н - лр 1+2 гр 
# Технологии и оборудование АП в машиностроении
# 8,12 н Защита интелл. собственности в машиностроении


class ExcelFormatterGetLessonsTests(unittest.TestCase):
    """Класс юнит-тестирования статических методов форматирования
    класса Parser
    """

    def setUp(self) -> None:
        self.formatter = ExcelFormatter()

    def test_get_lessons_0(self):
        result = self.formatter.get_lessons(
            '1-17 н. (кр. 3 н.) Архитектура утройств и систем вычислительной техники')
        correct_result = [
            {'name': 'Архитектура утройств и систем вычислительной техники', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_1(self):
        result = self.formatter.get_lessons(
            'кр. 3,5 н. Теория автоматического управления')
        correct_result = [{'name': 'Теория автоматического управления', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_2(self):
        result = self.formatter.get_lessons(
            '8,10 н. Цифровые системы управления')
        correct_result = [{'name': 'Цифровые системы управления', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_3(self):
        result = self.formatter.get_lessons(
            '7 н. Вычислительные системы реального времени')
        correct_result = [{'name': 'Вычислительные системы реального времени', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_4(self):
        result = self.formatter.get_lessons(
            '2,6,10,14 н Экология\n4,8,12,16 Правоведение')
        correct_result = [{'name': 'Экология', 'type': None}, {'name': 'Правоведение', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_5(self):
        result = self.formatter.get_lessons(
            'Деньги, кредит, банки кр. 2,8,10 н.')
        correct_result = [{'name': 'Деньги, кредит, банки', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_6(self):
        result = self.formatter.get_lessons(
            '2,6,10,14 н Экология\n4,8,12,16 Правоведение')
        correct_result = [{'name': 'Экология', 'type': None}, {'name': 'Правоведение', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_7(self):
        result = self.formatter.get_lessons(
            '3,7,11,15  н Физика                                                     кр. 5,8,13.17 н Организация ЭВМ и Систем')
        correct_result = [{'name': 'Физика', 'type': None}, {'name': 'Организация ЭВМ и Систем', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_8(self):
        result = self.formatter.get_lessons(
            'Практика по получению профессиональных умений и опыта профессиональной деятельности')
        correct_result = [
            {'name': 'Практика по получению профессиональных умений и опыта профессиональной деятельности', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_9(self):
        result = self.formatter.get_lessons(
            '4,8,12,16 н. Интерфейсы и периферийные устройства\n10 н. Микропроцессорные системы\n14 н. Микропроцессорные системы')
        correct_result = [{'name': 'Интерфейсы и периферийные устройства', 'type': None},
                          {'name': 'Микропроцессорные системы', 'type': None}, 
                          {'name': 'Микропроцессорные системы', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_10(self):
        result = self.formatter.get_lessons(
            'кр.5 н. Основы научно-технического творчества')
        correct_result = [{'name': 'Основы научно-технического творчества', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_11(self):
        result = self.formatter.get_lessons(
            'Ин. яз')
        correct_result = [{'name': 'Ин. яз', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_12(self):
        result = self.formatter.get_lessons(
            '(3,7,11,15 н. - лк; 5,9,13,17 н. - пр) Современные проблемы и методы прикладной информатики и развития информационного общества')
        correct_result = [
            {'name': 'Современные проблемы и методы прикладной информатики и развития информационного общества', 'type': 'лк'},  {'name': 'Современные проблемы и методы прикладной информатики и развития информационного общества', 'type': 'пр'}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_13(self):
        result = self.formatter.get_lessons(
            '2-16 н. Разработка ПАОИАС')
        correct_result = [{'name': 'Разработка ПАОИАС', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_14(self):
        result = self.formatter.get_lessons(
            '2,6,10,14нед. Техническая защита информации')
        correct_result = [{'name': 'Техническая защита информации', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_15(self):
        result = self.formatter.get_lessons(
            'кр. 5 н. Вычислительные системы реального времени')
        correct_result = [{'name': 'Вычислительные системы реального времени', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_16(self):
        result = self.formatter.get_lessons(
            '7,9 н. Технические средства автоматизации и управления\n11,13,15 н. Теория автоматического управления')
        correct_result = [{'name': 'Технические средства автоматизации и управления', 'type': None}, 
                          {'name': 'Теория автоматического управления', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_17(self):
        result = self.formatter.get_lessons(
            'Ин.яз. 1,2 подгр')
        correct_result = [{'name': 'Ин.яз. 1,2 подгр', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_18(self):
        result = self.formatter.get_lessons(
            '……………………')
        correct_result = []
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_19(self):
        result = self.formatter.get_lessons(
            'Ознакомительная практика')
        correct_result = [{'name': 'Ознакомительная практика', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_20(self):
        result = self.formatter.get_lessons(
            'Разработка ПАОИиАС 2,6,10,14 н.+4,8,12,16н.')
        correct_result = [{'name': 'Разработка ПАОИиАС', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_21(self):
        result = self.formatter.get_lessons(
            'кр. 3,17 н. Организация работы с технотронными документами\n3 н. Организация работы с технотронными документами')
        correct_result = [{'name': 'Организация работы с технотронными документами', 'type': None}, 
                          {'name': 'Организация работы с технотронными документами', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_22(self):
        result = self.formatter.get_lessons(
            '11н Суд присяжных в России и зарубежных странах')
        correct_result = [{'name': 'Суд присяжных в России и зарубежных странах', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_23(self):
        result = self.formatter.get_lessons(
            '2,8, н Технологии развития имиджа территории')
        correct_result = [{'name': 'Технологии развития имиджа территории', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_24(self):
        result = self.formatter.get_lessons(
            '14н Основы конструирования и технологии приборостроения')
        correct_result = [{'name': 'Основы конструирования и технологии приборостроения', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_25(self):
        result = self.formatter.get_lessons(
            '1,3,9,13 н. Конфиденциальное делопроизводство 5,7,11,15 н. Деньги, кредит,банки')
        correct_result = [{'name': 'Конфиденциальное делопроизводство', 'type': None}, 
                          {'name': 'Деньги, кредит,банки', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_26(self):
        result = self.formatter.get_lessons(
            '1,5,9,13 н. Физика (1 п/г)\n1,5,9,13 н. Физика (2 п/г)')
        correct_result = [{'name': 'Физика (1 п/г)', 'type': None}, {'name': 'Физика (2 п/г)', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_27(self):
        result = self.formatter.get_lessons(
            'Ин.яз 1,2 подгруп')
        correct_result = [{'name': 'Ин.яз 1,2 подгруп', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_28(self):
        result = self.formatter.get_lessons(
            'англ.яз. (2подгр.)')
        correct_result = [{'name': 'англ.яз. (2подгр.)', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_29(self):
        result = self.formatter.get_lessons(
            ' 3,7,9 н Магнитодиагностика неоднородных материалов;  11,13,15 н Магнитодиагностика неоднородных материалов 1 гр; 17 н Магнитодиагностика неоднородных материалов 2 гр')
        correct_result = [{'name': 'Магнитодиагностика неоднородных материалов', 'type': None}, 
                          {'name': 'Магнитодиагностика неоднородных материалов 1 гр', 'type': None}, 
                          {'name': 'Магнитодиагностика неоднородных материалов 2 гр', 'type': None}]
        self.assertEqual(result, correct_result)
    
    def test_get_lessons_30(self):
        result = self.formatter.get_lessons(
            '1гр.=5,9,13н.; 2гр.=7,11,15н. Разработка и эксплуатация защищенных автоматизированных систем')
        correct_result = [{'name': 'Разработка и эксплуатация защищенных автоматизированных систем 1 груп', 'type': None}, 
                          {'name': 'Разработка и эксплуатация защищенных автоматизированных систем 2 груп', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_31(self):
        result = self.formatter.get_lessons(
            '5,7,11,13 н ФОПИ\n9 н Оптические аналитические приборы и методы исследований\n15 н Основы конструирования и технологии приборостроения')
        correct_result = [{'name': 'ФОПИ', 'type': None}, 
                          {'name': 'Оптические аналитические приборы и методы исследований', 'type': None},
                          {'name': 'Основы конструирования и технологии приборостроения', 'type': None}]
        self.assertEqual(result, correct_result)

    def test_get_lessons_32(self):
        result = self.formatter.get_lessons(
            '2-8 н Теория соединения материалов\n10,14н-1гр 12,16н-2 гр Тепл. проц. в ТС')
        correct_result = [{'name': 'Теория соединения материалов', 'type': None}, 
                          {'name': 'Тепл. проц. в ТС 1 груп', 'type': None},
                          {'name': 'Тепл. проц. в ТС 2 груп', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_33(self):
        result = self.formatter.get_lessons(
            '2,4,6,8 н. Аудит 10,12 н. Финансовый мониторинг')
        correct_result = [{'name': 'Аудит', 'type': None}, 
                          {'name': 'Финансовый мониторинг', 'type': None}]
        self.assertEqual(result, correct_result)
    
    def test_get_lessons_34(self):
        result = self.formatter.get_lessons(
            ' 1,3,5,7 н Контроль и ревизия 9,11 Аудит')
        correct_result = [{'name': 'Контроль и ревизия', 'type': None}, 
                          {'name': 'Аудит', 'type': None}]
        self.assertEqual(result, correct_result)
    
    def test_get_lessons_35(self):
        result = self.formatter.get_lessons(
            '2,4,6,8 н Металловедение черных, цветных и драгоценных металлов и сплавов, 1 гр\n2,4,6,8  Методы неразрушающего контроля, 2 гр')
        correct_result = [{'name': 'Металловедение черных, цветных и драгоценных металлов и сплавов, 1 гр', 'type': None}, 
                          {'name': 'Методы неразрушающего контроля, 2 гр', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_36(self):
        result = self.formatter.get_lessons(
            '1гр.= 2н.; 2гр.=4н. Криптографические методы защиты информации;               6,8 н. Основы формирования каналов воздействия на информационные системы')
        correct_result = [{'name': 'Основы формирования каналов воздействия на информационные системы', 'type': None},
                          {'name': 'Криптографические методы защиты информации 1 груп', 'type': None},
                          {'name': 'Криптографические методы защиты информации 2 груп', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_37(self):
        result = self.formatter.get_lessons(
            '2,4,6,8,10 (лк),12,14н (пр) Инструментарий информационно-аналитической деятельности\n2,4,6,8,10 н (пр) Практический аудит ')
        correct_result = [{'name': 'Инструментарий информационно-аналитической деятельности', 'type': 'лк'},
                          {'name': 'Инструментарий информационно-аналитической деятельности', 'type': 'пр'},
                          {'name': 'Практический аудит', 'type': 'пр'}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_38(self):
        result = self.formatter.get_lessons(
            '1гр. 2,6,10,16 н. Безопасность систем баз данных\n8,12 н. Теория кодирования в системах защиты информации')
        correct_result = [{'name': '1гр. Безопасность систем баз данных', 'type': None},
                          {'name': 'Теория кодирования в системах защиты информации', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_39(self):
        result = self.formatter.get_lessons(
            '2гр. 2,6,10,16 н. Безопасность систем баз данных')
        correct_result = [{'name': '2гр. Безопасность систем баз данных', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_40(self):
        result = self.formatter.get_lessons(
            '2-8 н Теория соединения материалов\n10,14н-1гр 12,16н-2 гр Тепл. проц. в ТС')
        correct_result = [{'name': 'Теория соединения материалов', 'type': None},
                          {'name': 'Тепл. проц. в ТС 1 груп', 'type': None},
                          {'name': 'Тепл. проц. в ТС 2 груп', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_41(self):
        result = self.formatter.get_lessons(
            '1гр.=3,7,11,15; 2гр.=1,5,9,13н.Создание автоматизированных систем в защищенном исполнении')
        correct_result = [{'name': 'Создание автоматизированных систем в защищенном исполнении 1 груп', 'type': None},
                          {'name': 'Создание автоматизированных систем в защищенном исполнении 2 груп', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_42(self):
        result = self.formatter.get_lessons(
            '1гр.=4,8,12н.; 2гр.=6,10,14н. Разработка и эксплуатация защищенных автоматизированных систем; 1гр.=2,6,10,14н.; 2гр=4,8,12,16н.=Инфраструктура открытых ключей в СЗИ')
        correct_result = [{'name': 'Разработка и эксплуатация защищенных автоматизированных систем 1 груп', 'type': None},
                          {'name': 'Разработка и эксплуатация защищенных автоматизированных систем 2 груп', 'type': None},
                          {'name': 'Инфраструктура открытых ключей в СЗИ 1 груп', 'type': None},
                          {'name': 'Инфраструктура открытых ключей в СЗИ 2 груп', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_43(self):
        result = self.formatter.get_lessons(
            'кр. 5 н. Разработка конфигураций в среде "1С: Предприятие" ')
        correct_result = [{'name': 'Разработка конфигураций в среде "1С: Предприятие"', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_44(self):
        result = self.formatter.get_lessons(
            '10 н. Разработка конфигураций в среде "1С: Предприятие"  ')
        correct_result = [{'name': 'Разработка конфигураций в среде "1С: Предприятие"', 'type': None}]
        self.assertEqual(result, correct_result)
        
    def test_get_lessons_45(self):
        result = self.formatter.get_lessons(
            'История (история России, всеобщая история)')
        correct_result = [{'name': 'История (история России, всеобщая история)', 'type': None}]
        self.assertEqual(result, correct_result)
        