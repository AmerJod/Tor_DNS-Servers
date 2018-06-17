from flask import render_template, redirect, url_for, request
from datetime import datetime
from app import app, db
from .models import Request

@app.route('/', methods=['GET', 'POST'])
def index():

    r =  Request(ip=request.remote_addr, datetime=datetime.now())
    db.session.add(r)
    db.session.commit()

    # stroe in json file

    return render_template("index.html")