from app import app
from flask import Flask, flash, request, redirect, url_for, session, jsonify, render_template, make_response, Response
import requests
from os import environ  
import datetime
from schedule import today_sch, tomorrow_sch, week_sch, next_week_sch, get_groups, full_sched, for_cache
import sys

sys.path.append('..')
from schedule_parser.main import parse_schedule

@app.route('/api/schedule/<string:group>/today', methods=["GET"])
def today(group):
    """Today's schedule for requested group
    ---
    parameters:
      - name: group
        in: path
        type: string
        required: true
      
    definitions:
      Lesson:
        type: object
        nullable: true
        properties:
          lesson:
            type: object
            properties:
              classRoom: 
                type: string
              name: 
                type: string
              teacher: 
                type: string
              type: 
                type: string
            
          time:
            type: object
            properties:
              start: 
                type: string
              end: 
                type: string
      Week: 
        type: object
        properties:
          monday:
            type: array
            items:
              $ref: '#/definitions/Lesson'
          tuesday:
            type: array
            items:
              $ref: '#/definitions/Lesson'
          wednesday: 
            type: array
            items:
              $ref: '#/definitions/Lesson'
          thursday:
            type: array
            items:
              $ref: '#/definitions/Lesson'
          friday: 
            type: array
            items:
              $ref: '#/definitions/Lesson'
          saturday:
            type: array
            items:
              $ref: '#/definitions/Lesson'
      FullShedule:
        type: object
        nullable: true
        properties:
          first:
            type: object
            properties:
              week:
                $ref: '#/definitions/Week'
          second:
            type: object
            properties:
              week:
                $ref: '#/definitions/Week'
      
      Number: 
        type: object
        properties:
          number:
            type: integer
          group:
            type: string


      Direction:
        type: object
        properties:
          name: 
            type: string
          numbers:
            type: array
            items:
              $ref: '#/definitions/Number'
                      
      LiteDirection:
        type: object
        properties:
          name: 
            type: string
          numbers:
            type: array
            items:
              type: string

      Groups:
        type: object
        properties:
          bachelor:
            type: object
            properties:
              first:
                type: array
                items:
                  $ref: '#/definitions/LiteDirection'
              second:
                type: array
                items:
                  $ref: '#/definitions/LiteDirection'
              third:
                type: array
                items:
                  $ref: '#/definitions/LiteDirection'
              fourth:
                type: array
                items:
                  $ref: '#/definitions/LiteDirection'
          master:
            type: object
            properties:
              first:
                type: array
                items:
                  $ref: '#/definitions/Direction'
              second:
                type: array
                items:
                  $ref: '#/definitions/Direction'                    


    responses:
      200:
        description: Return today\'s schedule. There are 8 lessons on a day. "lesson":null, if there is no pair 
        schema:
          type: array
          items:
            $ref: '#/definitions/Lesson'
          minItems: 8
          maxItems: 8
            
      503:
          description: Retry-After:100
    """

    sch = today_sch(group)
    if sch:
      response = jsonify(sch)
      # return "today for{} is {}".format(group, res)
      return make_response(response)
    res = Response(headers={'Retry-After':200}, status=503)
    return res 

@app.route('/api/schedule/<string:group>/tomorrow', methods=["GET"])
def tomorrow(group):
    """Today's schedule for requested group
    ---
    parameters:
      - name: group
        in: path
        type: string
        required: true

    responses:
      200:
        description: Return tomorrow\'s schedule. There are 8 lessons on a day. "lesson":null, if there is no pair 
        schema:
          type: array
          items:
            $ref: '#/definitions/Lesson'
          minItems: 8
          maxItems: 8
            
      503:
          description: Retry-After:100
    """
    res = tomorrow_sch(group)
    if res:
      response = jsonify(res)
      # return "tomorrow for{} is {}".format(group, res)
      return make_response(response)
    res = Response(headers={'Retry-After':200}, status=503)
    return res 
    
