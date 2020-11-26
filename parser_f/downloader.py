from urllib import request
import requests
import traceback
import subprocess
import os
import os.path
import datetime
import re
from bs4 import BeautifulSoup
import ssl
import certifi


class Downloader:
    def __init__(self, path_to_error_log='errors/downloadErrorLog.csv', base_file_dir='xls/', except_types=[]):
        """
        Клаас загрузки расписания с сайта MIREA
        :type file_type: list
        """

        try:
            from bs4 import BeautifulSoup
        except ImportError:
            exit_code = self.install("beautifulsoup4")
            if exit_code == 0:
                from bs4 import BeautifulSoup
            else:
                print("При установке пакета возникла ошибка! {}".format(exit_code))
                exit(0)

        self.url = 'https://www.mirea.ru/schedule/'
        self.path_to_error_log = path_to_error_log
        self.base_file_dir = base_file_dir
        self.file_type = ['xls', 'xlsx']
        self.except_types = except_types
        self.download_dir = {
            "zach": [r'zach', r'zachety'],
            "exam": [r'zima', r'ekz', r'ekzam', r'ekzameny', r'sessiya'],
            "semester": [r'']
        }

    @staticmethod
    def install(package):
        """
        Устанавливает пакет
        :param package: название пакета (str)
        :return: код завершения процесса (int) или текст ошибки (str)
        """
        try:
            result = subprocess.check_call(['pip', 'install', package])
        except subprocess.CalledProcessError as result:
            return result

        return result

    @staticmethod
    def save_file(url, path):
        """
        :param url: Путь до web страницы
        :param path: Путь с именем для сохраняемого файла
        """

        def download(download_url, download_path):
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                if os.path.isfile(download_path):
                    os.remove(download_path)
                with open(download_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

        if os.path.isfile(path):
            old_file_size = os.path.getsize(path)
            new_file_size = len(requests.get(url).content)
            if old_file_size != new_file_size:
                download(url, path)
                return "download"
            else:
                return "skip"
        else:
            download(url, path)
            return "download"

    def get_dir(self, file_name):
        for dir_name in self.download_dir:
            for pattern in self.download_dir[dir_name]:
                if re.search(pattern, file_name, flags=re.IGNORECASE):
                    return dir_name

    def download(self):
        #urlopen(request, context=ssl.create_default_context(cafile=certifi.where()))
        response = request.urlopen(self.url, context=ssl.create_default_context(cafile=certifi.where()))  # Запрос страницы
        site = str(response.read().decode())  # Чтение страницы в переменную
        response.close()

        parse = BeautifulSoup(site, "html.parser")  # Объект BS с параметром парсера
        # xls_list = parse.findAll('a', {"class": "xls"})  # поиск в HTML Всех классов с разметой Html
        xls_list = parse.findAll('a', {"class": "uk-link-toggle"})  # поиск в HTML Всех классов с разметой Html

        # Списки адресов на файлы
        url_files = [x['href'].replace('https', 'http') for x in xls_list]  # Сохранение списка адресов сайтов
        progress_all = len(url_files)

        count_file = 0
        # Сохранение файлов
        for url_file in url_files:  # цикл по списку
            divided_path = os.path.split(url_file)
            # subdir = os.path.split(divided_path[0])[1]
            subdir = ''
            file_name = subdir + divided_path[1]
            try:
                if os.path.splitext(file_name)[1].replace('.', '') in self.file_type and "заоч" not in os.path.splitext(file_name)[0].replace('.', ''):
                    subdir = self.get_dir(file_name)
                    path_to_file = os.path.join(self.base_file_dir, subdir, file_name)
                    if subdir not in self.except_types:
                        if not os.path.isdir(os.path.join(self.base_file_dir, subdir)):
                            os.makedirs(os.path.join(self.base_file_dir, subdir), exist_ok=False)
                        result = self.save_file(url_file, path_to_file)
                        count_file += 1  # Счетчик для отображения скаченных файлов в %

                        print('{} : {} -- {}'.format(result, path_to_file, count_file / progress_all * 100))
                    else:
                        continue
                else:
                    count_file += 1  # Счетчик для отображения скаченных файлов в %

            except Exception as err:
                traceback.print_exc()
                with open(self.path_to_error_log, 'a+') as file:
                    file.write(
                        str(datetime.datetime.now()) + ': ' + url_file + ' message:' + str(err) + '\n', )
                pass


if __name__ == "__main__":
    Downloader = Downloader(path_to_error_log='logs/downloadErrorLog.csv', base_file_dir='xls/', except_types=[])
    Downloader.download()
