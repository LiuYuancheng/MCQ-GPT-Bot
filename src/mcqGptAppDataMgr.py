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

    def appendCompareResult(self, bankFilePath, correctCount, totalCount):
        with open(bankFilePath, 'a', encoding="utf8") as fh:
            fh.write('\n')
            fh.write('AI Answer compare (correct / total) : %s / %s ' % (str(correctCount), str(totalCount)))
            if totalCount == 0: totalCount = 1
            fh.write('Correctness rate : %s' % str(float(correctCount)/totalCount))

#-----------------------------------------------------------------------------
    def compareAIAnswers(self, bankName, questionList):
        """ Get the AI's answer of the questions and compare with the correct answer
            to calcuate the answer correctness rate.
            Returns:
                (int, int): (correct_Answer_Count, total_Question_count)
        """
        answerList = []
        correctCount = 0
        questionNum = len(questionList)
        for idx, question in enumerate(questionList):
            gv.gDebugPrint("- start to process question %s / %s " % (str(idx+1), str(questionNum)))
            self.updateWebLog("- start to process question %s / %s " % (str(idx+1), str(questionNum)))
            ans, aians, crt = self.mcqSolver.compareAnswer(question)
            answerList.append(aians)
            if crt: correctCount +=1
        self.dataMgr.addAiAnswers(bankName, answerList)
        return (correctCount, len(questionList))

#-----------------------------------------------------------------------------
    def _createQBfile(self, bankFilePath, mcqDict, aiAnsFlg=False):
        """ Create the question bank file.
        Args:
            bankFilePath (str): question bank file path.
            mcqDict (dict): mcq data dictionary. examle:
                {
                    'src': src if src else mcqSetName,
                    'mcqList': questionList,
                    'crtAnswers': answerList,
                    'aiAnswers': None
                }
            aiAnsFlg (bool, optional): whether append AI answer behind the 
                question. Defaults to False.
        """
        gv.gDebugPrint("Create question bank file: %s" %bankFilePath)
        with open(bankFilePath, 'a', encoding="utf8") as fh:
            srcLine = '# Src:'+ mcqDict['src'] +'\n'
            fh.write(srcLine)
            logAiAnswer = False
            if mcqDict['aiAnswers'] and aiAnsFlg: logAiAnswer = True
            for idx, question in enumerate(mcqDict['mcqList']):
                fh.write(question.strip('\n'))
                fh.write('\n')
                if logAiAnswer and idx < len(mcqDict['aiAnswers']):
                    aiAnsStr = 'AiAns:' + mcqDict['aiAnswers'][idx] + '\n'
                    fh.write(aiAnsStr)
                fh.write('\n')

#-----------------------------------------------------------------------------
    def processMcqFile(self):
        if gv.gSrceName and gv.gSrcType:
            bankName = str(gv.gSrceName).rsplit('.', 1)[0] + '_result'
            bankType = gv.gSrcType
            bankSrc = gv.gSrcPath
            gv.gDebugPrint("Start to process %s" %str(bankName), 
                          logType=gv.LOG_INFO)
            self.updateWebLog("Start to parse questions from: %s" %str(bankName))
            questionlist = self.mcqParser.getQuestions(bankSrc, srcType=bankType)
            self.dataMgr.addQuestions(bankName, bankSrc, questionlist)
            gv.gDebugPrint("- finished parsing the questions from source.")
            self.updateWebLog("- finished parsing the questions from source.")
            mcqDict = self.dataMgr.getMcqData(mcqSetName=bankName)
            crt = total = 0
            crt, total = self.compareAIAnswers(bankName, mcqDict['mcqList'])
            bankFilePath = os.path.join(gv.DOWNLOAD_FOLDER, bankName+'.txt')
            self._createQBfile(bankFilePath, mcqDict, aiAnsFlg=True)
            self.appendCompareResult(bankFilePath, crt, total)
            gv.gRstPath = bankFilePath
            gv.gDebugPrint("Finished process all the questions.")
            self.updateWebLog("Finished process all the questions.")
            self.updateWebLog("Downloading result...")
