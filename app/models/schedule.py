import datetime
from tokenize import group
from pydantic import Field, BaseModel
from typing import List


class WeekModelResponse(BaseModel):
    week: int


class GroupsListResponse(BaseModel):
    count: int
    groups: List[str]


class LessonModel(BaseModel):
    name: str
    weeks: List[int]
    time_start: str
    time_end: str
    types: str
    teachers: List[str]
    rooms: List[str]


class ScheduleValueModel(BaseModel):
    lessons: List[List[LessonModel]]


class ScheduleModel(BaseModel):
    monday: ScheduleValueModel = Field(..., alias='1', title='monday')
    tuesday: ScheduleValueModel = Field(..., alias='2', title='tuesday')
    wednesday: ScheduleValueModel = Field(..., alias='3', title='wednesday')
    thursday: ScheduleValueModel = Field(..., alias='4', title='thursday')
    friday: ScheduleValueModel = Field(..., alias='5', title='friday')
    saturday: ScheduleValueModel = Field(..., alias='6', title='saturday')


class ScheduleModelResponse(BaseModel):
    group: str
    schedule: ScheduleModel


class TeacherLessonModel(BaseModel):
    group: str
    weekday: int
    lesson_number: int
    lesson: LessonModel


class TeacherSchedulesModelResponse(BaseModel):
    schedules: List[TeacherLessonModel]


class ScheduleUpdateModel(BaseModel):
    groups: List[str]
    updated_at: datetime.datetime


class GroupStatsModel(BaseModel):
    groups: str
    received: int
