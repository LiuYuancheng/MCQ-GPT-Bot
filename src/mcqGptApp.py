#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        app.py [python3]
#
# Purpose:     This module is the main website host program to host the scheduled
#              tasks monitor Hub webpage by using python-Flask frame work. 
#  
# Author:      Yuancheng Liu
#
# Created:     2022/01/13
# version:     v0.2
# Copyright:   National Cybersecurity R&D Laboratories
# License:     
#-----------------------------------------------------------------------------

# CSS lib [bootstrap]: https://www.w3schools.com/bootstrap4/default.asp

# https://www.w3schools.com/howto/howto_css_form_on_image.asp

import os
import json

from datetime import timedelta, datetime
from flask import Flask, render_template, request, flash, url_for, redirect
from werkzeug.utils import secure_filename


import mcqGptAppGlobal as gv

TEST_MD = False # Test mode flag.

#-----------------------------------------------------------------------------
# Init the flask web app program.
def createApp():
    """ Create the flask App."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = gv.APP_SEC_KEY
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=gv.COOKIE_TIME)
    app.config['UPLOAD_FOLDER'] = gv.UPLOAD_FOLDER
    return app

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
app = createApp()

#-----------------------------------------------------------------------------
# web home request handling functions. 
@app.route('/')
def index():
    return render_template('index.html')

#-----------------------------------------------------------------------------
@app.route('/introduction')
def introduction():
    return render_template('introduction.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in gv.ALLOWED_EXTENSIONS

@app.route('/upload', methods = ['POST', 'GET'])  
def upload():
    if request.method == 'POST':
        file = request.files['file']
        print(file.filename)
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('index.html')


#-----------------------------------------------------------------------------
@app.route('/introduction')
def schedulermgmt():
    return render_template('introduction.html')


#-----------------------------------------------------------------------------
@app.route('/<int:postID>')
def peerstate(postID):
    #peerInfoDict = dataManager.buildPeerInfoDict(postID)
    return render_template('peerstate.html',posts=peerInfoDict)
 
#-----------------------------------------------------------------------------
@app.route('/<string:peerName>/<int:jobID>/<string:action>', methods=('POST',))
def changeTask(peerName, jobID, action):
    #peerInfo = gv.iDataMgr.getOnePeerDetail(peerName)
    #posts = gv.iDataMgr.changeTaskState(peerName, jobID, action)
    return redirect(url_for('peerstate', postID=peerInfo['id']))

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,  debug=False, threaded=True)
