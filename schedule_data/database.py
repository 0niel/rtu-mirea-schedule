"""
База данных и основные коллекции для работы с MongoDB
"""
import motor.motor_asyncio


client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://127.0.0.1:27017/')
db = client['schedule']

# коллекция, в которой хранится актуальное расписание
# для текущего семестра
semester_collection = db['semester']

# коллекция, в которой хранится актуальное расписание
# для текущей (или последней прошедшей) экзаминационной
# сессии
exam_collection = db['exam']
