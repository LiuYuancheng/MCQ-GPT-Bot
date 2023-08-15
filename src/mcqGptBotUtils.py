#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        Multi-Choice-Question-GPT-Bot untils 
#
# Purpose:     This module will provide different function modules used 
# 
# Author:      Yuancheng Liu
#
# Created:     2023/08/14
# Version:     v_0.1
# Copyright:   n.a
# License:     n.a
#-----------------------------------------------------------------------------

import os

# load the langchain libs
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI

from langchain.chains.summarize import load_summarize_chain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import BaseOutputParser

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
        if result: 
            data = ['Question:%s' % ct for ct in result.split('Question:')]
            return data[1:]
        return None

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class McqDataManager(object):

    def __init__(self) -> None:
        self.questionBank = {}

    def addQuestions(self, mcqSetName, src, questionList, answerList=None):
        questionSet = {
            'src': src if src else mcqSetName,
            'mcqList': questionList,
            'crtAnswers': answerList,
            'aiAnswers': None
        }
        self.questionBank[mcqSetName] = questionSet

#-----------------------------------------------------------------------------
    def addStandQuestionFile(self, bankName, questionFile):

        if os.path.exists(questionFile):
            questionList = []
            answerList = []
            with open(questionFile, encoding="utf8") as fp:
                questionStr = None
                answerStr = None
                for line in fp.readlines():
                    if line[0] in gv.FILTER_CHAR: continue
                    line = line.strip('\n')
                    # a new question is found
                    if 'Question:' in line:
                        # Add the old question in the question list.
                        if questionStr: questionList.append(questionStr)
                        questionStr = line.split(':', 1)[1]
                    elif questionStr:
                        # handler multi-lines questions
                        if 'Answer:' in line:
                            answerStr = line.split(':', 1)[1]
                            answerList.append(answerStr.strip())
                        else:
                            questionStr += line
                # when finish scan all line add the last question:
                if questionStr: questionList.append(questionStr)
            if len(questionList) == len(answerList):
                self.addQuestions(bankName, None, questionList, answerList=answerList )
            else:
                gv.gDebugPrint("Question number and answer number not match, please check the bank file: %s" % questionFile,
                                logType=gv.LOG_WARN)
        else:
            gv.gDebugPrint(" Question bank file not exit: %s" % questionFile,
                                logType=gv.LOG_WARN)

#-----------------------------------------------------------------------------
    def addAiAnswers(self, mcqSetName, answerList):
        if mcqSetName in self.questionBank.keys():
            self.questionBank[mcqSetName]['aiAnswers'] = answerList

#-----------------------------------------------------------------------------
    def addCrtAnswers(self, mcqSetName, answerList):
        if mcqSetName in self.questionBank.keys():
            self.questionBank[mcqSetName]['crtAnswers'] = answerList

#-----------------------------------------------------------------------------
    def clearQuestionBank(self):
        self.questionBank = {}

#-----------------------------------------------------------------------------
    def getMcqData(self, mcqSetName=None):
        if mcqSetName is None:
            return self.questionBank
        elif mcqSetName in self.questionBank.keys():
            return self.questionBank[mcqSetName]
        return None

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class CommaSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""
    def parse(self, text: str):
        """Parse the output of an LLM call."""
        return text.strip().split(", ")


class llmMcqSolver(object):

    def __init__(self, openAIkey=None, systemTemplate=gv.MCQ_SOL_TEMPLATE) -> None:
        if openAIkey: os.environ["OPENAI_API_KEY"] = openAIkey
        sysTemplate = SystemMessagePromptTemplate.from_template(systemTemplate)
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([sysTemplate, human_message_prompt])
        self.llmChain = LLMChain(llm=ChatOpenAI(), 
                                 prompt=chat_prompt, 
                                 output_parser=CommaSeparatedListOutputParser())

    def getAnswer(self, questionString):
        if 'Answer:' in questionString: questionString = questionString.split('Answer:')[0]
        answerList = self.llmChain.run(questionString)
        if answerList: 
            answerList.sort()
            return ''.join(answerList)
        else:
            gv.gDebugPrint('AI not able to find answer for question: %s ' % questionString)
            return None

    def compareAnswer(self, questionString, answerStr=None):
        """ Compare the AI answer with the correct answer """
        aiAnswer = self.getAnswer(questionString)
        if answerStr:
            answerStr = str(answerStr).strip()
            answerStr = ''.join([*answerStr].sort())
        else:
            if 'Answer:' in questionString:
                answerStr = questionString.questionString.split('Answer:')[1]
                answerStr = answerStr.replace('\n', '')
                answerStr = answerStr.replace(' ', '')
        return (answerStr, aiAnswer, aiAnswer==answerStr)