@app.route('/api/schedule/<string:group>/week', methods=["GET"])
def week(group):
    """Current week's schedule for requested group
    ---
    parameters:
      - name: group
        in: path
        type: string
        required: true
      
    responses:
      200:
        description: Return week\'s schedule. There are 8 lessons on a day. "lesson":null, if there is no pair.
        schema:
          $ref: '#/definitions/Week'
            
      503:
          description: Retry-After:100
    """
    res =  week_sch(group)
    if res:
      response = jsonify(res)
      # return "tomorrow for{} is {}".format(group, res)
      return make_response(response)
    res = Response(headers={'Retry-After':200}, status=503)
    return res

@app.route('/api/schedule/get_groups', methods=["GET"])
def groups():
  """Next week's schedule for requested group
    ---
      
    responses:
      200:
        description: Return all groups in IIT.
        schema:
          $ref: '#/definitions/Groups'

            
      503:
          description: Retry-After:100
  """
  res =  get_groups()
  if res:
    response = jsonify(res)
    # return "tomorrow for{} is {}".format(group, res)
    return make_response(response)
  res = Response(headers={'Retry-After':200}, status=503)
  return res

@app.route('/api/schedule/<string:group>/next_week', methods=["GET"])
def next_week(group):
    """Next week's schedule for requested group
    ---
    parameters:
      - name: group
        in: path
        type: string
        required: true
      
    responses:
      200:
        description: Return week\'s schedule. There are 8 lessons on a day. "lesson":null, if there is no pair.
        schema:
          $ref: '#/definitions/Week'
            
      503:
          description: Retry-After:100
    """
    res =  next_week_sch(group)
    if res:
      response = jsonify(res)
      # return "tomorrow for{} is {}".format(group, res)
      return make_response(response)
    res = Response(headers={'Retry-After':200}, status=503)
    return res 

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
    parse_schedule()
    return make_response({"status": 'ok'})

@app.route('/api/schedule/secret_refresh', methods=["POST"])
def secret_refresh():
    """Refresh shedule
    ---

    parameters:
        - in: header
          name: X-Auth-Token
          type: string
          required: true

    responses:
      200:
        description: Return \'ok\' after updating
        schema:
          type: object
          properties:
            status:
              type: string
    """
    try:
      secret = request.headers.get('X-Auth-Token')
      SECRET_FOR_REFRESH = environ.get('SECRET_FOR_REFRESH')
      if secret == SECRET_FOR_REFRESH:
        parse_schedule()
        return make_response({"status": 'ok'})
      return make_response({"status": 'wrong_password'}, 401)
    except:
      return make_response({"status": 'need_password'})
  
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
        description: Return full schedule of one group. There are 8 lessons on a day. "lesson":null, if there is no pair.
        schema:
          type: object
          properties:
            1:
              type: object
              properties:
                monday:
                  items:
                    $ref: '#/definitions/Lesson'
                  minItems: 8
                  maxItems: 8
            
      503:
          description: Retry-After:100
  """
  sch = full_sched(group)
  if sch:
    response = jsonify(sch)
    # return "today for{} is {}".format(group, res)
    return make_response(response)
  res = Response(headers={'Retry-After':200}, status=503)
  return res 

@app.route('/api/schedule/schedule_for_cache', methods=["GET"])
def schedule_for_cache():
  """Current week's schedule for requested group
    ---
      
    responses:
      200:
        description: Return full schedule of one group. There are 8 lessons on a day. "lesson":null, if there is no pair.
        schema:
          type: object
          properties:
            1:
              type: object
              properties:
                monday:
                  items:
                    $ref: '#/definitions/Lesson'
                  minItems: 8
                  maxItems: 8
            
      503:
          description: Retry-After:100
  """
  sch = for_cache()
  if sch:
    response = jsonify(sch)
    # return "today for{} is {}".format(group, res)
    return make_response(response)
  res = Response(headers={'Retry-After':200}, status=503)
  return res

