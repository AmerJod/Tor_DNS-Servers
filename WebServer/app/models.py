from app import db

class Request(db.Model):
    req_id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String)
    datetime = db.Column(db.String)

