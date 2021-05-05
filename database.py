"""
База данных и основные коллекции для работы с MongoDB
"""
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client['schedule']

# коллекция, в которой хранится актуальное расписание
# для текущего семестра
semester_collection = db['semester']

# коллекция, в которой хранится актуальное расписание
# для текущей (или последней прошедшей) экзаминационной
# сессии
exam_collection = db['exam']
