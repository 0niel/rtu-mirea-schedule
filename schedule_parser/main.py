from .reader import Reader
from .downloader import Downloader
from .writer import New_to_old_table
import sys
import os.path
import json


def parse_schedule():
    global Downloader
    try:
        try:
            subdir = "semester"
            base_file_dir = 'xls/'
            path_to_file = os.path.join(base_file_dir, subdir)
            os.listdir(path_to_file)
            print("\n")
            for the_file in os.listdir(path_to_file):
                file_path = os.path.join(path_to_file, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    #elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    print(e)
        except:
            print("???")
        Download = Downloader(path_to_error_log='logs/downloadErrorLog.csv', base_file_dir='xls/')
        Download.download()
        print("downloaded")
        try:
            reader = Reader(path_to_db="table.db")
        except:
            print("???")
        print("start reading")
        reader.run('xls', write_to_db=True, write_to_new_db=True, write_to_json_file=False, write_to_csv_file=False)
        print("\nКонвертация успешно выполнена!\n\n")

    except FileNotFoundError as err:
        print("Ошибка! Не найден файл шаблона 'template.xlsx' или файлы исходного расписания")

    except Exception as err:
        print(err, "!\n")
