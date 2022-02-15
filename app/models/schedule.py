from pydantic import Field, BaseModel
from typing import List

class WeekResponse(BaseModel):
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
