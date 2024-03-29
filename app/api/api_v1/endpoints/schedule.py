from typing import List

from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.core.config import SECRET_REFRESH_KEY
from app.core.schedule_utils import ScheduleUtils
from app.crud.schedule import (find_room, find_teacher, get_full_schedule,
                               get_groups, get_groups_stats,
                               update_group_stats)
from app.database.database import AsyncIOMotorClient, get_database
from app.models.schedule import (GroupsListResponse, GroupStatsModel,
                                 RoomScheduleModel, ScheduleModel,
                                 TeacherSchedulesModelResponse,
                                 WeekModelResponse)
from app.schedule_parser.excel import parse_schedule

router = APIRouter()


@router.post(
    "/refresh",
    description="Refresh shedule",
    response_description="Return 'ok' after updating",
)
async def refresh(
    secret_key: str = None, db: AsyncIOMotorClient = Depends(get_database)
):
    if (
        SECRET_REFRESH_KEY is None
        or SECRET_REFRESH_KEY == ""
        or SECRET_REFRESH_KEY == "None"
    ):
        await parse_schedule(db)
        return JSONResponse({"status": "ok"})
    elif secret_key == SECRET_REFRESH_KEY:
        await parse_schedule(db)
        return JSONResponse({"status": "ok"})
    return JSONResponse({"status": "Invalid secret API key"})


@router.get(
    "/schedule/{group}/full_schedule",
    response_description="Return full schedule of one group",
    response_model=ScheduleModel,
)
async def full_schedule(
    group: str = Path(..., min_length=10),
    db: AsyncIOMotorClient = Depends(get_database),
):
    schedule = await get_full_schedule(db, group)

    if not schedule:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Schedule for group '{group}' not found",
        )

    await update_group_stats(db, group)

    return schedule


@router.get(
    "/schedule/groups",
    response_description="List of all groups",
    response_model=GroupsListResponse,
)
async def groups_list(db: AsyncIOMotorClient = Depends(get_database)):
    groups = await get_groups(db)

    if not groups:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Groups not found",
        )

    if len(groups) == 0:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Groups are empty. Maybe schedule is not parsed yet",
        )

    return GroupsListResponse(groups=groups, count=len(groups))


@router.get(
    "/schedule/current_week",
    response_description="Get current week",
    response_model=WeekModelResponse,
)
async def current_week():
    return WeekModelResponse(week=ScheduleUtils.get_week(ScheduleUtils.now_date()))


@router.get(
    "/schedule/teacher/{teacher_name}",
    response_description="Find teacher schedule by teacher name",
    response_model=TeacherSchedulesModelResponse,
)
async def teacher_schedule(
    teacher_name: str = Path(...), db: AsyncIOMotorClient = Depends(get_database)
):
    schedule = await find_teacher(db, teacher_name)

    if not schedule:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Teacher with name {teacher_name} not found",
        )

    return schedule


@router.get(
    "/schedule/room/{room_name}",
    response_description="Find room schedule by room name",
    response_model=RoomScheduleModel,
)
async def room_schedule(
    room_name: str = Path(...), db: AsyncIOMotorClient = Depends(get_database)
):
    schedule = await find_room(db, room_name)

    if not schedule:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Room with name {room_name} not found",
        )

    return schedule


@router.get(
    "/schedule/groups_stats/",
    response_description="Get statistics of requests to group schedules",
    response_model=List[GroupStatsModel],
)
async def groups_stats(db: AsyncIOMotorClient = Depends(get_database)):
    stats = await get_groups_stats(db)

    if not stats:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Stats not found")

    return stats
