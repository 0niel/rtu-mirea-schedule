from app import app
from flask import Flask, flash, request, redirect, url_for, session, jsonify, render_template, make_response
import requests
from os import environ  
import datetime
from schedule import today_sch, tomorrow_sch, week_sch

####
@app.route('/<string:group>/today', methods=["GET"])
def today(group):
    res = {'schedule': today_sch(group)}
    response = jsonify(res)
    # return "today for{} is {}".format(group, res)
    return make_response(response)

#############
@app.route('/<string:group>/tomorrow', methods=["GET"])
def tomorrow(group):
    res = {'schedule': tomorrow_sch(group)}
    response = jsonify(res)
    # return "tomorrow for{} is {}".format(group, res)
    return make_response(response)

@app.route('/<string:group>/week', methods=["GET"])
def week(group):
    res = {'schedule': week_sch(group)}
    response = jsonify(res)
    # return "week for{} is {}".format(group, res)
    return make_response(response)