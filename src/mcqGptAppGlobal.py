#-----------------------------------------------------------------------------
# Name:        mcqGPTBotGlobal.py
#
# Purpose:     This module is used as a local config file to set constants, 
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2010/08/26
# Version:     v_0.1.2
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
"""
For good coding practice, follow the following naming convention:
    1) Global variables should be defined with initial character 'g'
    2) Global instances should be defined with initial character 'i'
    2) Global CONSTANTS should be defined with UPPER_CASE letters
"""

import os, sys

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(__file__) if os.path.dirname(__file__) else os.getcwd()
print("Current source code location : %s" % dirpath)
APP_NAME = ('OpenAI', 'mcq_bot')

TOPDIR = 'src'
LIBDIR = 'lib'

#-----------------------------------------------------------------------------
# Init the logger:
idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir):
    sys.path.insert(0, gLibDir)
import Log
Log.initLogger(gTopDir, 'Logs', APP_NAME[0], APP_NAME[1], historyCnt=100, fPutLogsUnderDate=True)

# Init the log type parameters.
DEBUG_FLG   = False
LOG_INFO    = 0
LOG_WARN    = 1
LOG_ERR     = 2
LOG_EXCEPT  = 3

def gDebugPrint(msg, prt=True, logType=None):
    if prt: print(msg)
    if logType == LOG_WARN:
        Log.warning(msg)
    elif logType == LOG_ERR:
        Log.error(msg)
    elif logType == LOG_EXCEPT:
        Log.exception(msg)
    elif logType == LOG_INFO or DEBUG_FLG:
        Log.info(msg)

#-----------------------------------------------------------------------------
# load the config file.
import ConfigLoader
CONFIG_FILE_NAME = 'config.txt'
gGonfigPath = os.path.join(dirpath, CONFIG_FILE_NAME)
iConfigLoader = ConfigLoader.ConfigLoader(gGonfigPath, mode='r')
if iConfigLoader is None:
    print("Error: The config file %s is not exist.Program exit!" %str(gGonfigPath))
    exit()
CONFIG_DICT = iConfigLoader.getJson()

#-----------------------------------------------------------------------------
# Init the openAI parameters.
API_KEY = CONFIG_DICT['API_KEY']
os.environ["OPENAI_API_KEY"] = API_KEY
AI_MODEL = CONFIG_DICT['AI_MODEL']

# Default mcq question AI prompt
MCQ_TEMPLATE = """Find all the multiple choice questions from the text:
"{text}", reformat them and list all the questions under below format:

Question:<question string>
A.choice
B.choice
C.choice
D.choice
"""

# default mcq exam scenario AI prompt
SCE_TEMPLATE = """You are a helpful assistant who find the answer of the 
cyber security multi choice questions. Just give the correct choice's front indicator 
character or characters (if the question shows you need to choose more than one choice). 
Return choice indicator character in a in a comma separated list. 
"""

# question bank file
Q_BANK_DIR = os.path.join(dirpath, CONFIG_DICT['QS_BANK_DIR'])
FILTER_CHAR = ('#', ' ', '\n', '\r', '\t')

# Init the web app glocal vars

RC_TIME_OUT = 10    # reconnection time out.
APP_SEC_KEY = 'secrete-key-goes-here'
UPDATE_PERIODIC = 15
COOKIE_TIME = 30

UPLOAD_FOLDER = os.path.join(dirpath, 'uploadFolder')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'html', 'md', 'pdf', 'json'}

#-------<GLOBAL VARIABLES (start with "g")>------------------------------------
# VARIABLES are the built in data type.
gMcqBankContent = os.path.join(Q_BANK_DIR, CONFIG_DICT['QS_CONT_JSON'])

import mcqGptPromptRepo
# ser the question AI prompt
gMcqQuestionPrompt = None
if 'MCQ_PROMPT' in CONFIG_DICT.keys() and hasattr(mcqGptPromptRepo, CONFIG_DICT['MCQ_PROMPT']):
    gDebugPrint("Use question AI prompt: %s " % str(CONFIG_DICT['MCQ_PROMPT']))
    gMcqQuestionPrompt = getattr(mcqGptPromptRepo, CONFIG_DICT['MCQ_PROMPT'])
else:
    gDebugPrint("Use default question AI prompt")
    gMcqQuestionPrompt = MCQ_TEMPLATE

gMcqScearioPrompt = None
if 'SCE_PROMPT' in CONFIG_DICT.keys() and hasattr(mcqGptPromptRepo, CONFIG_DICT['SCE_PROMPT']):
    gDebugPrint("Use scenario AI prompt: %s " % str(CONFIG_DICT['SCE_PROMPT']))
    gMcqScearioPrompt = getattr(mcqGptPromptRepo, CONFIG_DICT['SCE_PROMPT'])
else:
    gDebugPrint("Use default question AI prompt")
    gMcqScearioPrompt = SCE_TEMPLATE

gWeblogCount = 0 
gSrceName = None
gSrcType = None

#-------<GLOBAL PARAMTERS>-----------------------------------------------------
iSocketIO = None
iDataMgr = None