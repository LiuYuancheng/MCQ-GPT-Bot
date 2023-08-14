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
# Version:     v_0.1
# Copyright:   n.a
# License:     n.a
#-----------------------------------------------------------------------------

import os
import json

import openai

import mcqGPTBotGlobal as gv
import mcqGptBotUtils as botUtils

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class McqGPTBot(object):

    def __init__(self, openAIkey=None, createQb=False) -> None:
        self.createQb = createQb
        self.openAIkey = openAIkey if openAIkey else gv.API_KEY
        os.environ["OPENAI_API_KEY"] = self.openAIkey
        self.dataMgr = botUtils.McqDataManager()
        self.mcqParser = botUtils.QuestionParser(openAIkey=self.openAIkey, 
                                                 msqTemplate=gv.MCQ_QA_TEMPLATE)

#-----------------------------------------------------------------------------
    def _createQBfile(self, bankFilePath, mcqDict, aiAnsFlg=False):
        gv.gDebugPrint("Create question bank file: %s" %bankFilePath)
        with open(bankFilePath, 'a', encoding="utf8") as fh:
            srcLine = '# Src:'+ mcqDict['src'] +'\n'
            fh.write(srcLine)
            logAiAnswer = False
            if mcqDict['aiAnswers'] and aiAnsFlg: logAiAnswer = True
            for idx, question in enumerate(mcqDict['mcqList']):
                fh.write(question)
                if logAiAnswer and idx < len(mcqDict['aiAnswers']):
                    aiAnsStr = 'AiAns:' + mcqDict['aiAnswers'][idx] + '\n'
                    fh.write(question)

#-----------------------------------------------------------------------------
    def loadNewMcqBanks(self, qbDictFile):
        """ load the new question bank dictionary json file."""
        if os.path.exists(qbDictFile):
            with open(qbDictFile) as fh:
                self.mcqBanksList = json.load(fh)
        else:
            gv.gDebugPrint("The MCQ bank dictionary json file not exist.")

#-----------------------------------------------------------------------------
    def processMcqBanks(self, createQb=None):
        if self.mcqBanksList:
            gv.gDebugPrint("Start to process %s question banks" %str(len(self.mcqBanksList)), logType=gv.LOG_INFO)
            for item in self.mcqBanksList:
                bankName = item['name']
                bankType = item['type']
                bankSrc = item['src'] if str(bankType).lower() == 'url' else os.path.join(gv.Q_BANK_DIR, item['src'])
                questionlist = self.mcqParser.getQuestions(bankSrc, srcType=bankType)
                self.dataMgr.addQuestions(bankName, bankSrc, questionlist)
                mcqDict = self.dataMgr.getMcqData(mcqSetName=bankName)
                bankFilePath = os.path.join(gv.Q_BANK_DIR, bankName+'.txt')
                self._createQBfile(bankFilePath, mcqDict)
        else:
            gv.gDebugPrint("No Questions Bank loaded, please call function loadNewMcqBanks() to load the data.", logType=gv.LOG_INFO)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    
    mcqBot = McqGPTBot(createQb=True)
    mcqBot.loadNewMcqBanks(gv.gMcqBankContent)
    mcqBot.processMcqBanks()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()






