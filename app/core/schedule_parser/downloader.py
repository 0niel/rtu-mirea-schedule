"""
Реализация класса Downloader, с помощью которого осуществляется
скачивание файлов и парсинг ссылок со страницы по URL
"""
from . import setup_logger
from rtu_schedule_parser.downloader import ScheduleDownloader


class Downloader:
    """Класс для скачивания файлов расписания с сайта РТУ МИРЭА"""

    def __init__(self, base_file_dir='xls/'):
        self._base_file_dir = base_file_dir
        self._download_dir = {
            "zach": [r'zach', r'zachety'],
            "exam": [r'zima', r'ekz', r'ekzam', r'ekzameny', r'sessiya'],
            "semester": [r'']
        }
        self._logger = setup_logger('downloader.log', __name__)

    def run(self) -> list[str]:
        # Initialize downloader with default directory to save files
        downloader = ScheduleDownloader()
        # Get documents for specified institute and degree
        all_docs = downloader.get_documents()

        # Download only if they are not downloaded yet.
        downloaded = downloader.download_all(all_docs)

        self._logger.info(f"Downloaded {len(downloaded)} files")

        files_path = [doc[1] for doc in downloaded]

        self._logger.info(f"Downloaded files: {files_path}")

        return files_path
