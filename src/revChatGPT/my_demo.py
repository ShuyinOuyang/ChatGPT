import re
import os
import json
import math
import nltk
from nltk.corpus import stopwords
from V1 import Chatbot
import subprocess

def demo():
    email = 'shuyinouyang.jp@gmail.com'
    password = 'wanamaker670'
    prompt = "Solve this coding problem with Python3\n"
    path = '../../../problem_descriptions/'
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_list = os.listdir('./log')
            if filename in file_list:
                continue
            print(filename, flush=True)
            try:
                chatbot = Chatbot(config={
                    "email": email,
                    "password": password
                })
                with open(path + filename, 'r', encoding='utf-8') as f:
                    description = f.read()
                    for data in chatbot.ask(
                            prompt + description
                    ):
                        response = data["message"]
                    code_template = re.compile('```.*\n([\s\S]+?)\n```', re.M)
                    code = code_template.findall(response)
                    if len(code)>0:
                        with open('./log/%s' % (filename), 'w') as f:
                            f.write(code[0])
            except Exception as e:
                print(filename, e)
                pass

def use_chatGPT(email, password):
    chatbot = Chatbot(config={
        "email": email,
        "password": password,
        "paid": True
    })
    return chatbot

def chatGPT_code(email, password, description):
    chatbot = use_chatGPT(email, password)
    prompt = 'Generate Python3 solution only:\n'
    for data in chatbot.ask(
            prompt + description
    ):
        response = data["message"]
    code_template = re.compile('```.*\n([\s\S]+?)\n```', re.M)
    code = code_template.findall(response)
    if len(code) > 0:
        return code[0]
    return ''

def chatGPT_code_2(chatbot, description):
    prompt = 'Generate Python3 solution only:\n'
    for data in chatbot.ask(
            prompt + description
    ):
        response = data["message"]
    code_template = re.compile('```.*\n([\s\S]+?)\n```', re.M)
    code = code_template.findall(response)
    if len(code) > 0:
        return code[0]
    return ''

def chatGPT_code_diff(chatbot, description):
    prompt = 'Generate different Python3 solution only:\n'
    for data in chatbot.ask(
            prompt + description
    ):
        response = data["message"]
    code_template = re.compile('```.*\n([\s\S]+?)\n```', re.M)
    code = code_template.findall(response)
    if len(code) > 0:
        return code[0]
    return ''

def chatGPT_rephrase(email, password, description):
    chatbot = use_chatGPT(email, password)
    prompt = 'Rephrase the following description, and make it better to generate AC code:\n'
    for data in chatbot.ask(
            prompt + description
    ):
        response = data["message"]
    return response

def chatGPT_rephrase_2(chatbot, description):
    prompt = 'Rephrase the following description, and make it better to generate AC code:\n'
    for data in chatbot.ask(
            prompt + description
    ):
        response = data["message"]
    return response

def solution_evaluation(solution, test_cases):
    with open('demo.py', 'w') as f:
        f.write(solution)
    pass_num = 0
    for test_case in test_cases:
        output = subprocess.run(["python", "demo.py"], capture_output=True, text=True, input=test_case['input'], timeout=11)
        if test_case['output'].strip() == output.stdout.strip():
            pass_num += 1
    print('%s/%s pass.' % (pass_num, len(test_cases)), flush=True)
    return (pass_num, len(test_cases))

def summerization_extractive(description, percentage):
    word2count = {}

    if '\ninput' in description.lower():
        index = description.lower().index('\ninput')
    else:
        index = -1
    problem_description = description[:index]
    problem_else = description[index + 1:]
    word_list = nltk.word_tokenize(problem_description)
    stopword_list = stopwords.words('english')
    for i in word_list:
        if i not in stopword_list:
            if i not in word2count:
                word2count[i] = 1
            else:
                word2count[i] += 1
    for key in word2count.keys():
        word2count[key] = word2count[key] / max(word2count.values())
    # print(word2count)
    # calculate the score of the sentence
    sent2score = {}
    sentence_list = nltk.sent_tokenize(problem_description)
    for sentence in sentence_list:
        for word in nltk.word_tokenize(sentence):
            if word not in stopword_list:
                if sentence not in sent2score.keys():
                    sent2score[sentence] = word2count[word]
                else:
                    sent2score[sentence] += word2count[word]

    # sort the sentence by score
    # keep the original order of the sentence
    sorted_dic = sorted([(k, v) for k, v in sent2score.items()], reverse=True, key=lambda x: x[1])[:math.ceil(len(sentence_list)*percentage)]
    sorted_dic = [i[0] for i in sorted_dic]
    # print(sorted_dic)
    final_result = []
    for sentence in sentence_list:
        if sentence in sorted_dic:
            final_result.append(sentence)
    return ' '.join(i for i in final_result) + "/n" + problem_else

