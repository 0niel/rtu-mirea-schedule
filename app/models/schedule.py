import datetime
from typing import List

from pydantic import BaseModel, Field


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


class ScheduleLessonsModel(BaseModel):
    lessons: List[List[LessonModel]]


class ScheduleByWeekdaysModelResponse(BaseModel):
    monday: ScheduleLessonsModel = Field(..., alias="1", title="monday")
    tuesday: ScheduleLessonsModel = Field(..., alias="2", title="tuesday")
    wednesday: ScheduleLessonsModel = Field(..., alias="3", title="wednesday")
    thursday: ScheduleLessonsModel = Field(..., alias="4", title="thursday")
    friday: ScheduleLessonsModel = Field(..., alias="5", title="friday")
    saturday: ScheduleLessonsModel = Field(..., alias="6", title="saturday")


class ScheduleByWeekdaysModel(BaseModel):
    monday: ScheduleLessonsModel
    tuesday: ScheduleLessonsModel
    wednesday: ScheduleLessonsModel
    thursday: ScheduleLessonsModel
    friday: ScheduleLessonsModel
    saturday: ScheduleLessonsModel


class ScheduleModel(BaseModel):
    group: str
    schedule: ScheduleByWeekdaysModelResponse


class TeacherLessonModel(BaseModel):
    group: str
    weekday: int
    lesson_number: int
    lesson: LessonModel


class RoomLessonModel(BaseModel):
    room: str
    weekday: int
    lesson: LessonModel


class RoomScheduleModel(BaseModel):
    schedules: List[RoomLessonModel]


class TeacherSchedulesModelResponse(BaseModel):
    schedules: List[TeacherLessonModel]


class ScheduleUpdateModel(BaseModel):
    groups: List[str]
    updated_at: datetime.datetime


class GroupStatsModel(BaseModel):
    group: str
    received: int
