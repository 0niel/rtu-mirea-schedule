from typing import List

from app.models.schedule import ScheduleModelResponse, ScheduleModel
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
