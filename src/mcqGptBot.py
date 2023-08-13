#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        Mutli-Choice-Question-GPT-Bot
#
# Purpose:     This module is used to help people to batch process the multi
#              choice cyber security exam questions via Open-AI to get the 
#              answer so the researcher can use it to check the AI's correctness
#              rate.
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
# load the langchain libs
from langchain.llms import OpenAI
from langchain.chains.llm import LLMChain

from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI

# import different file loader
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders import WebBaseLoader
from langchain.document_loaders import UnstructuredPDFLoader

import mcqGPTBotGlobal as gv

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class QuestionParser(object):
    """ Load the function data from files or URL, then use AI to parse the 
        mcqs and generate the standard question bank data.
    """
    def __init__(self, openAIkey=None, msqTemplate=gv.MCQ_TEMPLATE) -> None:
        """ Init example: mcqParser = QuestionParser(openAIkey=<OpenAI-Key-String>,
            msqTemplate = <question bank string format>
        )
            Args:
                openAIkey (_type_, str): openAIkey. Defaults to None.
                msqTemplate (_type_, str): _description_. Defaults to gv.MCQ_TEMPLATE.
        """
        if openAIkey: os.environ["OPENAI_API_KEY"] = openAIkey
        self.dataloader = None
        self.databankList = []
        self.questionTemplate = PromptTemplate.from_template(msqTemplate)
        self.llm = ChatOpenAI(temperature=0, model_name=gv.AI_MODEL)
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.questionTemplate)
        # Define StuffDocumentsChain
        self.stuff_chain = StuffDocumentsChain(
            llm_chain=self.llm_chain, document_variable_name="text"
        )

    def clearDatabank(self):
        self.databankList = []

    def getDatabank(self):
        return self.databankList

    def getQuestions(self, src, srcType='txt'):
        result = None
        srcType = str(srcType).lower()
        if  srcType == 'txt' or srcType == 'html':
            if os.path.exists(src):
                gv.gDebugPrint('Processing source file: %s' % str(src), logType=gv.LOG_INFO)
                loader = UnstructuredHTMLLoader(src, mode="elements")
                data = loader.load()
                result = self.stuff_chain.run(data)
            else:
                gv.gDebugPrint('Source file: %s not exist' % str(src))
        elif srcType == 'url':
            gv.gDebugPrint('Processing MCQ url: %s' % str(src), logType=gv.LOG_INFO)
            loader = WebBaseLoader(src)
            data = loader.load()
            result = self.stuff_chain.run(data)
        elif srcType == 'pdf':
            if os.path.exists(src):
                gv.gDebugPrint('Processing prf source file: %s' % str(src), logType=gv.LOG_INFO)
                loader = UnstructuredPDFLoader(src)
                data = loader.load_and_split()
                result = self.stuff_chain.run(data)
        else:
            gv.gDebugPrint("The input src type [%s] is not valid" %str(srcType))
        return result

    def addToDatabank(self, src, result):
        dataElement = {
            'src': src,
            'mcqList': ['Question:%s' %ct for ct in result.split('Question:')]
        }
        self.databankList.append(dataElement)

    def loadQuestions(self, src, srcType='txt'):
        data = self.getQuestions(src, srcType=srcType)
        self.addToDatabank(src, data)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class McqGPTBot(object):

    def __init__(self, openAIkey=None, createQb=False) -> None:
        self.createQb = createQb
        self.openAIkey = openAIkey if openAIkey else gv.API_KEY
        os.environ["OPENAI_API_KEY"] = self.openAIkey
        self.mcqBanksList = None
        self.mcqParser = QuestionParser(openAIkey=self.openAIkey)

    def loadNewMcqBanks(self, qbDictFile):
        """ load the new question bacnk dictionary json file."""
        if os.path.exists(qbDictFile):
            with open(qbDictFile) as fh:
                self.mcqBanksList = json.load(fh)
        else:
            gv.gDebugPrint("The MCQ bank dictionary json file not exist.")
    
    def processMcqBanks(self):
        if self.mcqBanksList:
            gv.gDebugPrint("Start to process %s question banks" %str(len(self.mcqBanksList)), logType=gv.LOG_INFO)
            for item in self.mcqBanksList:
                bankName = item['name']
                bankType = item['type']
                bankSrc = item['src'] if str(bankType).lower() == 'url' else os.path.join(gv.Q_BANK_DIR, item['src'])
                self.mcqParser.clearDatabank()
                self.mcqParser.loadQuestions(bankSrc, srcType=bankType)
                mcqList = self.mcqParser.getDatabank()
                # create the standard question bank
                if self.createQb:
                    bankFilePath = os.path.join(gv.Q_BANK_DIR, bankName+'.txt')
                    gv.gDebugPrint("Create question bank file: %s" %bankFilePath)
                    with open(bankFilePath, 'a') as fh:
                        for mcqDict in mcqList:
                            srcLine = '# Src:'+ mcqDict['src'] +'\n'
                            fh.write(srcLine)
                            for line in mcqDict['mcqList']:
                                fh.write(line)
        else:
            gv.gDebugPrint("No Questions Bank loaded, please call function loadNewMcqBanks() to load the data.", logType=gv.LOG_INFO)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def testCase():
    
    mcqBot = McqGPTBot(createQb=True)
    mcqBot.loadNewMcqBanks(gv.gMcqBankContent)
    mcqBot.processMcqBanks()
    #txtFile = gv.gQuestionsFile
    #data = mcqParser.getQuestions(txtFile, srcType='html')

    #data = mcqParser.getQuestions(txtFile, srcType='pdf')
    #src = "https://www.yeahhub.com/certified-ethical-hacker-v10-multiple-choice-questions-answers-part-9/"
    #data = mcqParser.getQuestions(src, srcType='url')
    
    #mcqParser.loadQuestions(txtFile)
    #print(data)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase()






