from schedule_parser import start_parsing
from app import app
from flask import Flask, flash, request, make_response, Response
from schedule import get_full_schedule
import sys

sys.path.append('..')


@app.route('/refresh', methods=["POST"])
def refresh():
    """Refresh shedule
    ---

    responses:
      200:
        description: Return \'ok\' after updating
        schema:
          type: object
          properties:
            status:
              type: string
    """
    start_parsing()
    return make_response({"status": 'ok'})


@app.route('/api/schedule/<string:group>/full_schedule', methods=["GET"])
def full_schedule(group):
    """Current week's schedule for requested group
    ---
    parameters:
      - name: group
        in: path
        type: string
        required: true
      
    responses:
      200:
        description: Return full schedule of one group. 
        schema:
          $ref: '#/definitions/FullSchedule'
            
      503:
          description: Retry-After:100
    """
    full_schedule = get_full_schedule(group)
    if full_schedule:
        return make_response(full_schedule)
    
    res = Response(headers={'Retry-After': 200}, status=503)
    return res
