from calendar import weekday
from typing import List

from app.models.schedule import LessonModel, ScheduleModelResponse, ScheduleModel, TeacherLessonModel, TeacherSchedulesModelResponse
from app.core.config import DATABASE_NAME, SCHEDULE_COLLECTION_NAME
from app.database.database import AsyncIOMotorClient


def save_schedule(
    conn: AsyncIOMotorClient,
    group: str,
    schedule: ScheduleModel
):
    """Сохранение или обновление расписания группы."""
    conn[DATABASE_NAME][SCHEDULE_COLLECTION_NAME].update_one(
        {'group': group},
        {'$set': {'group': group,
                  'schedule':  schedule.dict()}},
        upsert=True
    )


async def get_full_schedule(
    conn: AsyncIOMotorClient,
    group_name: str
) -> ScheduleModelResponse:
    """Получение полного расписания для выбранной группы"""
    schedule = await conn[DATABASE_NAME][SCHEDULE_COLLECTION_NAME].find_one(
        {'group': group_name}, {'_id': 0})

    if schedule:
        schedule_with_num_keys = {
            '1': schedule['schedule']['monday'],
            '2': schedule['schedule']['tuesday'],
            '3': schedule['schedule']['wednesday'],
            '4': schedule['schedule']['thursday'],
            '5': schedule['schedule']['friday'],
            '6': schedule['schedule']['saturday'],
        }
        return ScheduleModelResponse(group=schedule['group'],
                                     schedule=schedule_with_num_keys)


async def get_groups(conn: AsyncIOMotorClient) -> List[str]:
    """Получение списка всех групп, для которых доступно расписание"""
    cursor = conn[DATABASE_NAME][SCHEDULE_COLLECTION_NAME].find(
        {}, {'group': 1, '_id': 0})
    groups = await cursor.to_list(None)
    groups = [group['group'] for group in groups]

    if len(groups) > 0:
        return groups


async def find_teacher(conn: AsyncIOMotorClient, teacher_name: str) -> TeacherSchedulesModelResponse:
    # todo: [А-Яа-я]+\s+[А-Яа-я]\.\s*[А-Я]\.
    request_data = {'$or': [
        {"schedule.monday.lessons": {'$elemMatch': {
            '$elemMatch': {"teachers": {'$regex': teacher_name, '$options': 'i'}}}}},
        {"schedule.tuesday.lessons": {'$elemMatch': {
            '$elemMatch': {"teachers": {'$regex': teacher_name, '$options': 'i'}}}}},
        {"schedule.wednesday.lessons": {'$elemMatch': {
            '$elemMatch': {"teachers": {'$regex': teacher_name, '$options': 'i'}}}}},
        {"schedule.thursday.lessons": {'$elemMatch': {
            '$elemMatch': {"teachers": {'$regex': teacher_name, '$options': 'i'}}}}},
        {"schedule.friday.lessons": {'$elemMatch': {
            '$elemMatch': {"teachers": {'$regex': teacher_name, '$options': 'i'}}}}},
        {"schedule.saturday.lessons": {'$elemMatch': {
            '$elemMatch': {"teachers": {'$regex': teacher_name, '$options': 'i'}}}}},
    ]}

    cursor = conn[DATABASE_NAME][SCHEDULE_COLLECTION_NAME].find(request_data, {
                                                                '_id': 0})
    schedules = await cursor.to_list(None)

    result = []
    
    for schedule in schedules:
        schedule_with_num_keys = {
            '1': schedule['schedule']['monday'],
            '2': schedule['schedule']['tuesday'],
            '3': schedule['schedule']['wednesday'],
            '4': schedule['schedule']['thursday'],
            '5': schedule['schedule']['friday'],
            '6': schedule['schedule']['saturday'],
        }

        for i in range(1, 7):
            lessons_in_day = schedule_with_num_keys[str(i)]['lessons']
            for lesson_num in range(len(lessons_in_day)):
                for lesson in lessons_in_day[lesson_num]:
                    for teacher in lesson['teachers']:
                        if teacher.lower().find(teacher_name.lower()) != -1:
                            teacher_lesson = TeacherLessonModel(
                                weekday=i, lesson_number=lesson_num, lesson=LessonModel(**lesson))
                            result.append(teacher_lesson)
    
    teacher_schedule = TeacherSchedulesModelResponse(schedules=result)

    if len(result) > 0:
        return teacher_schedule