def randomness_test():
    email = 'shuyinouyang.jp@gmail.com'
    password = 'wanamaker670'
    with open('../../../alpha_code/dataset/code_contests_test.json', 'r') as f:
        problem_list = json.load(f)
        for problem in problem_list:
            description = problem['description']
            description_extractive = summerization_extractive(description, 0.8)
            test_set = problem['public_tests'] + problem['private_tests'] + problem['generated_tests']
            code = chatGPT_code(email, password, description_extractive)
            if code == '':
                print('code empty')
            res_0 = solution_evaluation(code, test_set)
            return code, res_0

def experiment_1():
    # top5 code
    # chatgpt rephrase V.S. original
    email = 'shuyinouyang.jp@gmail.com'
    password = 'wanamaker670'
    with open('./log/experiment1.log', 'w') as f:
        f.write('')
    with open('./tmp2/code_contests_test.json', 'r') as f:
        problem_list = json.load(f)
    for problem in problem_list:
        print('----------------------problem name: %s--------------------------------' % (problem['name']), flush=True)
        description = problem['description']
        test_set = problem['public_tests'] + problem['private_tests'] + problem['generated_tests']

        print('rephrasing description', flush=True)
        try:
            description_rephrase = chatGPT_rephrase(email, password, problem['description'])
        except Exception as e:
            print(e, flush=True)
            continue

        print('generating code for original description', flush=True)
        count = 0
        while True:
            if count>=5:
                break
            try:
                code = chatGPT_code(email, password, description)
                res_0 = solution_evaluation(code, test_set)
            except Exception as e:
                print(e, flush=True)
                continue
            res = {
                'name': problem['name'],
                'description': description,
                'code': code,
                'test_case_solved': res_0,
            }
            json_str = json.dumps(res)
            with open('./log/experiment1.log', 'a') as f:
                f.write(json_str+'\n')
            count += 1


        print('generating code for rephrased description', flush=True)
        count = 0
        while True:
            if count >= 5:
                break
            try:
                code_rephrase = chatGPT_code(email, password, description_rephrase)
                res_1 = solution_evaluation(code_rephrase, test_set)
            except Exception as e:
                print(e, flush=True)
                continue
            res = {
                'name': problem['name'],
                'rephrased_description': description_rephrase,
                'rephrased_code': code_rephrase,
                'test_case_solved': res_1,
            }
            json_str = json.dumps(res)
            with open('./log/experiment1.log', 'a') as f:
                f.write(json_str + '\n')
            count += 1

def experiment_2():
    # top5 code
    # each question one window
    email = 'shuyinouyang.jp@gmail.com'
    password = 'wanamaker670'
    # initialize the log
    # with open('./log/experiment_2.log', 'w') as f:
    #     f.write('')
    # start from last part
    names = set()
    with open('./log/experiment_2.log', 'r') as f:
        for line in f:
            content = json.loads(line)
            names.add(content['name'])
    # with open('../../../alpha_code/dataset/code_contests_test.json', 'r') as f:
    with open('./tmp2/code_contests_test.json', 'r') as f:
        problem_list = json.load(f)
    for problem in problem_list:
        if problem['name'] in names:
            continue
        print('----------------------problem name: %s--------------------------------' % (problem['name']), flush=True)
        description = problem['description']
        test_set = problem['public_tests'] + problem['private_tests'] + problem['generated_tests']
        print('Initializing chatbot')
        chatbot = use_chatGPT(email, password)
        print('generating code for original description', flush=True)
        count = 0
        while True:
            if count >= 1:
                break
            try:
                code = chatGPT_code_2(chatbot, description)
                res_0 = solution_evaluation(code, test_set)
                count += 1
            except Exception as e:
                print(e, flush=True)
                continue
        res = {
            'name': problem['name'],
            'description': description,
            'code': code,
            'test_case_solved': res_0,
        }
        json_str = json.dumps(res)
        with open('./log/experiment_2.log', 'a') as f:
            f.write(json_str + '\n')

        print('generating code for rephrased description', flush=True)
        count = 0
        while True:
            if count >= 1:
                break
            try:
                description_rephrase = chatGPT_rephrase_2(chatbot, problem['description'])
            except Exception as e:
                print(e, flush=True)
                continue
            try:
                code_rephrase = chatGPT_code_2(chatbot, description_rephrase)
                res_1 = solution_evaluation(code_rephrase, test_set)
                count += 1
            except Exception as e:
                print(e, flush=True)
                continue
        res = {
            'name': problem['name'],
            'rephrased_description': description_rephrase,
            'rephrased_code': code_rephrase,
            'test_case_solved': res_1,
        }
        json_str = json.dumps(res)
        with open('./log/experiment_2.log', 'a') as f:
            f.write(json_str + '\n')


