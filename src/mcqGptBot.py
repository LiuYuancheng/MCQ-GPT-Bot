#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        Mutli-Choice-Question-GPT
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

import mcqGPTBotGlobal as gv


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class QuestionParser(object):
    def __init__(self, openAIkey=None, msqTemplate=gv.MCQ_TEMPLATE) -> None:
        if openAIkey:
            os.environ["OPENAI_API_KEY"] = openAIkey
        self.dataloader = None
        self.databankList = []
        self.questionTemplate = PromptTemplate.from_template(msqTemplate)
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
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
            loader = WebBaseLoader(src)
            data = loader.load()
            result = self.stuff_chain.run(data)

        return result

    def addToDatabank(self, src, result):
        dataElement = {
            'src': src,
            'mcqList': ['Question:' + ct for ct in result.split('Question:')]
        }
        self.databankList.append(dataElement)

    def loadQuestions(self, src, srcType='txt'):
        data = self.getQuestions(src, srcType=srcType)
        self.addToDatabank(src, data)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def testCase():
    
    mcqParser = QuestionParser()
    #txtFile = gv.gQuestionsFile
    #data = mcqParser.getQuestions(txtFile, srcType='html')
    src = "https://www.yeahhub.com/certified-ethical-hacker-v10-multiple-choice-questions-answers-part-9/"
    data = mcqParser.getQuestions(src, srcType='url')
    #mcqParser.loadQuestions(txtFile)
    print(data)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase()






