from app.models import GroupsListModel, ScheduleModel
from schedule_parser import start_parsing
from app import app
from schedule_data.schedule import Schedule
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
import sys

sys.path.append('..')


@app.post('/refresh', description='Refresh shedule', response_description='Return \'ok\' after updating',)
async def refresh():
    start_parsing()
    return JSONResponse({"status": 'ok'})


@app.get('/api/schedule/{group}/full_schedule', response_description="Return full schedule of one group", response_model=ScheduleModel)
async def full_schedule(group: str):
    schedule_db = Schedule()
    full_schedule = await schedule_db.get_full_schedule(group)
    if full_schedule:
        return JSONResponse(full_schedule)

    raise HTTPException(headers={'Retry-After': 200},
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@app.get('/api/schedule/groups', response_description="List of all groups", response_model=GroupsListModel)
async def groups_list():
    schedule_db = Schedule()
    groups_list = await schedule_db.get_groups_list()
    if groups_list:
        return JSONResponse({'groups': groups_list, 'count': len(groups_list)})

    raise HTTPException(headers={'Retry-After': 200},
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
