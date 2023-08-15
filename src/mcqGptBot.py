#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        Multi-Choice-Question-GPT-Bot
#
# Purpose:     This module is used to help people to batch process the multi-choice 
#              cyber security exam questions via Open-AI to get the answer so the 
#              researcher can use it to check the AI's correctness rate.
# 
# Author:      Yuancheng Liu
#
# Created:     2023/08/11
# Version:     v_0.1.2
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import os
import json

import mcqGPTBotGlobal as gv
import mcqGptBotUtils as botUtils

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class McqGPTBot(object):

    def __init__(self, openAIkey=None, mcqTemplate=gv.MCQ_QA_TEMPLATE) -> None:
        self.openAIkey = openAIkey if openAIkey else gv.API_KEY
        os.environ["OPENAI_API_KEY"] = self.openAIkey
        self.dataMgr = botUtils.McqDataManager()
        self.mcqParser = botUtils.QuestionParser(openAIkey=self.openAIkey, 
                                                 mcqTemplate=mcqTemplate)
        self.mcqSolver = botUtils.llmMcqSolver()


#-----------------------------------------------------------------------------
    def _createQBfile(self, bankFilePath, mcqDict, aiAnsFlg=False):
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
    def loadNewMcqBanks(self, qbDictFile):
        """ load the new question bank dictionary json file."""
        if os.path.exists(qbDictFile):
            with open(qbDictFile) as fh:
                self.mcqBanksList = json.load(fh)
        else:
            gv.gDebugPrint("The MCQ bank dictionary json file not exist.")

#-----------------------------------------------------------------------------
    def updateAIAnswers(self, bankName, questionList):
        answerList = []
        for question in questionList:
            answer = self.mcqSolver.getAnswer(question)
            answerList.append(answer)
        self.dataMgr.addAiAnswers(bankName, answerList)

#-----------------------------------------------------------------------------
    def compareAIAnswers(self, bankName, questionList):
        answerList = []
        correctCount = 0
        for question in questionList:
            ans, aians, crt = self.mcqSolver.compareAnswer(question)
            answerList.append(aians)
            if crt: correctCount +=1
        self.dataMgr.addAiAnswers(bankName, answerList)
        return (correctCount, len(questionList))

    def appendCompareResult(self, bankFilePath, correctCount, totalCount):
        with open(bankFilePath, 'a', encoding="utf8") as fh:
            fh.write('\n')
            fh.write('AI Answer compare (correct / totaol) : %s / %s ' % (str(correctCount), str(totalCount)))
            if totalCount == 0: totalCount = 1
            fh.write('Correctness rate : %s' % str(float(correctCount)/totalCount))

#-----------------------------------------------------------------------------
    def processMcqBanks(self, calCrtRate=False):
        if self.mcqBanksList:
            gv.gDebugPrint("Start to process %s question banks" %str(len(self.mcqBanksList)), logType=gv.LOG_INFO)
            for item in self.mcqBanksList:
                bankName = item['name']
                bankType = item['type']
                bankSrc = item['src'] if str(bankType).lower() == 'url' else os.path.join(gv.Q_BANK_DIR, item['src'])
                questionlist = self.mcqParser.getQuestions(bankSrc, srcType=bankType)
                self.dataMgr.addQuestions(bankName, bankSrc, questionlist)
                mcqDict = self.dataMgr.getMcqData(mcqSetName=bankName)
                # get the questions solution
                crt = total = 0
                if calCrtRate:
                    crt, total = self.compareAIAnswers(bankName, mcqDict['mcqList'])
                else:
                    self.updateAIAnswers(bankName, mcqDict['mcqList'])
                bankFilePath = os.path.join(gv.Q_BANK_DIR, bankName+'.txt')
                self._createQBfile(bankFilePath, mcqDict, aiAnsFlg=True)
                if calCrtRate:
                    self.appendCompareResult(bankFilePath, crt, total)

            gv.gDebugPrint("Finished process all the question source.")
        else:
            gv.gDebugPrint("No Questions Bank loaded, please call function loadNewMcqBanks() to load the data.", logType=gv.LOG_INFO)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    #mcqBot = McqGPTBot(mcqTemplate=gv.MCQ_Q_TEMPLATE)
    mcqBot = McqGPTBot()
    mcqBot.loadNewMcqBanks(gv.gMcqBankContent)
    mcqBot.processMcqBanks(calCrtRate=True)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()






