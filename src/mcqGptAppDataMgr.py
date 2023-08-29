#-----------------------------------------------------------------------------
# Name:        dataManager.py
#
# Purpose:     A manager class running in the sub-thead to handle all the data
#              shown in the ***state page.
#              
# Author:      Yuancheng Liu, 
#
# Version:     v_0.2
# Created:     2022/09/04
# Copyright:   
# License:     
#-----------------------------------------------------------------------------
import os
import json
import time
import threading
import mcqGptAppGlobal as gv
import mcqGptBotUtils as botUtils

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManager(threading.Thread):

    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)
        self.parent = parent
        os.environ["OPENAI_API_KEY"] = gv.API_KEY
        # Init the data manager
        self.dataMgr = botUtils.McqDataManager()
        # Init the mcq question parser
        self.mcqParser = botUtils.QuestionParser(openAIkey=gv.API_KEY, 
                                                 mcqTemplate=gv.MCQ_TEMPLATE)
        # Init the mcq solver
        self.mcqSolver = botUtils.llmMcqSolver(systemTemplate=gv.SCE_TEMPLATE)
        self.terminate = False
        self.startProFlg = False

    def updateWebLog(self, logMsg):
        if gv.iSocketIO:
            gv.gWeblogCount +=1
            gv.iSocketIO.emit('serv_response',{'data': str(logMsg), 'count': gv.gWeblogCount})

#-----------------------------------------------------------------------------
    def run(self):
        """ Thread run() function call by start(). """
        #Log.info("gv.iDataMgr: run() function loop start, terminate flag [%s]", str(
        #    self.terminate), printFlag=LOG_FLAG)
        time.sleep(1)  # sleep 1 second to wait socketIO start to run.
        while not self.terminate:
            if self.startProFlg:
                self.processMcqFile()
                self.startProFlg = False
            time.sleep(0.5)

#-----------------------------------------------------------------------------
    def startProcess(self):
        self.startProFlg = True

#-----------------------------------------------------------------------------
    def processMcqFile(self):
        if gv.gSrceName and gv.gSrcType:
            bankName = str(gv.gSrceName).rsplit('.', 1)[0] + '_result'
            bankType = gv.gSrcType
            bankSrc = os.path.join(gv.UPLOAD_FOLDER, gv.gSrceName) 
            gv.gDebugPrint("Start to process %s" %str(bankName), 
                          logType=gv.LOG_INFO)
            self.updateWebLog("Start to parse questions from: %s" %str(bankName))
            questionlist = self.mcqParser.getQuestions(bankSrc, srcType=bankType)
            self.dataMgr.addQuestions(bankName, bankSrc, questionlist)
            gv.gDebugPrint("- finished parsing the questions from source.")
            self.updateWebLog("- finished parsing the questions from source.")