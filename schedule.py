from connect import connect_to_sqlite
import pprint
import datetime as dt
from datetime import datetime, date, time
import re

days_of_week = {
    1: 'Понедельник',
    2: 'Вторник',
    3: 'Среда',
    4: 'Четверг',
    5: 'Пятница',
    6: 'Суббота',
    7: 'Воскресенье'
}

rings = {
    1: '9:00-10:30',
    2: '10:40-12:10',
    3: '12:40-14:10',
    4: '14:20-15:50',
    5: '16:20-17:50',
    6: '18:00-19:30',
    7: '19:40-21:10'
}

time_zone = None

def cur_week(today):
    if today.month<8:
        first = date(today.year, 2, 9)
    else: 
        first = date(today.year, 9, 1)
    today_iso = today.isocalendar()
    first_iso = first.isocalendar()
    week = today_iso[1] - first_iso[1]
    
    if not (first_iso[2] == 7):
        week+=1
    return week

def format_lesson(record, day_of_week, week, today):
    formatted_str = '\n' + days_of_week[day_of_week] + " " + str(today.day) + "." + str(today.month)
    
    for lesson in record:
        typ = lesson[3].split()
        typ.append('')
        less = lesson[2] 
        if "кр." in less:
            exc = less.split("н.")[0]
            less = less.split("н.")[1].strip()
            regex_num = re.compile('\d+')  
            weeks = [int(item) for item in regex_num.findall(exc)] 
            print (exc, '  --  ', less, '  --  ',lesson, '  --  ', weeks)
            if "-" in exc:
                
                if not (weeks[0]<=week and week <= weeks[1]):
                    formatted_str+= "\n\n{0} пара ({4}, {1}) \n{2} {3}".format(lesson[0], rings[lesson[0]], less, typ[0], lesson[4])

            else:

                if not (week in weeks):
                    
                    formatted_str+= "\n\n{0} пара ({4}, {1}) \n{2} {3}".format(lesson[0], rings[lesson[0]], less, typ[0], lesson[4])

        elif "н." in less:
            exc = less.split("н.")[0]
            less = less.split("н.")[1].strip()
            regex_num = re.compile('\d+')  
            weeks = [int(item) for item in regex_num.findall(exc)]

            if "-" in exc:
                
                if (weeks[0]<=week and week <= weeks[1]):
                    formatted_str+= "\n\n{0} пара ({4}, {1}) \n{2} {3}".format(lesson[0], rings[lesson[0]], less, typ[0], lesson[4])

            else:
                if (week in weeks):
                    formatted_str+= "\n\n{0} пара ({4}, {1}) \n{2} {3}".format(lesson[0], rings[lesson[0]], less, typ[0], lesson[4])

        else:
            formatted_str+= "\n\n{0} пара ({4}, {1}) \n{2} {3}".format(lesson[0], rings[lesson[0]], less, typ[0], lesson[4])

        
    formatted_str += "\n" + "="*30
    return formatted_str


def return_one_day(today, group):
    week = cur_week(today)
    print(week)
    cursor = connect_to_sqlite()
    day_of_week = today.isocalendar()[2]
    if(day_of_week==7):
        return ""
    if (week%2):
        current_week = 1
    else:
        current_week = 2
    sqlite_select_Query = "SELECT schedule_calls.call_id, lessons.call_time, discipline_name, lesson_types.lesson_type_name, room_num, teacher_name  \
                        FROM lessons\
                        Join disciplines ON discipline_id = discipline\
                        Join schedule_calls ON call_id = call_num\
                        Join rooms On room_id = room\
                        JOIN teachers On teacher = teacher_id\
                        JOIN groups on group_id = group_num\
                        JOIN lesson_types on lesson_type_id = lesson_type\
                        WHERE groups.group_name = :group AND day = :day AND week = :week \
                        order by schedule_calls.call_id"
    cursor.execute(sqlite_select_Query, {'group':group, 'day':day_of_week, 'week':current_week})
    record = cursor.fetchall()
    print ('mew = ', record)
    cursor.close()
    if len(record):
        return format_lesson(record, day_of_week, week, today)
    return '\n' + days_of_week[day_of_week] + " " + str(today.day) + "." + str(today.month) + "\nНет пар\n" + "="*30


def today_sch(group):
    today = datetime.now(tz=time_zone)
    formatted_str = "="*30
    return formatted_str + return_one_day(today, group)
    
def tomorrow_sch(group): 
    today = datetime.now(tz=time_zone) + dt.timedelta(days=1)
    formatted_str = "="*30
    return formatted_str + return_one_day(today, group)

def week_sch(group): 
    today = datetime.now(tz=time_zone)
    day_of_week = today.isocalendar()[2]
    formatted_str = "="*30
    for i in range(6):
        today = datetime.now(tz=time_zone) + dt.timedelta(days=i-day_of_week+1)
        formatted_str += return_one_day(today, group)
    return formatted_str


