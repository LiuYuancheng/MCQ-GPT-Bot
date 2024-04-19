#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        Multi-Choice-Question-GPT-Bot
#
# Purpose:     This module is used to help user to batch processing the multi-choice 
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

import mcqGptPromptRepo
import mcqGPTBotGlobal as gv
import mcqGptBotUtils as botUtils

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class McqGPTBot(object):

    def __init__(self, openAIkey=None, 
                 mcqTemplate=gv.MCQ_TEMPLATE,
                 solTemplate=gv.SCE_TEMPLATE
                 ) -> None:
        
        self.openAIkey = openAIkey if openAIkey else gv.API_KEY
        os.environ["OPENAI_API_KEY"] = self.openAIkey
        # Init the data manager
        self.dataMgr = botUtils.McqDataManager()
        # Init the mcq question parser
        self.mcqParser = botUtils.QuestionParser(mcqTemplate=mcqTemplate)
        # Init the mcq solver
        self.mcqSolver = botUtils.llmMcqSolver(systemTemplate=solTemplate)

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
    def loadNewMcqBanksSrcJson(self, qbDictFile):
        """ load the new question bank dictionary json file."""
        if os.path.exists(qbDictFile):
            with open(qbDictFile) as fh:
                self.mcqBanksList = json.load(fh)
        else:
            gv.gDebugPrint("The MCQ bank dictionary json file not exist.")

    def loadNewMcqSrc(self, qbDict):
        self.mcqBanksList = [qbDict]

#-----------------------------------------------------------------------------
    def updateAIAnswers(self, bankName, questionList):
        """ Get the AI's answer of the questions and update the data manager's 
            record.
        """
        answerList = []
        questionNum = len(questionList)
        for idx, question in enumerate(questionList):
            gv.gDebugPrint("- start to process question %s / %s " % (str(idx+1), str(questionNum)))
            answer = self.mcqSolver.getAnswer(question)
            answerList.append(answer)
        self.dataMgr.addAiAnswers(bankName, answerList)

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
            ans, aians, crt = self.mcqSolver.compareAnswer(question)
            answerList.append(aians)
            if crt: correctCount +=1
        self.dataMgr.addAiAnswers(bankName, answerList)
        return (correctCount, len(questionList))
    
#-----------------------------------------------------------------------------
    def appendCompareResult(self, bankFilePath, correctCount, totalCount):
        with open(bankFilePath, 'a', encoding="utf8") as fh:
            fh.write('\n')
            fh.write('AI Answer compare (correct / total) : %s / %s ' % (str(correctCount), str(totalCount)))
            if totalCount == 0: totalCount = 1
            fh.write('Correctness rate : %s' % str(float(correctCount)/totalCount))

#-----------------------------------------------------------------------------
    def processMcqBanks(self, calCrtRate=False):
        """ process the questions in the data manager.
            Args:
                calCrtRate (bool, optional): flag to indenfiy whether to calculate 
                the AI solution correctness rate. Defaults to False.
        """
        if self.mcqBanksList:
            gv.gDebugPrint("Start to process %s question banks" %str(len(self.mcqBanksList)), logType=gv.LOG_INFO)
            for item in self.mcqBanksList:
                bankName = item['name']
                bankType = item['type']
                bankSrc = item['src'] if str(bankType).lower() == 'url' else os.path.join(gv.Q_BANK_DIR, item['src'])
                questionlist = self.mcqParser.getQuestions(bankSrc, srcType=bankType)
                gv.gDebugPrint("- finished parsing the questions from source.")
                self.dataMgr.addQuestions(bankName, bankSrc, questionlist)
                mcqDict = self.dataMgr.getMcqData(mcqSetName=bankName)
                # get the questions solution
                crt = total = 0
                if calCrtRate:
                    crt, total = self.compareAIAnswers(bankName, mcqDict['mcqList'])
                else:
                    self.updateAIAnswers(bankName, mcqDict['mcqList'])
                bankFilePath = os.path.join(gv.Q_BANK_DIR, bankName+'_AIresult.txt')
                self._createQBfile(bankFilePath, mcqDict, aiAnsFlg=True)
                if calCrtRate:
                    self.appendCompareResult(bankFilePath, crt, total)
            gv.gDebugPrint("Finished process all the question source.")
        else:
            gv.gDebugPrint("No Questions Bank loaded, please call \
                           function loadNewMcqBanks() to load the data.", logType=gv.LOG_INFO)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main(mode):
    # mcqBot = McqGPTBot(mcqTemplate=gv.MCQ_Q_TEMPLATE)
    # mcqBot = McqGPTBot(solTemplate=gv.CCNA_SOL_TEMPLATE)
    if mode == 0:
        print("Start the automatic mode processing....")
        mcqBot = McqGPTBot(mcqTemplate=gv.gMcqQuestionPrompt,
                           solTemplate=gv.gMcqScearioPrompt)
        mcqBot.loadNewMcqBanksSrcJson(gv.gMcqBankContent)
        mcqBot.processMcqBanks(calCrtRate=True)
    elif mode == 1:
        print("Start the manual mode processing....")
        #
        print("*\nStep2 : select the process mode (Type in the number):")
        print(" - 0. Use LLM AI to get the answer.(default)")
        print(" - 1. Compare AI result to calculate the correctness rate.")
        pmode = int(input())
        gv.gMcqQuestionPrompt = mcqGptPromptRepo.MCQ_QA_PROMPT if pmode else mcqGptPromptRepo.MCQ_Q_PROMPT
        #
        print("*\nStep3 : select the MCQ solution prompt:")
        print(" - 0. Normal security question solve prompt.(default)")
        print(" - 1. Certified Ethical Hacker exam prompt.")
        print(" - 2. CISCO CCPN network security exam prompt.")
        prompt = int(input())
        gv.gMcqScearioPrompt = mcqGptPromptRepo.MCQ_SOL_PROMPT
        if prompt == 1:
            gv.gMcqScearioPrompt = mcqGptPromptRepo.CEH_SOL_PROMPT
        elif prompt == 2:
            gv.gMcqScearioPrompt = mcqGptPromptRepo.CCNP_SOL_PROMPT
        mcqBot = McqGPTBot(mcqTemplate=gv.gMcqQuestionPrompt,
                           solTemplate=gv.gMcqScearioPrompt)
        while True:
            print("*\nStep4.1 : Select the question bank source type (Type in the number):")
            print(" - 0. txt\n - 1. html\n - 2. url\n - 3. pdf\n - 4. json\n - 5. md\n - 6. exit")
            inputVal = int(input())
            if inputVal >= 6:
                break
            typelist = ['txt', 'html', 'url', 'pdf', 'json', 'md']
            qbType = typelist[inputVal]
            print("*\nStep4.2: Input the question bank source file name (under folder 'questionbank'):")
            qbFilePath = input()
            print("*\nStep4.3: Input the output result file name")
            outputName = input()
            qbDict = {
                "name": outputName,
                "type": qbType,
                "src": qbFilePath
            }
            mcqBot.loadNewMcqSrc(qbDict)
            mcqBot.processMcqBanks(calCrtRate=False)
    else:
        print("Invalid mode, please check the usage mode.")

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    print("*\nStep1 : Please select the usage mode (Type in the number):")
    print(" - 0. Auto mode based on all paramters from config file.(default)")
    print(" - 1. Manual mode (user input all the parameters).")
    mode = int(input())
    main(mode)
