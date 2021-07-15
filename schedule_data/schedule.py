import datetime as dt
from schedule_data.database import semester_collection
from datetime import date


class Schedule:
    def __init__(self) -> None:
        pass

    lessons_times = {
        1: {"start": '9:00', "end": '10:30'},
        2: {"start": '10:40', "end": '12:10'},
        3: {"start": '12:40', "end": '14:10'},
        4: {"start": '14:20', "end": '15:50'},
        5: {"start": '16:20', "end": '17:50'},
        6: {"start": '18:00', "end": '19:30'},
        7: {"start": '19:40', "end": '21:10'},
    }

    @staticmethod
    def save(group, schedule):
        """Сохранение или обновление расписания группы.

        Args:
            group (str): название группы
            schedule (dict): словарь расписания для каждого дня недели
        """
        semester_collection.update_one(
            {'group': group},
            {'$set': {'group': group,
                      'schedule':  schedule}},
            upsert=True
        )

    @staticmethod
    def get_current_week(today):
        if today.month < 8:
            first = date(today.year, 2, 9)
        else:
            first = date(today.year, 9, 1)
        today_iso = today.isocalendar()
        first_iso = first.isocalendar()
        week = today_iso[1] - first_iso[1]

        if not (first_iso[2] == 7):
            week += 1
        return week

    @staticmethod
    def get_full_schedule(group_name):
        schedule = semester_collection.find_one(
            {'group': group_name}, {'_id': 0})
        return schedule

    @staticmethod
    def get_groups_list():
        groups = list(semester_collection.find({}, {'group': 1, '_id': 0}))
        return [group['group'] for group in groups]
