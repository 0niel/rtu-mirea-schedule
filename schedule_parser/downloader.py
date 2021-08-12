"""
Реализация класса Downloader, с помощью которого осуществляется 
скачивание файлов и парсинг ссылок со страницы по URL
"""
import requests
import os
import os.path
import re
import ssl
import certifi
import time
from urllib import request
from bs4 import BeautifulSoup
from schedule_parser import setup_logger


class Downloader:
    """Класс используется для скачивания документов расписания с 
    сайта РТУ МИРЭА
    
    Methods
    -------
    run(self)
        Главный метод, который реализует скачивание файлов с сайта
    download_file(self, url: str, file_path='', attempts=2)
        Загрузка файла по пути file_path с помощью прямого URL на него. 
        Скачивание происходит указанное количество попыток (attempts) 
        каждые 5 сек.
    """

    def __init__(self, path_to_error_log='errors/downloader.log',
                 base_file_dir='xls/', except_types=[]):
        """Конструктор класса Downloader

        Args:
        -------
            path_to_error_log (str, optional): путь и название файла
                для сохранения логов ошибок. 
                По умолчанию = 'errors/downloader.log'.
            base_file_dir (str, optional): директория, в которую будут
                сохраняться скаченные документы расписания. 
                По умолчанию = 'xls/'.
            except_types (list, optional): типы расписания, которые 
                будут исключены. По умолчанию = [].
        """
        self._url = 'https://www.mirea.ru/schedule/'
        self._path_to_error_log = path_to_error_log
        self._base_file_dir = base_file_dir
        self._file_types = ['xls', 'xlsx', 'pdf']
        self._except_types = except_types
        self._download_dir = {
            "zach": [r'zach', r'zachety'],
            "exam": [r'zima', r'ekz', r'ekzam', r'ekzameny', r'sessiya'],
            "semester": [r'']
        }
        self._logger = setup_logger(path_to_error_log, __name__)

    def __download_schedule(self, url: str, path: str):
        """Скачивание документа с расписанием (excel)

        Args:
        ----------
            url (str): Прямой URL до файла
            path (str): Путь с именем для сохраняемого файла

        Returns:
        ----------
            bool: True при успешном скачивании и False, если 
                скачивание пропущено
        """
        # проверка на актуальность файла, чтобы скачать именно нужный
        # todo: вынести в отдельный метод
        if "зима" in path or "лето" in path:
            return False

        if os.path.isfile(path):
            # сравнение двух файлов по их размеру
            # кажется, что это является ненадёжной штукой
            # todo: реализовать более надёжное сравнение файлов
            # (например, по времени изменения)
            old_file_size = os.path.getsize(path)
            new_file_size = len(requests.get(url).content)
            if old_file_size != new_file_size:
                try:
                    self.download_file(url, file_path=path)
                    return True
                except Exception as ex:
                    self._logger.error(f'Download failed with error: {ex}')
            else:
                return False

        try:
            self.download_file(url, file_path=path)
            return True
        except Exception as ex:
            self._logger.error(f'Download failed with error: {ex}')

    def __get_dir(self, file_name: str):
        """Возращает название папки, которая соответствует типу 
        документа расписания

        Args:
        ----------
            file_name (str): Название файла расписания

        Returns:
        ----------
            str: Название директории
        """
        for dir_name in self._download_dir:
            for pattern in self._download_dir[dir_name]:
                if re.search(pattern, file_name, flags=re.IGNORECASE):
                    return dir_name

    def __parse_links_by_title(self, block_title: str, parse):
        """Получить список всех ссылок на документы из блоков 
        расписания по заголовку. Например, если title == 'Расписание занятий:', 
        то вернёт список всех ссылок на все документы с расписанием на семестр, 
        проигнорируя расписание для сессии и др.

        Args:
            block_title (str): заголовок в блоке на сайте (https://www.mirea.ru/schedule/)
            parse (BeautifulSoup): объект BS для парсинга
        """
        documents_links = []
        
        # мы ищем все заголовки в блоках с расписанием, это может быть 
        # заголовок об экзаминационной сесии или т.п.
        schedule_titles = parse.find_all('b', class_='uk-h3')
        for title in schedule_titles:
            if title.text == block_title:
                # если это расписание занятий, то от носительно него 
                # получаем главный блок, в котором находятся ссылки на 
                # документы с расписанием
                all_divs = title.parent.parent.find_all('div', recursive=False)
                for i, div in enumerate(all_divs):
                    if block_title in div.text:
                        # проходимся по всем div'ам начиная от блока с расписанием, 
                        # заканчивая другим блоком с расписанием. Это нужно, т.к. 
                        # эти блоки не имеют вложенности и довольно сложно определить 
                        # где начинаются и кончаются документы с расписанием для семестра.
                        for j in range(i + 1, len(all_divs)):
                            # 'uk-h3' - класс заголовка расписания
                            if 'uk-h3' not in str(all_divs[j]) and all_divs[j].text != block_title:
                                 # поиск в HTML Всех классов с разметой Html
                                document = all_divs[j].find('a', {"class": "uk-link-toggle"})
                                if document is not None:
                                    if document['href'] not in documents_links:
                                        documents_links.append(document['href'])
                            else:
                                break
        return documents_links
    
    def download_file(self, url: str, file_path='', attempts=2):
        """Загружает содержимое URL-адреса в файл 
        (с поддержкой больших файлов путем потоковой передачи)

        Args:
        ----------
            url (str): Прямой URL до файла
            file_path (str, optional): Путь с именем для сохраняемого 
                файла. По умолчанию = ''.
            attempts (int, optional): Количество попыток скачивания 
                одного файла. По умолчанию = 2.
        """
        for attempt in range(1, attempts + 1):
            try:
                if attempt > 1:
                    # 5 секунд ожидания между попытками скачивания
                    time.sleep(5)
                with requests.get(url, stream=True) as response:
                    # вызываем исключение в случае, если status_code
                    # будет неудовлетворительными
                    # (не находится в диапазоне 200-29)
                    response.raise_for_status()
                    if os.path.isfile(file_path):
                        os.remove(file_path)

                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    return

            except Exception as ex:
                self._logger.error(
                    f'Download attempt #{attempt} ({url}) \
                    failed with error: {ex}'
                )

    def run(self):
        """
        Главный метод, реализующий парсинг ссылок на расписание и 
        скачивание документов в папку

        Note:
            URL, типы файлов для проверки, директории, строго заданы 
            в качестве защищённых полей класса
        """
        # Запрос страницы
        response = request.urlopen(
            self._url, context=ssl.create_default_context(
                cafile=certifi.where()
            )
        )
        # Чтение страницы в переменную
        html = str(response.read().decode())
        response.close()

        # Объект BS с параметром парсера
        parse = BeautifulSoup(html, "html.parser")

        # списки адресов на файлы
        url_files = self.__parse_links_by_title('Расписание занятий:', parse)
        print(url_files)
        # TODO: скачивание сессионных файлов

        # количество файлов на скачивание (всего)
        progress_all = len(url_files)
        
        # количество скачанных файлов
        count_file = 0

        # Сохранение файлов
        for url_file in url_files:
            # получаем название файла из URL
            divided_path = os.path.split(url_file)
            file_name = divided_path[1]
            try:
                # название файла и его расширение
                (file_root, file_ext) = os.path.splitext(file_name)
                if file_ext.replace('.', '') in self._file_types and "заоч" not in file_root:
                    subdir = self.__get_dir(file_name)
                    path_to_file = os.path.join(
                        self._base_file_dir, subdir, file_name)
                    if subdir not in self._except_types:
                        os.makedirs(os.path.join(
                            self._base_file_dir, subdir), exist_ok=True)
                        result = self.__download_schedule(
                            url_file, path_to_file)

                        count_file += 1
                        progress_percentage = count_file / progress_all * 100

                        if result:
                            self._logger.info(
                                'Download : {0} -- {1}'.format(
                                    path_to_file,
                                    progress_percentage))
                        else:
                            self._logger.info(
                                'Skp : {0} -- {1}'.format(
                                    path_to_file,
                                    progress_percentage))
                    else:
                        continue
                else:
                    count_file += 1

            except Exception as ex:
                self._logger.error(f'[{url_file}] message:' + str(ex))
