#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        mcqGPTApp.py [python3]
#
# Purpose:     The web interface of the Multi-Choice-Question-GPT-Bot for user 
#              to batch processing the multi-choice cyber security exam questions 
#              via Open-AI to get the answers.
#  
# Author:      Yuancheng Liu
#
# Created:     2023/08/23
# version:     v0.1.4
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
# CSS lib [bootstrap]: https://w3schools.com/bootstrap5/
# https://www.w3schools.com/howto/howto_css_form_on_image.asp
# https://medium.com/the-research-nest/how-to-log-data-in-real-time-on-a-web-page-using-flask-socketio-in-python-fb55f9dad100

import os
import threading

from datetime import timedelta 
from flask import Flask, render_template, flash, url_for, redirect, request, session
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit # pip install Flask-SocketIO==5.3.5

import mcqGptAppGlobal as gv

async_mode = None

#-----------------------------------------------------------------------------
# Init the flask web app program.
def createApp():
    """ Create the flask App with the data manager."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = gv.APP_SEC_KEY
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=gv.COOKIE_TIME)
    app.config['UPLOAD_FOLDER'] = gv.UPLOAD_FOLDER
    # init the data manager is not under web test mode.
    print("Program test mode: %s" %str(gv.gTestMD))
    if not gv.gTestMD:
        import mcqGptAppDataMgr as dataManager
        gv.iDataMgr = dataManager.DataManager(app)
        if not gv.iDataMgr: exit()
        gv.iDataMgr.start()
    return app

#-----------------------------------------------------------------------------
def createTemMcqFile(contents):
    """ Create a temporary file used to save the security MCQ contents which 
        upload by the user directly.
        Args:
            contents (str): _description_
    """
    filename = 'tempQuestionFile.txt'
    gv.gAppParmDict['srcName'] = filename
    gv.gAppParmDict['srcPath'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    gv.gAppParmDict['srcType'] = 'txt'
    gv.gAppParmDict['rstPath'] = None
    with open(gv.gAppParmDict['srcPath'], "w") as outfile:
        outfile.write(contents)
    return True

def checkFile(filename):
    """ Check whether the upload file name is valid."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in gv.ALLOWED_EXTENSIONS

def uploadfile(file):
    """ upload a file from the post request"""
    print(file.filename)
    if file.filename == '':
        flash('No selected file')
    elif file and checkFile(file.filename):
        filename = secure_filename(file.filename)
        gv.gAppParmDict['srcName'] = filename
        gv.gAppParmDict['srcPath'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        gv.gAppParmDict['srcType'] = filename.rsplit('.', 1)[1].lower()
        gv.gAppParmDict['rstPath'] = None
        file.save(gv.gAppParmDict['srcPath'])
        return True
    return False 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
gv.gAppParmDict['funcMode'] = None
gv.gAppParmDict['webMsgCount'] = 0
gv.gAppParmDict['srcName'] = None
gv.gAppParmDict['srcPath'] = None
gv.gAppParmDict['srcType'] = None
gv.gAppParmDict['rstPath'] = None

app = createApp()
socketio = SocketIO(app, async_mode=async_mode)
gv.iSocketIO = socketio
thread = None
threadLock = threading.Lock()

#-----------------------------------------------------------------------------
# web request handling functions. 
@app.route('/')
def index():
    # page index is used to highlight the left page slide bar.
    posts = {'page': 1}
    return render_template('index.html',
                           async_mode=socketio.async_mode,
                           posts=posts)

@app.route('/introduction')
def introduction():
    return render_template('intro.html', posts={'page': 0})

@app.route('/mdselect', methods = ['POST', 'GET'])  
def mdselect():
    """ Handle the AI mode (get ans or calcuate correctness rate)."""
    posts = {'page': 1, 'mode': gv.gAppParmDict['funcMode']}
    if request.method == 'POST':
        option = request.form['options']
        if gv.iDataMgr:
            gv.gAppParmDict['funcMode'] = 1 if option == 'mode1'else 2
            gv.iDataMgr.reInitQuestionParser(mode=gv.gAppParmDict['funcMode'])
            posts['mode'] = gv.gAppParmDict['funcMode']
    return render_template('index.html', posts=posts)

@app.route('/fileupload', methods = ['POST', 'GET'])  
def fileupload():
    posts = {'page': 1, 'mode': gv.gAppParmDict['funcMode']}
    if request.method == 'POST':
        file = request.files['file']
        rst = uploadfile(file)
        if not rst: return redirect(request.url)  
        posts['filename'] = gv.gAppParmDict['srcName']
    return render_template('index.html', posts=posts)

@app.route('/urlupload', methods=['POST', 'GET'])
def urlupload():
    posts = {'page': 1, 'mode': gv.gAppParmDict['funcMode']}
    if request.method == 'POST':
        urlStr = request.form['mcqurl']
        posts['filename'] = gv.gAppParmDict['srcName'] = 'mcq_from_url'
        gv.gAppParmDict['srcPath'] = urlStr
        gv.gAppParmDict['srcType'] = 'url'
        gv.gAppParmDict['rstPath'] = None
    return render_template('index.html', posts=posts)

@app.route('/textupload', methods=['POST', 'GET'])
def textupload():
    posts = {'page': 1, 'mode': gv.gAppParmDict['funcMode']}
    if request.method == 'POST':
        data = request.form['text']
        print(data)
        rst = createTemMcqFile(data)
    return render_template('index.html', posts=posts)

#-----------------------------------------------------------------------------
# socketIO communication handling functions. 
@socketio.event
def connect():
    gv.gAppParmDict['webMsgCount'] = 0
    emit('serv_response', 
         {'data': 'MCQ-Solver Ready \n', 'count': gv.gAppParmDict['webMsgCount']})

@socketio.event
def cli_request(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    if message['data'] == 'download' and gv.gAppParmDict['rstPath']:
        if os.path.exists(gv.gAppParmDict['rstPath']):
            gv.gDebugPrint("Download the file.", logType=gv.LOG_INFO)
            with open(gv.gAppParmDict['rstPath']) as fh:
                socketio.emit('file_ready', 
                              {'filename': gv.gAppParmDict['srcName'], 'content': fh.read()})
    else:
        emit('serv_response',
             {'data': message['data'], 'count': session['receive_count']})
    
@socketio.on('startprocess')
def startProcess(data):
    print('received message: ' + str(data))
    gv.iDataMgr.startProcess()
    emit('startprocess', 
         {'data': 'Starting to process MCQ-source: %s \n' %str(gv.gAppParmDict['srcName'])})

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=5000,  debug=False, threaded=True)
    app.run(host=gv.gflaskHost,
            port=gv.gflaskPort,
            debug=gv.gflaskDebug,
            threaded=gv.gflaskMultiTH)
