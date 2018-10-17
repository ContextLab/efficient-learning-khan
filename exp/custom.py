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

# # to call script on finish
from subprocess import call
import os
import csv
import base64
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

###########################################################
#  serving warm, fresh, & sweet custom, user-provided routes
#  add them here
###########################################################
#@custom_code.route('/createaudiofolder',methods=['POST'])
#def createFolder():
#    print('creating audio folder...')
#    call('mkdir ' + '/data/' + request.form['data'], shell=True)
#    print(request.form['data'])
#    resp = {"folderCreated": "success"}
#    return jsonify(**resp)
#
#@custom_code.route('/save_audio', methods=['POST'])
#def save_audio():
#    print('saving audio...')
#    """ Save an audio file"""
#    try:
#        # get file name
#        filename = request.form['audio-filename']
#
#        # get folder name
#        foldername = request.form['audio-foldername']
#
#        # get audio file
#        wav = request.files
#
#        # file path
#        fname ='/data/' + foldername + "/" + filename
#
#        # write out audio file
#        wav['audio-blob'].save(fname)
#
#        resp = {'message' : "Sucessfully saved audio file: " + fname,
#                'fname' : fname}
#
#        print('audio saved!')
#    except Exception as e:
#        print(e)
#        resp = {"message": "There was an error saving the audio file: " + fname}
#
#    return jsonify(**resp)
