#-----------------------------------------------------------------------------
# Name:        mcqGptPromptRepo.py
#
# Purpose:     This module is used save different MCQ question and the exam 
#              scenario AI-prompt 
#              
# Author:      Yuancheng Liu
#
# Created:     2023/08/21
# Version:     v_0.1.2
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# defile all the question parsing AI prompts here:

# Question parse prompt without parse the answer.
MCQ_Q_PROMPT = """Find all the multiple choice questions from the text:
"{text}", reformat them and list all the questions under below format:

Question:<question string>
A.choice
B.choice
C.choice
D.choice
"""
# Question parse prompt with parse the answer.
MCQ_QA_PROMPT = """Find all the multiple choice questions with answer from the text:
"{text}", reformat them and list all the questions with answer under below format:

Question:<question string>
A.choice
B.choice
C.choice
D.choice
Answer:
"""

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# define all the question/exam scenario AI prompts here:

# Question solution template.
MCQ_SOL_PROMPT = """You are a helpful assistant who find the answer of the 
cyber security multi choice questions. Just give the correct choice's front indicator 
character or characters (if the question shows you need to choose more than one choice). 
Return choice indicator character in a in a comma separated list. 
"""

# CISCO CCPN exam prompt here
CCNP_SOL_PROMPT = """You are a helpful assistant who find the answer of the Cisco
CCNP Security Implementing Cisco Secure Access multi choice questions. Just give the 
correct choice's front indicator character or characters (if the question shows you 
need to choose more than one choice). Return choice indicator character in a in a comma 
separated list. 
"""

# Certified Ethical Hacker exam prompt here
CEH_SOL_PROMPT = """You are a helpful assistant who find the answer of the certified 
Ethical Hacker multi choice questions exam. Just give the correct choice's front indicator 
character or characters (if the question shows you need to choose more than one choice). 
Return choice indicator character in a in a comma separated list. 
"""