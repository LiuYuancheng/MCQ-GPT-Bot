# MCQ-GPT-Bot

**Program design**:  We want to create an assistant AI-Bot program which can batch process the multi choice cyber security exam questions (From different source format : `md` `url`, `html`, `txt`, `pdf`) via OpenAI to get the answers so the researcher can use it to check the AI's answer correctness rate, AI's performance on solving question on different fields and do further data analysis.

[TOC]

- [MCQ-GPT-Bot](#mcq-gpt-bot)
    + [Introduction](#introduction)
        * [Program Workflow Diagram](#program-workflow-diagram)
        * [AI Solution Correctness](#ai-solution-correctness)
    + [Program Design](#program-design)
        * [Program module files list](#program-module-files-list)
    + [Program Setup](#program-setup)
          + [Development Environment : python 3.8.2 rc2](#development-environment---python-382-rc2)
          + [Additional Lib/Software Need](#additional-lib-software-need)
          + [Hardware Needed : None](#hardware-needed---none)
    + [Program Usage](#program-usage)
        * [Step1: Copy the MCQ source file](#step1--copy-the-mcq-source-file)
        * [Step2: Set the configuration file](#step2--set-the-configuration-file)
        * [Step3: Run the Bot to batch process all the MCQ source](#step3--run-the-bot-to-batch-process-all-the-mcq-source)
    + [Problem and solution](#problem-and-solution)
        * [Problem [0]: Execution Exception: OpenAI API timeout](#problem--0---execution-exception--openai-api-timeout)
    + [Reference](#reference)
        * [AI Answer's Correctness rate for cyber security MCQ question test:](#ai-answer-s-correctness-rate-for-cyber-security-mcq-question-test-)



------

### Introduction

The MCQ-GPT-Bot will is an automate AI-Bot assistant program which provides below functions: 

- Parse multi-choice-questions from different format data source to build the standard question bank files for the further process such as training (data normalization) .
- If the question sources don't content the answer, use OpenAI to get the answer (with or without the scenario prompt) . 
- If the question sources also provide the answer, compare with AI's answer and calculate the AI's correctness rate.

The program will use the LLM [LangChain](https://python.langchain.com/docs/get_started/introduction.html) frame work to implement the communication with the OpenAI-API.

##### Program Workflow Diagram

The program will follow below workflow to load the question sources, process the questions and archive the result:

![](doc/img/workflow.png)

The program is a single thread program to continuous loading all the question source files/urls set in the config file, convert to the standard question format, then based on the question type setup the LLM's scenario prompt and send to the questions solver to get the AI's solution. If you have multiple OpenAI-API, you can also config multi-thread with several parser and question solver to increase the processing efficiency.

##### AI Solution Correctness 

Based on our test to applying on 500+ MCQ question, currently for different level difficulty cyber security question (such as CISCO-CCIE, Huawei Certified Network Associate exam, IBM Security QRadar certificate exam ...) , the AI can provide **60% to 80%** correctness rate. For the correctness test, please refer to the reference section: [AI Answer's Correctness rate for cyber security MCQ question test](#ai-answer-s-correctness-rate-for-cyber-security-mcq-question-test-)

##### Current Stable Program Version 

`Version: v0.1.2` 



------

### Program Design 

As shown in the workflow diagram, the MCQ data will be processed follow the data flow below:

```mermaid
graph LR;
A[MCQ data mining] -->  B
B[MCQ data normalization] --> C
C[MCQ data storage] --> D
D[MCQ data analysis] --> E
E[result archiving]
```

The program will provide three main modules to finish the steps: 

##### QuestionParser

The MCQ question data parser (QuestionParser) will do the data mining and normalization step,  it will load all the contents from MCQ source files or URL, use AI to find all the MCQs,  then generate the standard question bank data. All the questions will be formatted to below text format:

```
Question:< Question string >
A. choice 1
B. choice 2
C. choice 3
D. choice 4
```

##### McqDataManager 

The MCA data manager (McqDataManger) will do the data storage and result archiving step, it will store and questions, AI's answers and format the result. As we will batch process multiple question source, the data manager will log the process progress (such as whether a source file's result has been archived) so if there is program execution interruption happens, when the user run again, the don't need to process the source from the beginning. 

##### llmMcqSolver 

The large language MCQ solver (llmMcqSolver) will fetch the question from the data manager, preload the MCQ questions scenario prompt to OpenAI, then call OpenAI API to get the answer and calculate the AI's correctness rate based on the setting. After process, different kind of question format source will be convert to the standard question bank file format as shown blow: 

![](doc/img/convert.png)

The question bank file (data archiving) will be built as a text file which follow below format: 

```
Question:< Question string >
A. choice 1
B. choice 2
C. choice 3
D. choice 4
Answer:<correct answer>
AiAns:<Answer gave by OpenAI>

Question:< Question string >
...
AI Answer compare (correct / total) : <correct number> / <total number>
Correctness rate: <>
```



##### Question Solution Prompt

Based on our test, the AI will provide a higher problem solving correctness rate if we load a problem solving scenario prompt to the AI before we pass the real MCQ question to llmMcqSolver. For example if we want to process the Cisco CCNP Security Implementing Cisco Threat Control Solutions Exam, when we pre-load the below CCPN prompt to the AI before pass the question to AI: 

```
CCNA_SOL_TEMPLATE = """You are a helpful assistant who find the answer of the Cisco
CCNP Security Implementing Cisco Secure Access multi choice questions. Just give the 
correct choice's front indicator character or characters (if the question shows you 
need to choose more than one choice). Return choice indicator character in a in a comma 
separated list. 
"""
```

The correctness rate will increate from (10/24) **41.66%** (If we don't set scenario prompt) to (12/24) **50.0%** if we test 24 questions. If you load a good scenario prompt to the AI, AI will understand the question better especially for the worlds abbreviations appear in the question.



##### Program module files list

| Idx  | Program File                       | Execution Env | Description                                                  |
| ---- | ---------------------------------- | ------------- | ------------------------------------------------------------ |
| 1    | src/config.txt                     |               | System config file.                                          |
| 2    | src/mcqGptBot.py                   | python 3      | Main MCQ auto batch process program.                         |
| 3    | src/mcqGptBotUtils.py              | python 3      | Provide different OpenAI utility function modules used by the MCQ-GPT-Bot modules. |
| 4    | src/mcqGptBotGlobal.py             | python 3      | System global file, the system config file's contents will be saved in the global parameters. |
| 5    | lib/ConfigLoader.py                | python 3      | Configuration file loading module.                           |
| 6    | lib/Log.py                         | python 3      | Log module.                                                  |
| 7    | questionbank/*                     |               | All the question source files.                               |
| 8    | questionbank/questionContents.json |               | Question source config json file.                            |



------

### Program Setup

###### Development Environment : python 3.8.2 rc2

###### Additional Lib/Software Need

1. **OpenAI** : https://github.com/openai/openai-python
2. **langChain** :  https://python.langchain.com/docs/get_started/installation
3. **Pylib need to install**:

```
pip install unstructured
pip install pdf2image
pip install pdfminer
pip install pdfminer-six
pip install --upgrade openai
pip install langchain
```

4. **Valid OpenAI-API key** : https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key

###### Hardware Needed : None



------

### Program Usage

Please follow below steps to process the MCQ source files:

##### Step1: Copy the MCQ source files

Copy the MCQ files ( `*.html`, `*.txt`, `*.md`, `*.pdf` )  you want to process and `questionContents.json` to the a folder in the `src` folder (such as the `questionbank` ).  Add/Append the files you want to process in the `questionContents.json` as below : 

```
"name": "test_question_bank03",
"type": "url",
"src": "https://www.yeahhub.com/certified-ethical-hacker-v10-multiple-choice-questions-answers-part-9/"
```

- **name** : The question bank file name you want to archive.
- **type**: Mcq source type ( current support type: html, url, md, pdf, txt).
- **src**: The source file name or URL.



##### Step2: Set the Bot execution configuration file

Rename the configuration file template `config_template.txt` to `config.txt` and add you OpenAI-API key as below:

```
# This is the config file template for the module <mcqGptBot.py>
# Setup the parameter with below format (every line follow <key>:<val> format, the
# key cannot be changed):

# set openAI API key
API_KEY: <Yout own OpenAI API key>

# select the AI model apply to the mcq.
AI_MODEL:gpt-3.5-turbo-16k

# folder name of the question source files, the source folder need to be in the 
# same folder of mcqGptBot.py.
QS_BANK_DIR:questionbank

# The json file which contents the source files information need to process in the 
# question source folder.
QS_CONT_JSON:questionContents.json
```



##### Step3: Run the Bot to batch process all the MCQ sources

Run program:

```
python mcqGptBot.py
```

The processed question will be saved in the text question bank file which same name as the name you set in the `questionContents.json` file. You can refer to the questionbank folder to check the detail. Example: 

`network-secuirty-quiz-questions-answers.pdf` => `test_question_bank03.txt`



------

### Problem and solution

##### Problem [0]: Execution Exception: OpenAI API timeout

If you are using Free OpenAI-API key, one minutes you can only process 3 questions, so you may met timeout problem as shown below: 

```
(vEnv3.8) C:\Works\NCL\Project\ChatGPT_on_MCQ\src>python mcqGptBot.py
Current working directory is : C:\Works\NCL\Project\ChatGPT_on_MCQ\src
Current source code location : C:\Works\NCL\Project\ChatGPT_on_MCQ\src
> Init(): load 4 lines of config
Start to process 4 question banks
Processing source file: C:\Works\NCL\Project\ChatGPT_on_MCQ\src\questionbank\questionbank_19.txt
Question parse finish.
- finished parsing the questions from source.
Create question bank file: C:\Works\NCL\Project\ChatGPT_on_MCQ\src\questionbank\test_question_bank01.txt
Processing source file: C:\Works\NCL\Project\ChatGPT_on_MCQ\src\questionbank\questionbank_20.html
Question parse finish.
- finished parsing the questions from source.
Create question bank file: C:\Works\NCL\Project\ChatGPT_on_MCQ\src\questionbank\test_question_bank02.txt
Processing MCQ url: https://www.yeahhub.com/certified-ethical-hacker-v10-multiple-choice-questions-answers-part-9/
Question parse finish.
- finished parsing the questions from source.
Create question bank file: C:\Works\NCL\Project\ChatGPT_on_MCQ\src\questionbank\test_question_bank03.txt
Processing prf source file: C:\Works\NCL\Project\ChatGPT_on_MCQ\src\questionbank\network-secuirty-quiz-questions-answers.pdf
Question parse finish.
```

This is normal, you need to update you OpenAI account to a payment account. 



------

### Reference



##### AI Answer's Correctness rate for cyber security MCQ question test: 

| idx  | Question bank                                                | Question bank file     | correct  Answer  num | total Question num | correct rate                 |
| ---- | ------------------------------------------------------------ | ---------------------- | -------------------- | ------------------ | ---------------------------- |
| 1    | CTF cyber-security question example (javatpoint exam)        | questionbank_00.txt    | 39                   | 60                 | 65.0%                        |
| 2    | ISA Cybersecurity Specialist Exam (ICS/IEC 62443)            | questionbank_01.txt    | 30                   | 38                 | 78.94%                       |
| 3    | CCIE Advanced Security Written Exam 2023                     | questionbank_02.txt    | 46                   | 63                 | 73.01%                       |
| 4    | Microsoft Cybersecurity Architect SC100                      | questionbank_03.txt    | 33                   | 43                 | 76.74 %                      |
| 5    | 首届360杯网络安全职业技能CTF大赛初赛                         | 360CTF理论大赛试题.pdf |                      |                    | Applying for answer          |
| 6    | 华东师范 XCTF 集训营 2020                                    | questionbank_07.txt    |                      |                    | need to translate to English |
| 7    | Yeahhub CTF-repo: Certified Ethical Hacker 2021 v10 exam part (1-2) | questionbank_08.txt    | 38                   | 46                 | 82.60 %                      |
| 8    | Yeahhub CTF-repo: Certified Ethical Hacker 2021 v10 exam part (3-4) | questionbank_09.txt    | 38                   | 53                 | 71.69%                       |
| 9    | Yeahhub CTF-repo: Certified Ethical Hacker 2021 v10 exam part (5-6) | questionbank_10.txt    | 31                   | 62                 | 50.0%                        |
| 10   | Yeahhub CTF-repo: Certified Ethical Hacker 2021 v10 exam part (7-8) | questionbank_11.txt    | 38                   | 45                 | 84.44%                       |
| 11   | Yeahhub CTF-repo: Certified Ethical Hacker 2021 v10 exam part (9-10) | questionbank_12.txt    | 35                   | 45                 | 77.77%                       |
| 12   | Yeahhub CTF-repo: Certified Ethical Hacker 2021 v10 exam part (11-12) | questionbank_13.txt    | 36                   | 46                 | 78.26%                       |
| 13   | Yeahhub CTF-repo: Certified Ethical Hacker 2021 v10 exam part (13-14) | questionbank_14.txt    | 32                   | 44                 | 72.72 %                      |
| 14   | CCNA Security Implementing Cisco Network Security Exam       | questionbank_15.txt    | 34                   | 55                 | 61.81%                       |
| 15   | CCNP Security Implementing Cisco Edge Network Security Solutions (SENSS) Exam | questionbank_16.txt    | 32                   | 58                 | 55.17%                       |
| 16   | CCNP Security Implementing Cisco Secure Access Solutions (SISAS) Exam | questionbank_17.txt    | 12                   | 24                 | 50.0%                        |
| 17   | CCNP Security Implementing Cisco Threat Control Solutions Exam | questionbank_18.txt    | 23                   | 38                 | 60.52 %                      |
|      |                                                              |                        |                      |                    |                              |



------

> last edit by LiuYuancheng (liu_yuan_cheng@hotmail.com) by 15/08/2023 if you have any problem, please send me a message. 