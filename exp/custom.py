# this file imports custom routes into the experiment server
from flask import Blueprint, render_template, request, jsonify, Response, abort, current_app
from jinja2 import TemplateNotFound
from functools import wraps
from sqlalchemy import or_

from psiturk.psiturk_config import PsiturkConfig
from psiturk.experiment_errors import ExperimentError
from psiturk.user_utils import PsiTurkAuthorization, nocache

# # Database setup
from psiturk.db import db_session, init_db
from psiturk.models import Participant
from json import dumps, loads

import sqlalchemy
import json

#from base64 import b64encode
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError

# # to call script on finish
from subprocess import call
import os
import csv
import base64
import sys
import glob
import json
import traceback

cwd = os.getcwd()
# dir_path = os.path.dirname(os.path.realpath(__file__))

# load the configuration options
config = PsiturkConfig()
config.load_config()
myauth = PsiTurkAuthorization(config)  # if you want to add a password protect route use this

# explore the Blueprint
custom_code = Blueprint('custom_code', __name__, template_folder='templates', static_folder='static')

@custom_code.route('/compute_bonus', methods=['GET']) #originally post
def compute_bonus():
    #get uniqueId
    if not request.args.has_key('uniqueId'):
        raise ExperimentError('improper_inputs')
    uniqueId = request.args['uniqueId']

    try:
        # lookup user in database
        user = Participant.query.\
               filter(Participant.uniqueid == uniqueId).\
               one()
        user_data = loads(user.datastring) # load datastring from JSON
        bonus = 0 # initialize

    except:
        abort(404)  # quick solution, update **
