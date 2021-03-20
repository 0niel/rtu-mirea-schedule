from connect import connect_to_sqlite
import pprint
import datetime as dt
from datetime import datetime, date, time
import re
from schedule_parser.main import parse_schedule


offset = dt.timedelta(hours=3)


rings = {
    1: {"start": '9:00', "end": '10:30'},
    2: {"start": '10:40', "end": '12:10'},
    3: {"start": '12:40', "end": '14:10'},
    4: {"start": '14:20', "end": '15:50'},
    5: {"start": '16:20', "end": '17:50'},
    6: {"start": '18:00', "end": '19:30'},
    7: {"start": '19:40', "end": '21:10'},
}

time_zone = dt.timezone(offset, name='МСК')

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
    day = [{
        "time" : {"start": '9:00', "end": '10:30'},
        "lesson": None
    }, {
        "time" : {"start": '10:40', "end": '12:10'},
        "lesson": None
    }, {
        "time" : {"start": '12:40', "end": '14:10'},
        "lesson": None
    }, {
        "time" :{"start": '14:20', "end": '15:50'} ,
        "lesson": None
    }, {
        "time" : {"start": '16:20', "end": '17:50'},
        "lesson": None
    }, {
        "time" : {"start": '18:00', "end": '19:30'},
        "lesson": None
    }, { 
        "time" : {"start": '19:40', "end": '21:10'},
        "lesson": None
    }]
    for lesson in record:
        res_lesson = {}
        typ = lesson[3].split()
        typ.append('')
        less = lesson[2] 
        if "кр." in less:
            exc = less.split("н.")[0]
            less = less.split("н.")[1].strip()
            regex_num = re.compile(r'\d+')
            weeks = [int(item) for item in regex_num.findall(exc)] 
            if "-" in exc:
                
                if not (weeks[0]<=week and week <= weeks[1]):
                    res_lesson["classRoom"] = lesson[4]
                    res_lesson["teacher"] = lesson[5]
                    res_lesson["name"] = less
                    res_lesson["type"] = typ[0]
                    day[lesson[0]-1]["lesson"] = res_lesson

            else:

                if not (week in weeks):
                    res_lesson["classRoom"] = lesson[4]
                    res_lesson["teacher"] = lesson[5]
                    res_lesson["name"] = less
                    res_lesson["type"] = typ[0]
                    day[lesson[0]-1]["lesson"] = res_lesson

        elif "н." in less or " н " in less:
            if "н." in less:
                exc = less.split("н.")[0]
                less = less.split("н.")[1].strip()
            elif " н " in less:
                exc = less.split(" н ")[0]
                less = less.split(" н ")[1].strip()
            regex_num = re.compile(r'\d+')  
            weeks = [int(item) for item in regex_num.findall(exc)]

            if "-" in exc:
                
                if (weeks[0]<=week and week <= weeks[1]):
                    res_lesson["classRoom"] = lesson[4]
                    res_lesson["teacher"] = lesson[5]
                    res_lesson["name"] = less
                    res_lesson["type"] = typ[0]
                    day[lesson[0]-1]["lesson"] = res_lesson

            else:
                if (week in weeks):
                    res_lesson["classRoom"] = lesson[4]
                    res_lesson["teacher"] = lesson[5]
                    res_lesson["name"] = less
                    res_lesson["type"] = typ[0]
                    day[lesson[0]-1]["lesson"] = res_lesson

        else:
            res_lesson["classRoom"] = lesson[4]
            res_lesson["teacher"] = lesson[5]
            res_lesson["name"] = less
            res_lesson["type"] = typ[0]
            day[lesson[0]-1]["lesson"] = res_lesson

    return day


def return_one_day(today, group):
    week = cur_week(today)
    try:
        cursor = connect_to_sqlite()
        day_of_week = today.isocalendar()[2]
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
        cursor.close()
        return format_lesson(record, day_of_week, week, today)
    except:
        print("No database")
        return None
    
def for_cache(): 
    try:
        cursor = connect_to_sqlite()
        sqlite_select_Query = "SELECT group_name FROM groups where group_name like 'И%';"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        cursor.close()
        res = {}

        for group in record:
            group = group[0]
            print(group)
            res[group] = full_sched(group)
        
        return res
    except:
        print("No database")
        return None


def get_groups():
    try:
        res = {"bachelor": {"first":{}, "second":{}, "third":{}, "fouth":{}},
                "master": {"first":{}, "second":{}}
        }
        cursor = connect_to_sqlite()
        sqlite_select_Query = "SELECT group_name FROM groups where group_name like 'И%';"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        cursor.close()
        m = []
        b = []
        a = []
        m_courses = {}
        b_courses = {}
        max_year = 0
        for group in record:
            group = group[0]
            print(group)
            max_year = max(max_year, int(group[-2]+group[-1]))
        

        for group in record:
            group = group[0]
            if group[2] == "М":
                course = max_year - int(group[-2]+group[-1]) + 1
                if group[:4] in res["master"][course]:
                        res["master"][course][group[:4]].append(int(group[5:7]))  
                else:
                    res["master"][course][group[:4]] = [int(group[5:7])] 
            elif group[2] == "Б":
                course = max_year - int(group[-2]+group[-1]) + 1
                if group[:4] in res["bachelor"][course]:
                        res["bachelor"][course][group[:4]].append(int(group[5:7]))  
                else:
                    res["bachelor"][course][group[:4]] = [int(group[5:7])] 
            else:
                a.append(group)
        print(res)
        return res
    except:
        print("No database")
        return None

def today_sch(group):
    today = datetime.now(tz=time_zone)
    return return_one_day(today, group)
    
def tomorrow_sch(group): 
    today = datetime.now(tz=time_zone) + dt.timedelta(days=1)
    return return_one_day(today, group)

def week_sch(group): 
    today = datetime.now(tz=time_zone)
    day_of_week = today.isocalendar()[2]
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    res = {}
    for i in range(6):
        today = datetime.now(tz=time_zone) + dt.timedelta(days=i-day_of_week+1)
        day = return_one_day(today, group)
        if day:
            res[days[i]] = day
        else:
            return None
    return res

def next_week_sch(group):
    today = datetime.now(tz=time_zone) + dt.timedelta(days=7)
    day_of_week = today.isocalendar()[2]
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    res = {}
    for i in range(6):
        today = datetime.now(tz=time_zone) + dt.timedelta(days=i-day_of_week+1) + dt.timedelta(days=7)
        day = return_one_day(today, group)
        if day:
            res[days[i]] = day
        else:
            return None
    return res

def full_sched(group):
    today = datetime.now(tz=time_zone) + dt.timedelta(days=7)
    day_of_week = today.isocalendar()[2]
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    res = {}
    res2 = {}

    for i in range(6):
        today = datetime.now(tz=time_zone) + dt.timedelta(days=i-day_of_week+1)
        day = return_one_day(today, group)
        if day:
            res[days[i]] = day
        else:
            return None
    for i in range(6):
        today = datetime.now(tz=time_zone) + dt.timedelta(days=i-day_of_week+1) + dt.timedelta(days=7)
        day = return_one_day(today, group)
        if day:
            res2[days[i]] = day
        else:
            return None     
    if cur_week(today) == 1: 
        return {"first": res, "second": res2}
    
    return {"first": res2, "second": res}