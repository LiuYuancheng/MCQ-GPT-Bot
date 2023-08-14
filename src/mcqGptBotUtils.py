#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        Multi-Choice-Question-GPT-Bot untils 
#
# Purpose:     This module will provide different function modules used 
# 
# Author:      Yuancheng Liu
#
# Created:     2023/08/11
# Version:     v_0.1
# Copyright:   n.a
# License:     n.a
#-----------------------------------------------------------------------------

import os

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
    def __init__(self, openAIkey=None, msqTemplate=gv.MCQ_Q_TEMPLATE) -> None:
        """ Init example: mcqParser = QuestionParser(openAIkey=<OpenAI-Key-String>,
            msqTemplate = <question bank string format>
        )
            Args:
                openAIkey (_type_, str): openAIkey. Defaults to None.
                msqTemplate (_type_, str): _description_. Defaults to gv.MCQ_Q_TEMPLATE.
        """
        if openAIkey: os.environ["OPENAI_API_KEY"] = openAIkey
        self.questionTemplate = PromptTemplate.from_template(msqTemplate)
        self.llm = ChatOpenAI(temperature=0, model_name=gv.AI_MODEL)
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.questionTemplate)
        # Define StuffDocumentsChain
        self.stuff_chain = StuffDocumentsChain(
            llm_chain=self.llm_chain, document_variable_name="text"
        )

#-----------------------------------------------------------------------------
    def _parseQuestions(self, src, srcType='txt'):
        """ parse questions from the src file/url
            Args:
                src (str): ctf questions source.
                srcType (str, optional): questions source type. Defaults to 'txt'.

            Returns:
                _type_: _description_
        """
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
            gv.gDebugPrint("The input src type [%s] is not valid" % str(srcType))
        return result

#-----------------------------------------------------------------------------
    def getQuestions(self, src, srcType='txt'):
        """ Get the question list from the question source. """
        result = self._parseQuestions(src, srcType=srcType)
        if result: return ['Question:%s' % ct for ct in result.split('Question:')]
        return None

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class McqDataManager(object):

    def __init__(self) -> None:
        self.questionBank = {}

    def addQuestions(self, mcqSetName, src, questionList):
        questionSet = {
            'src': src,
            'mcqList': questionList,
            'aiAnswers': None
        }
        self.questionBank[mcqSetName] = questionSet

    def addAiAnswers(self, mcqSetName, answerList):
        if mcqSetName in self.questionBank.keys():
            self.questionBank[mcqSetName]['aiAnswers'] = answerList

    def clearQuestionBank(self):
        self.questionBank = {}

    def getMcqData(self, mcqSetName=None):
        if mcqSetName is None:
            return self.questionBank
        elif mcqSetName in self.questionBank.keys():
            return self.questionBank[mcqSetName]
        return None
