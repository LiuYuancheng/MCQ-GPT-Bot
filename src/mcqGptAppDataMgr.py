#-----------------------------------------------------------------------------
# Name:        mcqGptAppDataMgr.py
#
# Purpose:     A MCQ data manager class to hold the MCQ solve bot and manage the 
#              result of the mcq question. 
#                 
# Author:      Yuancheng Liu, 
#
# Version:     v_0.1.4
# Created:     2023/09/04
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License 
#-----------------------------------------------------------------------------

import os
import time
import threading
import mcqGptAppGlobal as gv
import mcqGptBotUtils as botUtils

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class DataManager(threading.Thread):
    """ A data manager class (with a MCQ parser and a MCQ solver) running in the 
        sub-thread to accept the MCQ question from the Web UI, use the mcq parser 
        to parse the question, and use the mcq solver to generate the AI answer.
        The result of the mcq question will be saved to the result download folder 
        for user to download from the webUI.
    """
    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)
        self.parent = parent
        os.environ["OPENAI_API_KEY"] = gv.API_KEY
        # Init the data manager
        self.dataMgr = botUtils.McqDataManager()
        # Init the mcq question parser
        self.mcqParserMode = 1
        self.mcqParser = botUtils.QuestionParser(openAIkey=gv.API_KEY, 
                                                 mcqTemplate=gv.MCQ_TEMPLATE)
        # Init the mcq solver
        self.mcqSolver = botUtils.llmMcqSolver(systemTemplate=gv.SCE_TEMPLATE)
        self.terminate = False
        self.startProFlg = False

    #-----------------------------------------------------------------------------
    def _createQBfile(self, bankFilePath, mcqDict, aiAnsFlg=False):
        """ Create the question bank file.
        Args:
            bankFilePath (str): question bank file path.
            mcqDict (dict): mcq data dictionary. example:
                {
                    'src': src if src else mcqSetName,
                    'mcqList': questionList,
                    'crtAnswers': answerList,
                    'aiAnswers': None
                }
            aiAnsFlg (bool, optional): whether append AI answer behind the 
                question. Defaults to False.
        """
        gv.gDebugPrint("Create question bank file: %s" %bankFilePath, logType=gv.LOG_INFO)
        with open(bankFilePath, 'w', encoding="utf8") as fh:
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
    def appendCompareResult(self, bankFilePath, correctCount, totalCount):
        """ Append the correnctness calculation reuslt in the result file.
            Args:
                bankFilePath (str): result file path
                correctCount (int): correct answer count
                totalCount (int): total question count
        """
        with open(bankFilePath, 'a', encoding="utf8") as fh:
            fh.write('\n')
            fh.write('AI Answer compare (correct / total) : %s / %s ' %
                     (str(correctCount), str(totalCount)))
            if totalCount == 0: totalCount = 1
            fh.write('Correctness rate : %s' %str(float(correctCount)/totalCount))

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
            self.updateWebLog("- start to process question %s / %s " % (str(idx+1), str(questionNum)))
            ans, aians, crt = self.mcqSolver.compareAnswer(question)
            answerList.append(aians)
            if crt: correctCount +=1
        self.dataMgr.addAiAnswers(bankName, answerList)
        return (correctCount, len(questionList))

    #-----------------------------------------------------------------------------
    def reInitQuestionParser(self, mode=1):
        """ ReInit the question parser based on the user setting
            Args:
                mode (int, optional): 
                - 1: User AI to get the answer. 
                - 2: Compare the AI answer with the correct input to calcuate the 
                correctness rate.  
                Defaults to 1.
        """
        if mode == self.mcqParserMode: return
        self.mcqParserMode = mode
        mcqTemplate = gv.MCQ_TEMPLATE if self.mcqParserMode == 1 else gv.gMcqQuestionPrompt
        self.mcqParser = botUtils.QuestionParser(openAIkey=gv.API_KEY,
                                                 mcqTemplate=mcqTemplate)
        gv.gDebugPrint('MCQ question parser mode set to : [%s]' % str(self.mcqParserMode),
                       logType=gv.LOG_INFO)


    #-----------------------------------------------------------------------------
    def updateWebLog(self, logMsg):
        """Update the contents in the web log text field."""
        gv.gDebugPrint(logMsg, logType=gv.LOG_INFO)
        if gv.iSocketIO:
            gv.gWeblogCount += 1
            gv.iSocketIO.emit('serv_response', {'data': str(logMsg)+'\n', 'count': gv.gWeblogCount})

    #-----------------------------------------------------------------------------
    def startProcess(self):
        """ Set the tart process flag."""
        if self.startProFlg: return False # There is one process on going .
        self.startProFlg = True
        return True

    #-----------------------------------------------------------------------------
    def run(self):
        """ Thread run() function call by start(). """
        gv.gDebugPrint( "gv.iDataMgr: run() function loop start, terminate flag [%s]" %str(self.terminate), 
                       logType=gv.LOG_INFO)
        time.sleep(1)  # sleep 1 second to wait socketIO start to run.
        while not self.terminate:
            if self.startProFlg:
                self.processMcqFile()
                self.startProFlg = False
            time.sleep(0.5)
    
    #-----------------------------------------------------------------------------
    def processMcqFile(self):
        if gv.gAppParmDict['srcName'] and gv.gAppParmDict['srcType']:
            bankName = str(gv.gAppParmDict['srcName']).rsplit('.', 1)[0] + '_result'
            bankType = gv.gAppParmDict['srcType']
            bankSrc = gv.gAppParmDict['srcPath']
            self.updateWebLog("Start to generate reuslt to : %s" %str(bankName))
            questionlist = self.mcqParser.getQuestions(bankSrc, srcType=bankType)
            self.dataMgr.addQuestions(bankName, bankSrc, questionlist)
            self.updateWebLog("- finished parsing the questions from source.")
            mcqDict = self.dataMgr.getMcqData(mcqSetName=bankName)
            crt = total = 0
            crt, total = self.compareAIAnswers(bankName, mcqDict['mcqList'])
            bankFilePath = os.path.join(gv.DOWNLOAD_FOLDER, bankName+'.txt')
            self._createQBfile(bankFilePath, mcqDict, aiAnsFlg=True)
            self.appendCompareResult(bankFilePath, crt, total)
            gv.gDebugPrint("Finished process all the questions.")
            self.updateWebLog("Finished process all the questions.")
            self.updateWebLog("Downloading result...")
        else:
            gv.gDebugPrint("The input source or type in not valid: %s" %str((gv.gAppParmDict['srcName'], 
                                                                    gv.gAppParmDict['srcType'])), logType=gv.LOG_WARN)
