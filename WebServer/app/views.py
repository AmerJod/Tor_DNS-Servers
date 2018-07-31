import json
import os

from flask import render_template, redirect, url_for, request
from datetime import datetime
from app import app, db
from .models import Request


JsonRequestsPATH = 'JSON/NormalRequests/HTTPRequestNodes'
JsonRequestsPATHCheck = 'JSON/CheckingRequests/HTTPCheckingRequestNodes' # store all the request about checkoing if the dns supports 0x20 code


@app.route('/', methods=['GET', 'POST'])
def index():
    req = Request(ip=request.remote_addr, datetime=datetime.now())
    # store it in json file
    storeHTTPRequestJSON(time=str(datetime.now()),srcIP=request.remote_addr, baseUrl=request.base_url)
    # storing in the database, so much data
    #db.session.add(req)
    #db.session.commit()
    return render_template("index.html")


@app.route('/thesis', methods=['GET', 'POST'])
def thesis():
    return render_template("thesis.html")

@app.route('/aboutUs', methods=['GET', 'POST'])
def aboutUs():
    return render_template("aboutUs.html")

@app.route('/check', methods=['GET', 'POST'])
def check():
    req = Request(ip=request.remote_addr, datetime=datetime.now())
    # store it in json file
    storeHTTPRequestJSON(time=str(datetime.now()),srcIP=request.remote_addr ,baseUrl=request.base_url, mode='check')
    # storing in the database, so much data
    #db.session.add(req)
    #db.session.commit()
    return render_template("check.html")


#TODO: need to implmment a class for it
def storeHTTPRequestJSON(time,srcIP,baseUrl,mode='none'):
    """Help for the bar method of Foo classes"""
    date = getTime(2)
    if mode == 'check':
        file = JsonRequestsPATHCheck + '_' + date + '.json'
    else:
        # TODO: need refactoring - make it more abstract
        file = JsonRequestsPATH + '_' + date + '.json'

    jsons = {}

    if (os.path.exists(file)) != True: # check if the file exist, if not create it.
        with open(file, 'w+') as jsonfile:
            json.dump(' ', jsonfile)
    else:
        with open(file, 'r') as jsonfile:
            jsons = json.load(jsonfile)

    with open(file,'w') as jsonfile:
        DNSRequestNodes = {
            'Request': {
                'ID': str(len(jsons)+1),
                'Time': time,
                'SrcIP': srcIP,
                'Url':  baseUrl,
            }
        }
        jsons[str(len(jsons)+1)] = DNSRequestNodes
        # Write into Json file
        json.dump(jsons, jsonfile)



# option: 1 full (time+date)
# option: 2 date
# option: 3 time
def getTime(opt = 1):
    date = datetime.now()
    if opt == 1:    # full
        return (((str(date)).split('.')[0]).split(' ')[1] + ' ' + ((str(date)).split('.')[0]).split(' ')[0])
    if opt == 2:    # date
        return (((str(date)).split('.')[0]).split(' ')[0])
    if opt == 3:    # time
        return (((str(date)).split('.')[0]).split(' ')[1])