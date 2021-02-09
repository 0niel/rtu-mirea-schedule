import unittest
from reader import Reader


class Format_name_test(unittest.TestCase):
    def setUp(self) -> None:
        self.reader = Reader()

    def test_example_1(self):
        result = self.reader.format_name("2,6,10,14 н Экология\n4,8,12,16 Правоведение")
        correct_result = [['Экология', ['2', '6', '10', '14'], ''], ['Правоведение', ['4', '8', '12', '16'], '']]
        self.assertEqual(result, correct_result)

    def test_example_2(self):
        result = self.reader.format_name("Деньги, кредит, банки кр. 2,8,10 н.")
        correct_result = [['Деньги, кредит, банки', '', ['2', '8', '10']]]
        self.assertEqual(result, correct_result)

    def test_example_3(self):
        result = self.reader.format_name("Орг. Химия (1-8 н.)")
        correct_result = [['Орг. Химия', [1, 2, 3, 4, 5, 6, 7, 8], '']]
        self.assertEqual(result, correct_result)

    def test_example_4(self):
        result = self.reader.format_name("Web-технологии в деятельности экономических субьектов")
        correct_result = [['Web-технологии в деятельности экономических субьектов', '', '']]
        self.assertEqual(result, correct_result)

    def test_example_5(self):
        result = self.reader.format_name("1,5,9,13 н Оперционные системы\n3,7,11,15 н  Оперционные системы")
        correct_result = [['Оперционные системы', ['1', '5', '9', '13'], ''],
                          ['Оперционные системы', ['3', '7', '11', '15'], '']]
        self.assertEqual(result, correct_result)

    def test_example_6(self):
        result = self.reader.format_name(
            "3,7,11,15  н Физика                                                     кр. 5,8,13.17 н Организация ЭВМ и Систем")
        correct_result = [['Физика', ['3', '7', '11', '15'], ''],
                          ['Организация ЭВМ и Систем', '', ['5', '8', '13', '17']]]
        self.assertEqual(result, correct_result)

    def test_example_7(self):
        result = self.reader.format_name(
            "2,6,10,14 н Кроссплатформенная среда исполнения программного обеспечения 4,8,12,16 н Кроссплатформенная среда исполнения программного обеспечения")
        correct_result = [['Кроссплатформенная среда исполнения программного обеспечения', ['2', '6', '10', '14'], ''],
                          ['Кроссплатформенная среда исполнения программного обеспечения', ['4', '8', '12', '16'], '']]
        self.assertEqual(result, correct_result)

    def test_example_8(self):
        result = self.reader.format_name("кр 1,13 н Интеллектуальные информационные системы")
        correct_result = [['Интеллектуальные информационные системы', '', ['1', '13']]]
        self.assertEqual(result, correct_result)

    def test_example_9(self):
        result = self.reader.format_name("кр1 н Модели информационных процессов и систем")
        correct_result = [['Модели информационных процессов и систем', '', ['1']]]
        self.assertEqual(result, correct_result)

    def test_example_10(self):
        result = self.reader.format_name("Разработка ПАОИиАС 2,6,10,14 н.+4,8,12,16н.")
        correct_result = [['Разработка ПАОИиАС', ['2', '6', '10', '14', '4', '8', '12', '16'], '']]
        self.assertEqual(result, correct_result)

    def test_example_11(self):
        result = self.reader.format_name("Физика, кроме 13 н")
        correct_result = [['Физика', '', ['13']]]
        self.assertEqual(result, correct_result)

    def test_example_12(self):
        result = self.reader.format_name("4, 8, 12,16 н ;2,10нед Программно-аппаратные средства защиты информации")
        correct_result = [['Программно-аппаратные средства защиты информации', ['4', '8', '12', '16', '2', '10'], '']]
        self.assertEqual(result, correct_result)

    def test_example_13(self):
        result = self.reader.format_name(
            "(3,7,11,15 н. - лк; 5,9,13,17 н. - пр) Современные проблемы и методы прикладной информатики и развития информационного общества")
        correct_result = [['Современные проблемы и методы прикладной информатики и развития информационного общества',
                           ['3', '7', '11', '15', '5', '9', '13', '17'],
                           '']]
        self.assertEqual(result, correct_result)

    def test_example_14(self):
        result = self.reader.format_name(
            "2,6,10,14нед. Техническая защита информации")
        correct_result = [['Техническая защита информации', ['2', '6', '10', '14'], '']]
        self.assertEqual(result, correct_result)

    def test_example_15(self):
        result = self.reader.format_name(
            "2-16 н. Разработка ПАОИАС")
        correct_result = [['Разработка ПАОИАС',
                           [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                           '']]
        self.assertEqual(result, correct_result)

    def test_format_teacher_name_example_1(self):
        result = self.reader.format_teacher_name("Козлова Г.Г.\nИсаев Р.А.")
        correct_result = ['Козлова Г.Г.', 'Исаев Р.А.']
        self.assertEqual(result, correct_result)

    def test_format_room_name_example_1(self):
        result = self.reader.format_room_name("В-78*\nБ-105")
        correct_result = ['Проспект Вернадского, д.78 Б-105']
        self.assertEqual(result, correct_result)

    def test_format_room_name_example_2(self):
        result = self.reader.format_room_name("23452     Б-105")
        correct_result = ['23452', 'Б-105']
        self.assertEqual(result, correct_result)

    def test_format_room_name_example_3(self):
        result = self.reader.format_room_name('В-78*А318 \n429')
        correct_result = ['Проспект Вернадского, д.78 А318 429']
        self.assertEqual(result, correct_result)


if __name__ == '__main__':
    unittest.main()