def experiment_3():
    # top5 code
    # same window
    # each question one window
    email = 'shuyinouyang.jp@gmail.com'
    password = 'wanamaker670'
    # initialize the log
    # with open('./log/experiment_3.log', 'w') as f:
    #     f.write('')
    # start from last part
    names = set()
    with open('./log/experiment_3.log', 'r') as f:
        for line in f:
            content = json.loads(line)
            names.add(content['name'])
    # with open('../../../alpha_code/dataset/code_contests_test.json', 'r') as f:
    with open('./tmp2/code_contests_test.json', 'r') as f:
        problem_list = json.load(f)
    for problem in problem_list:
        if problem['name'] in names:
            continue
        print('----------------------problem name: %s--------------------------------' % (problem['name']), flush=True)
        description = problem['description']
        test_set = problem['public_tests'] + problem['private_tests'] + problem['generated_tests']
        print('Initializing chatbot')
        chatbot = use_chatGPT(email, password)
        print('generating code for original description', flush=True)
        res_list_0 = []
        while True:
            if len(res_list_0) >= 5:
                break
            if len(res_list_0) == 0:
                try:
                    code = chatGPT_code_2(chatbot, description)
                    res_0 = solution_evaluation(code, test_set)
                except Exception as e:
                    print(e, flush=True)
                    continue
            else:
                try:
                    code = chatGPT_code_diff(chatbot, description)
                    res_0 = solution_evaluation(code, test_set)
                except Exception as e:
                    print(e, flush=True)
                    continue
            res = {
                'name': problem['name'],
                'description': description,
                'code': code,
                'test_case_solved': res_0,
            }
            res_list_0.append(res)

        print('generating code for rephrased description', flush=True)
        res_list_1 = []
        description_rephrase = ''
        while description_rephrase == '':
            try:
                description_rephrase = chatGPT_rephrase_2(chatbot, problem['description'])
            except Exception as e:
                print(e, flush=True)
                continue
        while True:
            if len(res_list_1) >= 5:
                break
            if len(res_list_1) == 0:
                try:
                    code_rephrase = chatGPT_code_2(chatbot, description_rephrase)
                    res_1 = solution_evaluation(code_rephrase, test_set)
                except Exception as e:
                    print(e, flush=True)
                    continue
            else:
                try:
                    code_rephrase = chatGPT_code_diff(chatbot, description_rephrase)
                    res_1 = solution_evaluation(code_rephrase, test_set)

                except Exception as e:
                    print(e, flush=True)
                    continue
            res = {
                'name': problem['name'],
                'rephrased_description': description_rephrase,
                'rephrased_code': code_rephrase,
                'test_case_solved': res_1,
            }
            res_list_1.append(res)
        for res in res_list_0:
            json_str = json.dumps(res)
            with open('./log/experiment_3.log', 'a') as f:
                f.write(json_str + '\n')
        for res in res_list_1:
            json_str = json.dumps(res)
            with open('./log/experiment_3.log', 'a') as f:
                f.write(json_str + '\n')

if __name__ == "__main__":
    experiment_3()
    # res_list = []
    # for _ in range(5):
    #     code, res_0 = randomness_test()
    #     res_list.append([code, res_0])

