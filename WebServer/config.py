WTF_CSRF_ENABLED = True
SECRET_KEY = 'bsajdfdsf$£^%$dsjkioe4895ry48fdf;E"RFE"RWE""'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'project.sqlite')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True
