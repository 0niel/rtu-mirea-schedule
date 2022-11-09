import logging
import sys
import os.path
from app.core.schedule_utils import ScheduleUtils

from app.crud.schedule import update_schedule_updates
from app.models.schedule import ScheduleUpdateModel


def setup_logger(path_to_error_log, logger_name):
    """Инициализация объекта для логирования информации

    Parameters
    ----------
    path_to_error_log: str, обязательный
        Путь и название файла, куда будут сохраняться логи. Пример: errors.log
    logger_name: str или None, обязательный
        Название логгера

    Вернёт logger с указанным именем (logger_name), если имя указано как None, то вернёт корневой логгер
    """
    logging_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] - %(message)s')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(path_to_error_log)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging_formatter)

    # логирование в консоль
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging_formatter)
    logger.addHandler(handler)
    logger.addHandler(file_handler)
    return logger


async def start_parsing():
    """Главная функция, реализующая выполнение парсинга данных с помощью
    интерфейса класса Parse
    """
    # во избежание рекурсивного включения
    # from .parser import ExcelParser, PDFParse
    from .excel_parser import ExcelParser
    from .college_parser import CollegeParser
    from .downloader import Downloader
    from .excel_formatter import ExcelFormatter
    from .college_formatter import CollegeFormatter
    from app.database.database import get_database

    downloader = Downloader(base_file_dir='documents/')
    files_path = downloader.run()

    # '_LATEST' означает, что парсинг этого файла проводить не нужно
    actual_file = '_LATEST'

    college_dir = 'documents/college'

    schedule_updates = []

    for file_path in files_path:
        if actual_file not in file_path:
            file_extension = os.path.splitext(file_path)[1]
            if file_extension != '.pdf':
                excel_parser = ExcelParser(await get_database(), file_path, 'semester', ExcelFormatter(),
                                           path_to_error_log='excel_parser.log')
                groups = excel_parser.parse()
                schedule_updates.append(ScheduleUpdateModel(groups=groups, updated_at=ScheduleUtils.now_date()))

            elif college_dir in file_path:
                college_parser = CollegeParser(await get_database(), file_path, CollegeFormatter())
                groups = college_parser.parse()
                schedule_updates.append(ScheduleUpdateModel(groups=groups, updated_at=ScheduleUtils.now_date()))

    await update_schedule_updates(await get_database(), schedule_updates)
