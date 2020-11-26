from reader import Reader
from downloader import Downloader
from writer import New_to_old_table
import sys
import os.path
import json

def parse_schedule():
    global Downloader
    try:
        # Downloader = Downloader(path_to_error_log='logs/downloadErrorLog.csv', base_file_dir='xls/')
        # Downloader.download()

        reader = Reader(path_to_db="table.db")
        reader.run('xls', write_to_db=True, write_to_new_db=True, write_to_json_file=False, write_to_csv_file=False)
        print("\nКонвертация успешно выполнена!\n\n")

    except FileNotFoundError as err:
        print("Ошибка! Не найден файл шаблона 'template.xlsx' или файлы исходного расписания")

    except Exception as err:
        print(err, "\n")
