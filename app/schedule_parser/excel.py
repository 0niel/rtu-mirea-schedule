import datetime
import json
import logging
import os
from collections import defaultdict
from itertools import groupby
from typing import Generator

import rtu_schedule_parser.utils.academic_calendar as academic_calendar
from motor.motor_asyncio import AsyncIOMotorClient
from rtu_schedule_parser import ExcelScheduleParser, LessonsSchedule
from rtu_schedule_parser.constants import Degree, Institute, ScheduleType
from rtu_schedule_parser.downloader import ScheduleDownloader
from rtu_schedule_parser.schedule import LessonEmpty, LessonsSchedule

from ..crud.schedule import save_schedule
from ..models.schedule import (LessonModel, ScheduleByWeekdaysModel,
                               ScheduleLessonsModel)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_by_json(docs_dir: str) -> Generator[list[LessonsSchedule], None, None]:
    try:
        with open(os.path.join(docs_dir, "files.json"), "r") as f:
            files = json.load(f)

            for file in files:
                file_path = os.path.join(docs_dir, file["file"])
                logger.info(f"Parsing {file['file']} from `files.json`")

                if not os.path.exists(file_path):
                    logger.error(
                        f"File {file['file']} not found. See `files.json` for more info. Skipping..."
                    )
                    continue

                try:
                    now_date = datetime.datetime.now()
                    parser = ExcelScheduleParser(
                        file_path,
                        academic_calendar.get_period(now_date),
                        Institute.get_by_short_name(file["institute"]),
                        Degree(file["degree"]),
                    )

                    yield parser.parse(force=True).get_schedule()
                except Exception as e:
                    logger.error(f"Error while parsing {file['file']}: {e}")
                    continue

    except FileNotFoundError:
        logger.error("File `files.json` not found. Skipping...")
        return


def parse() -> Generator[list[LessonsSchedule], None, None]:
    """Parse parser from excel file"""
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(docs_dir, "docs")

    # Initialize downloader with default directory to save files
    downloader = ScheduleDownloader(base_file_dir=docs_dir)

    if os.path.exists(docs_dir):
        # Delete all files and dirs in folder
        for root, dirs, files in os.walk(docs_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
    else:
        os.mkdir(docs_dir)

    # Get documents for specified institute and degree
    all_docs = downloader.get_documents(
        specific_schedule_types={ScheduleType.SEMESTER},
        specific_degrees={Degree.BACHELOR, Degree.MASTER, Degree.PHD},
        specific_institutes={
            institute for institute in Institute if institute != Institute.COLLEGE
        },
    )

    logger.info(f"Found {len(all_docs)} documents to parse")

    # Download only if they are not downloaded yet.
    downloaded = downloader.download_all(all_docs)

    # сначала документы с Degree.PHD, потом Degree.MASTER, потом Degree.BACHELOR (то есть по убыванию)
    downloaded = sorted(downloaded, key=lambda x: x[0].degree, reverse=True)

    logger.info(f"Downloaded {len(downloaded)} files")

    for doc in downloaded:
        print(f"Processing document: {doc}")

        parser = ExcelScheduleParser(
            doc[1], doc[0].period, doc[0].institute, doc[0].degree
        )

        yield parser.parse(force=True).get_schedule()

    docs_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(docs_dir, "..", "..", "docs")

    yield from parse_by_json(docs_dir)


def parse_schedule(conn: AsyncIOMotorClient) -> None:
    """Parse parser and save it to database"""

    for schedules in parse():
        for schedule in schedules:
            try:
                # В модели расписания 1-6 -- дни недели. По ключу 1 лежит расписание на понедельник, 2 -- на вторник и т.д.
                # "lessons" содержит список списков пар. Первый список относится к номеру пары, второй список -- различные пары в это время

                lessons = schedule.lessons

                lessons_by_weekdays = defaultdict(list)

                for lesson in lessons:
                    weekday = lesson.weekday

                    if type(lesson) is not LessonEmpty:
                        room = lesson.room
                        rooms = [
                            f"{room.name} ({room.campus.short_name})"
                            if room.campus is not None
                            else room.name
                        ]

                        name = lesson.name

                        if lesson.subgroup:
                            name += f" ({lesson.subgroup} подгруппа)"

                        lesson = LessonModel(
                            name=name,
                            weeks=lesson.weeks,
                            time_start=lesson.time_start.strftime("%H:%M"),
                            time_end=lesson.time_end.strftime("%H:%M"),
                            types=lesson.type.value if lesson.type else "",
                            teachers=lesson.teachers,
                            rooms=rooms,
                        )

                    lessons_by_weekdays[str(weekday)].append(lesson)

                # Объединяем пары, которые проходят в одно и то же время и в один день недели в один список
                for weekday, lessons in lessons_by_weekdays.items():
                    lessons_by_weekdays[weekday] = [
                        list(g) for k, g in groupby(lessons, lambda x: x.time_start)
                    ]

                by_weekdays = ScheduleByWeekdaysModel(
                    monday=ScheduleLessonsModel(lessons=lessons_by_weekdays["1"]),
                    tuesday=ScheduleLessonsModel(lessons=lessons_by_weekdays["2"]),
                    wednesday=ScheduleLessonsModel(lessons=lessons_by_weekdays["3"]),
                    thursday=ScheduleLessonsModel(lessons=lessons_by_weekdays["4"]),
                    friday=ScheduleLessonsModel(lessons=lessons_by_weekdays["5"]),
                    saturday=ScheduleLessonsModel(lessons=lessons_by_weekdays["6"]),
                )

                save_schedule(conn, schedule.group, by_weekdays)

            except Exception as e:
                logger.error(f"Error while parsing schedule: {e}")
