from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.database.database import AsyncIOMotorClient, get_database
from app.models.schedule import GroupsListResponse, ScheduleModelResponse
from app.schedule_parser import start_parsing
from app.crud.schedule import get_full_schedule, get_groups
from app.core.config import SECRET_REFRESH_KEY


router = APIRouter()


@router.post(
    '/refresh',
    description='Refresh shedule',
    response_description='Return \'ok\' after updating'
)
async def refresh(secret_key: str):
    if SECRET_REFRESH_KEY is None or SECRET_REFRESH_KEY == '' \
       or SECRET_REFRESH_KEY == 'None':
        await start_parsing()
        return JSONResponse({"status": 'ok'})
    elif secret_key == SECRET_REFRESH_KEY:
        await start_parsing()
        return JSONResponse({"status": 'ok'})
    return JSONResponse({"status": 'Invalid secret API key'})


@router.get(
    '/schedule/{group}/full_schedule',
    response_description="Return full schedule of one group",
    response_model=ScheduleModelResponse
)
async def full_schedule(
    group: str = Path(..., min_length=10),
    db: AsyncIOMotorClient = Depends(get_database)
):
    schedule = await get_full_schedule(db, group)

    if not schedule:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Schedule for group '{group}' not found",
        )

    return schedule


@router.get(
    '/schedule/groups',
    response_description="List of all groups",
    response_model=GroupsListResponse
)
async def groups_list(db: AsyncIOMotorClient = Depends(get_database)):
    groups = await get_groups(db)

    if not groups:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Groups not found",
        )

    groups_response = GroupsListResponse(
        groups=groups, count=len(groups))

    return groups_response