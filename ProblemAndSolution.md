# **Problem and Solution**

**In this document we will share the valuable problems and the solution we meet during the project development as a reference menu for the new programmer who may take over this project for further development. Later we will sort the problem based on the problem <type>.**

[TOC]

- [**Problem and Solution**](#--problem-and-solution--)
        * [Problem [0]: Execution Exception: OpenAI API timeout](#problem--0---execution-exception--openai-api-timeout)

**Format:** 

**Problem**: ( Situation description )

**OS Platform** :

**Error Message**:

**Type**: Setup exception

**Solution**:

**Related Reference**:

------

##### Problem [0]: Execution Exception: OpenAI API timeout

**OS Platform** : Windows / Linus 

**Error Message**:

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

**Type**: Setup exception

**Solution**: This is normal, you need to update you OpenAI account to a payment account as the free API can only handle 4 questions per mins.

**Related Reference**:



------

> last edit by LiuYuancheng (liu_yuan_cheng@hotmail.com) by 27/04/2024 if you have any problem, please send me a message. 

