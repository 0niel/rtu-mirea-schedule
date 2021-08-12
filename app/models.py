from pydantic import BaseModel, Field, BaseConfig
from typing import Any, List, Optional, Dict

BaseConfig.arbitrary_types_allowed = True

class GroupsListModel(BaseModel):
    count: int
    groups: List[str]


class LessonModel(BaseModel):
    name: str
    weeks: List[int]
    time_start: str
    time_end: str
    type: str
    teacher: str
    room: str


class ScheduleValueModel(BaseModel):
    lessons: List[List[LessonModel]]


class ScheduleModel(BaseModel):
    group: str
    field_1: ScheduleValueModel = Field(..., alias='1')
    field_2: ScheduleValueModel = Field(..., alias='2')
    field_3: ScheduleValueModel = Field(..., alias='3')
    field_4: ScheduleValueModel = Field(..., alias='4')
    field_5: ScheduleValueModel = Field(..., alias='5')
    field_6: ScheduleValueModel = Field(..., alias='6')
