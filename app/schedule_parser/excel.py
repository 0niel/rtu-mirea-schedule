import datetime
import json
import logging
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import groupby
from typing import Generator

import rtu_schedule_parser.utils.academic_calendar as academic_calendar
from motor.motor_asyncio import AsyncIOMotorClient
from rtu_schedule_parser import ExcelScheduleParser, LessonsSchedule
from rtu_schedule_parser.constants import Degree, Institute, ScheduleType
from rtu_schedule_parser.downloader import ScheduleDownloader
from rtu_schedule_parser.schedule import (ExamsSchedule, LessonEmpty,
                                          LessonsSchedule)

from ..crud.schedule import save_schedule
from ..models.schedule import (LessonModel, ScheduleByWeekdaysModel,
                               ScheduleLessonsModel)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _parse_document(doc) -> list[LessonsSchedule | ExamsSchedule]:
    logger.info(f"Обработка документа: {doc}")
    try:
        parser = ExcelScheduleParser(doc[0], doc[1], doc[2], doc[3])
        return parser.parse(force=True).get_schedule()
    except Exception:
        logger.error(f"Парсинг завершился с ошибкой ({doc})")


def _get_documents_by_json(docs_dir: str) -> list:
    # Формат json:
    # [
    #     {
    #         "file": "./расписание колледж.xlsx",
    #         "institute": "КПК",
    #         "type": 1,
    #         "degree": 4
    #     }
    # ]
    try:
        with open(os.path.join(docs_dir, "files.json"), "r") as f:
            files = json.load(f)

            documents = []

            for file in files:
                file_path = os.path.join(docs_dir, file["file"])
                logger.info(f"Файл {file['file']} добавлен на парсинг из `files.json`")

                if not os.path.exists(file_path):
                    logger.error(
                        f"Файл {file['file']} не найден. См. `files.json`. Пропускаем..."
                    )
                    continue

                documents.append(
                    (
                        file_path,
                        academic_calendar.get_period(datetime.datetime.now()),
                        Institute.get_by_short_name(file["institute"]),
                        Degree(file["degree"]),
                    )
                )

            return documents

    except FileNotFoundError:
        logger.info("`files.json` не найден. Пропускаем...")
        return []


def _get_documents() -> list:
    """Get documents for specified institute and degree"""
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(docs_dir, "docs")

    downloader = ScheduleDownloader(base_file_dir=docs_dir)

    if os.path.exists(docs_dir):
        for root, dirs, files in os.walk(docs_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
    else:
        os.mkdir(docs_dir)

    all_docs = downloader.get_documents(
        specific_schedule_types={ScheduleType.SEMESTER},
        specific_degrees={Degree.BACHELOR, Degree.MASTER, Degree.PHD},
        specific_institutes=set(Institute),
    )

    logger.info(f"Найдено {len(all_docs)} документов для парсинга")

    downloaded = downloader.download_all(all_docs)

    # сначала документы с Degree.PHD, потом Degree.MASTER, потом Degree.BACHELOR (то есть по убыванию)
    downloaded = sorted(downloaded, key=lambda x: x[0].degree, reverse=True)

    logger.info(f"Скачано {len(downloaded)} файлов")

    documents = [
        (doc[1], doc[0].period, doc[0].institute, doc[0].degree) for doc in downloaded
    ]
    
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(docs_dir, "..", "..", "docs")
    
    documents += _get_documents_by_json(docs_dir)

    return documents


def _parse() -> Generator[list[LessonsSchedule | ExamsSchedule], None, None]:
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = []
        for doc in _get_documents():
            task = executor.submit(_parse_document, doc)
            tasks.append(task)

        for future in as_completed(tasks):
            if (
                schedules := future.result()
            ):  # type: list[LessonsSchedule | ExamsSchedule]
                groups = {schedule.group for schedule in schedules}
                logger.info(f"Получено расписание документа. Группы: {groups}")
                yield schedules


async def parse_schedule(conn: AsyncIOMotorClient) -> None:
    """Parse parser and save it to database"""

    for schedules in _parse():
        for schedule in schedules:
            try:
                # В модели расписания 1-6 -- дни недели. По ключу 1 лежит расписание на понедельник,
                # 2 -- на вторник и т.д. "lessons" содержит список списков пар. Первый список относится к номеру пары,
                # второй список -- различные пары в это время
                lessons = schedule.lessons

                lessons_by_weekdays = defaultdict(list)

                for lesson in lessons:
                    weekday = lesson.weekday.value[0]

                    if type(lesson) is not LessonEmpty:
                        room = lesson.room
                        if room:
                            room = [
                                f"{room.name} ({room.campus.short_name})"
                                if room.campus is not None
                                else room.name
                            ]
                        else:
                            room = []

                        name = lesson.name

                        if lesson.subgroup:
                            name += f" ({lesson.subgroup} подгруппа)"

                        lesson = LessonModel(
                            name=name,
                            weeks=lesson.weeks,
                            time_start=lesson.time_start.strftime("%-H:%M"),
                            time_end=lesson.time_end.strftime("%-H:%M"),
                            types=lesson.type.value if lesson.type else "",
                            teachers=lesson.teachers,
                            rooms=room,
                        )

                    lessons_by_weekdays[str(weekday)].append(lesson)

                # Объединяем пары, которые проходят в одно и то же время и в один день недели
                for weekday, lessons in lessons_by_weekdays.items():
                    lessons_by_weekdays[weekday] = [
                        list(g) for k, g in groupby(lessons, lambda x: x.time_start)
                    ]

                # Удаляем пустые пары (LessonEmpty), конвертируем в ScheduleLessonsModel
                for weekday, lessons in lessons_by_weekdays.items():
                    lessons_by_weekdays[weekday] = ScheduleLessonsModel(
                        lessons=[
                            [
                                lesson
                                for lesson in lessons_by_weekday
                                if type(lesson) is not LessonEmpty
                            ]
                            for lessons_by_weekday in lessons
                        ]
                    )

                by_weekdays = ScheduleByWeekdaysModel(
                    monday=lessons_by_weekdays["1"],
                    tuesday=lessons_by_weekdays["2"],
                    wednesday=lessons_by_weekdays["3"],
                    thursday=lessons_by_weekdays["4"],
                    friday=lessons_by_weekdays["5"],
                    saturday=lessons_by_weekdays["6"],
                )

                await save_schedule(conn, schedule.group, by_weekdays)

            except Exception as e:
                logger.error(f"Error while parsing schedule: {e}")
